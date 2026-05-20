import polars as pl
from src.config import CAT_GEO, CAT_NOMBRES, GEO_COLS


def geo_from_csv(lf: pl.LazyFrame) -> pl.DataFrame:
    # Toma la geografía más reciente por establecimiento desde los propios CSV.
    # Solo existen valores desde 2023 — sirven para rellenar 2019-2022.
    return (
        lf.select(["IdEstablecimiento", "fecha"] + GEO_COLS)
        .filter(pl.col("CodigoRegion").is_not_null())
        .sort("fecha")
        .group_by("IdEstablecimiento")
        .agg([pl.col(c).last() for c in GEO_COLS])
        .collect()
    )


def nombres_from_csv(lf: pl.LazyFrame) -> pl.DataFrame:
    return (
        lf.select(["IdEstablecimiento", "NEstablecimiento", "fecha"])
        .filter(pl.col("NEstablecimiento").is_not_null())
        .sort("fecha")
        .group_by("IdEstablecimiento")
        .agg(pl.col("NEstablecimiento").last())
        .collect()
    )


def nombres_from_deis(df_est: pl.DataFrame) -> pl.DataFrame:
    return (
        df_est
        .select(["id_antiguo", "NEstablecimiento"])
        .rename({"id_antiguo": "IdEstablecimiento"})
        .filter(pl.col("NEstablecimiento").is_not_null())
        .unique(subset=["IdEstablecimiento"])
    )


def save(cat_geo: pl.DataFrame, cat_nombres: pl.DataFrame) -> None:
    CAT_GEO.parent.mkdir(parents=True, exist_ok=True)
    cat_geo.write_parquet(CAT_GEO)
    cat_nombres.write_parquet(CAT_NOMBRES)
    print(f"  geo:     {cat_geo.shape[0]} establecimientos")
    print(f"  nombres: {cat_nombres.shape[0]} establecimientos")