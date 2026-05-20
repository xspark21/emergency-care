import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import polars as pl

from src.config   import FIXED_DIR, FINAL_DIR, MASTER_PARQUET
from src.io       import fix_encoding, scan
from src.clean    import clean
from src.catalog  import geo_from_csv, nombres_from_csv, nombres_from_deis, save
from src.deis     import load_establecimientos, geo_from_deis
from src.locality import fill_geo, geo_report
from src.no_register  import geo as no_register_geo, nombres as no_register_nombres


def main() -> None:
    print("\n:: encoding")
    fix_encoding()

    print("\n:: carga")
    lf = scan(FIXED_DIR)
    print(f"  {len(lf.collect_schema().names())} columnas")

    print("\n:: limpieza")
    lf = clean(lf)

    print("\n:: fechas")
    lf = lf.with_columns(
        pl.col("fecha").str.to_date(format="%d/%m/%Y", strict=False)
    )

    print("\n:: catalogos csv")
    cat_geo     = geo_from_csv(lf)
    cat_nombres = nombres_from_csv(lf)
    save(cat_geo, cat_nombres)

    print("\n:: catalogos deis")
    df_est   = load_establecimientos()
    geo_deis = geo_from_deis(df_est)

    print("\n:: recuperacion geografica")
    lf = fill_geo(lf, cat_geo, geo_deis, no_register_geo())

    # Enriquece NEstablecimiento con nombres del Excel DEIS y tabla de verificados.
    # Los CSV 2019-2022 no incluían NEstablecimiento para todos los registros.
    cat_nombres_ext = pl.concat(
        [nombres_from_deis(df_est), no_register_nombres()],
        how="diagonal",
    ).unique(subset=["IdEstablecimiento"], keep="first")

    lf = (
        lf
        .join(
            cat_nombres_ext.rename({"NEstablecimiento": "_nombre_ext"}).lazy(),
            on="IdEstablecimiento", how="left",
        )
        .with_columns(
            pl.col("NEstablecimiento").fill_null(pl.col("_nombre_ext"))
        )
        .drop("_nombre_ext")
    )

    print("\n:: exportando")
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    lf.sink_parquet(MASTER_PARQUET)
    print(f"  -> {MASTER_PARQUET}")

    print("\n:: nulos residuales")
    geo_report(pl.scan_parquet(MASTER_PARQUET))

    print("\n:: pipeline completado\n")


if __name__ == "__main__":
    main()