import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import polars as pl
from src.config  import MASTER_PARQUET, EST_PARQUET
from src.no_register import geo as no_register_geo


def ok(msg: str) -> None:
    print(f"  ok  {msg}")

def warn(msg: str, n: int) -> None:
    print(f"  !!  {msg:<45} {n:>12,}")

def fail(msg: str, n: int) -> None:
    print(f"  !!  {msg:<45} {n:>12,}  [critico]")


def main() -> None:
    if not MASTER_PARQUET.exists():
        print(f"no existe {MASTER_PARQUET} — ejecuta build.py primero")
        sys.exit(1)

    df    = pl.scan_parquet(MASTER_PARQUET)
    total = df.select(pl.len()).collect().item()
    print(f"\n:: {MASTER_PARQUET}  ({total:,} registros)")

    errores = 0

    # — nulos críticos
    print("\n:: nulos")
    for col in ["IdEstablecimiento", "fecha", "IdCausa", "GlosaCausa",
                "Total", "CodigoRegion", "NombreRegion", "CodigoComuna"]:
        n = df.filter(pl.col(col).is_null()).select(pl.len()).collect().item()
        if n == 0:
            ok(col)
        else:
            fail(col, n)
            errores += 1

    # — rangos
    print("\n:: rangos")
    n = df.filter(pl.col("Total") < 0).select(pl.len()).collect().item()
    if n == 0: ok("Total >= 0")
    else: fail("Total >= 0", n); errores += 1

    n = df.filter((pl.col("semana") < 1) | (pl.col("semana") > 53)).select(pl.len()).collect().item()
    if n == 0: ok("semana 1-53")
    else: fail("semana 1-53", n); errores += 1

    n = df.filter(
        pl.col("CodigoRegion").is_not_null() &
        ((pl.col("CodigoRegion") < 1) | (pl.col("CodigoRegion") > 16))
    ).select(pl.len()).collect().item()
    if n == 0: ok("CodigoRegion 1-16")
    else: fail("CodigoRegion 1-16", n); errores += 1

    año_min = df.select(pl.col("fecha").dt.year().min()).collect().item()
    año_max = df.select(pl.col("fecha").dt.year().max()).collect().item()
    n = df.filter(
        (pl.col("fecha").dt.year() < año_min) | (pl.col("fecha").dt.year() > año_max)
    ).select(pl.len()).collect().item()
    if n == 0: ok(f"fecha {año_min}-{año_max}")
    else: fail(f"fecha {año_min}-{año_max}", n); errores += 1

    # — consistencia
    print("\n:: consistencia")
    n = df.filter(
        pl.col("Total") < sum(
            pl.col(c).fill_null(0)
            for c in ["Menores_1", "De_1_a_4", "De_5_a_14", "De_15_a_64", "De_65_y_mas"]
        )
    ).select(pl.len()).collect().item()
    if n == 0: ok("Total >= suma grupos etarios")
    else: warn("Total >= suma grupos etarios", n)

    # Establecimientos sin fila en establecimientos.parquet.
    # Se excluyen los de no_register.py que tienen cobertura geográfica verificada
    # pero no están en el Excel DEIS.
    if EST_PARQUET.exists():
        est = pl.read_parquet(EST_PARQUET)
        ids_ref = (
            set(est["id_antiguo"].drop_nulls().to_list()) |
            set(est["id_vigente"].drop_nulls().to_list()) |
            set(no_register_geo()["IdEstablecimiento"].to_list())
        )
        ids_maestra = (
            df.select("IdEstablecimiento").unique().collect()["IdEstablecimiento"].to_list()
        )
        sin_ref = [i for i in ids_maestra if i not in ids_ref]
        if not sin_ref:
            ok("todos los establecimientos tienen referencia")
        else:
            warn("sin referencia en DEIS ni no_register", len(sin_ref))
            if len(sin_ref) <= 20:
                print(f"      {sin_ref}")
    else:
        print("  --  establecimientos.parquet no encontrado")

    # — cobertura temporal
    print("\n:: cobertura")
    pl.Config.set_tbl_rows(-1)
    print(
        df.with_columns(pl.col("fecha").dt.year().alias("año"))
        .group_by("año")
        .agg([
            pl.len().alias("registros"),
            pl.col("IdEstablecimiento").n_unique().alias("establecimientos"),
            pl.col("CodigoRegion").null_count().alias("sin_region"),
        ])
        .sort("año")
        .collect()
    )

    print()
    if errores == 0:
        print(":: ok\n")
    else:
        print(f":: {errores} checks criticos fallaron\n")
        sys.exit(1)


if __name__ == "__main__":
    main()