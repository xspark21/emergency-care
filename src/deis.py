import polars as pl
from pathlib import Path
from src.config import DEIS_2025, DEIS_2026, DEIS_COL_MAP, EST_COLS, GEO_COLS, EST_PARQUET


def _read_sheet(path: Path, sheet_index: int) -> pl.DataFrame:
    # Los Excel del DEIS tienen una fila de título mergeada antes del header real.
    df = pl.read_excel(path, sheet_id=sheet_index + 1, engine="calamine")
    headers = df.row(0)
    seen: dict[str, int] = {}
    resolved: list[str] = []
    for old, raw in zip(df.columns, headers):
        name = raw if isinstance(raw, str) and raw.strip() else old
        if name in seen:
            seen[name] += 1
            name = f"{name}_{seen[name]}"
        else:
            seen[name] = 1
        resolved.append(name)
    return df.slice(1).rename(dict(zip(df.columns, resolved)))


def _normalize(df: pl.DataFrame, activo: bool) -> pl.DataFrame:
    strip_map = {c: c.strip() for c in df.columns if c != c.strip()}
    if strip_map:
        df = df.rename(strip_map)
    df = df.rename({k: v for k, v in DEIS_COL_MAP.items() if k in df.columns})
    df = df.with_columns(pl.lit(activo).alias("activo"))
    for col in EST_COLS:
        if col not in df.columns:
            df = df.with_columns(pl.lit(None).alias(col))
    return df.select(EST_COLS)


def _cast(df: pl.DataFrame) -> pl.DataFrame:
    for col, dtype in {
        "CodigoRegion": pl.Int64, "CodigoComuna": pl.Int64,
        "CodigoDependencia": pl.Int64, "Latitud": pl.Float64, "Longitud": pl.Float64,
    }.items():
        if col in df.columns:
            df = df.with_columns(pl.col(col).cast(dtype, strict=False))
    for col in ["FechaInicio", "FechaCierre", "FechaIncorporacion"]:
        if col in df.columns and df[col].dtype == pl.String:
            df = df.with_columns(pl.col(col).str.to_date(format="%d/%m/%Y", strict=False))
    return df


def load_establecimientos() -> pl.DataFrame:
    parts: list[pl.DataFrame] = []

    if DEIS_2025.exists():
        print(f"  {DEIS_2025.name}")
        parts.append(_normalize(_read_sheet(DEIS_2025, 1), activo=True))
        parts.append(_normalize(_read_sheet(DEIS_2025, 2), activo=False))
    else:
        print(f"  [skip] {DEIS_2025.name} no encontrado")

    if DEIS_2026.exists():
        print(f"  {DEIS_2026.name}")
        parts.append(_normalize(_read_sheet(DEIS_2026, 0), activo=True))
        parts.append(_normalize(_read_sheet(DEIS_2026, 1), activo=False))
    else:
        print(f"  [skip] {DEIS_2026.name} no encontrado")

    if not parts:
        raise FileNotFoundError("no se encontró ningún Excel DEIS en data/reference/")

    df = (
        pl.concat(parts, how="diagonal")
        .pipe(_cast)
        .sort(["activo"], descending=False)
        .unique(subset=["id_antiguo"], keep="last")
    )

    EST_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(EST_PARQUET)
    print(f"  establecimientos: {df.shape[0]} registros")
    return df


def geo_from_deis(df_est: pl.DataFrame) -> pl.DataFrame:
    return (
        df_est
        .select(["id_antiguo"] + GEO_COLS)
        .rename({"id_antiguo": "IdEstablecimiento"})
        .filter(pl.col("CodigoRegion").is_not_null())
        .unique(subset=["IdEstablecimiento"])
    )