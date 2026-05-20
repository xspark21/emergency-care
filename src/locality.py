import polars as pl
from src.config import GEO_COLS


def fill_geo(
    lf: pl.LazyFrame,
    from_csv: pl.DataFrame,
    from_deis: pl.DataFrame,
    from_no_register: pl.DataFrame,
) -> pl.LazyFrame:
    # Cascada de fuentes por orden de confianza:
    #   1. valor propio de la fila (CSV 2023+)
    #   2. from_csv    — último valor conocido por establecimiento en los propios CSV
    #   3. from_deis   — Excel DEIS (activos y cerrados, 2025 y 2026)
    #   4. from_no_register — tabla verificada para establecimientos sin cobertura en ninguna fuente
    s = {"csv": "_csv", "deis": "_deis", "no_register": "_no_register"}

    geo_csv     = from_csv.rename({c: f"{c}{s['csv']}"     for c in GEO_COLS})
    geo_deis    = from_deis.rename({c: f"{c}{s['deis']}"   for c in GEO_COLS})
    geo_no_register = from_no_register.rename({c: f"{c}{s['no_register']}" for c in GEO_COLS})

    return (
        lf
        .join(geo_csv.lazy(),     on="IdEstablecimiento", how="left")
        .join(geo_deis.lazy(),    on="IdEstablecimiento", how="left")
        .join(geo_no_register.lazy(), on="IdEstablecimiento", how="left")
        .with_columns([
            pl.col(c)
              .fill_null(pl.col(f"{c}{s['csv']}"))
              .fill_null(pl.col(f"{c}{s['deis']}"))
              .fill_null(pl.col(f"{c}{s['no_register']}"))
              .alias(c)
            for c in GEO_COLS
        ])
        .drop([f"{c}{sfx}" for c in GEO_COLS for sfx in s.values()])
    )


def geo_report(lf: pl.LazyFrame) -> None:
    total = lf.select(pl.len()).collect().item()
    nulls = lf.filter(pl.col("CodigoRegion").is_null()).select(pl.len()).collect().item()
    ids   = (
        lf.filter(pl.col("CodigoRegion").is_null())
        .select(pl.col("IdEstablecimiento").n_unique())
        .collect().item()
    )
    print(f"  registros       : {total:>12,}")
    print(f"  sin CodigoRegion: {nulls:>12,}  ({nulls/total*100:.2f}%)")
    print(f"  establecimientos: {ids}")