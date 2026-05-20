import csv
import polars as pl
from pathlib import Path
from src.config import RAW_DIR, FIXED_DIR, CSV_SCHEMA


def fix_encoding(force: bool = False) -> None:
    # Los CSV del DEIS vienen en latin-1. Se reescriben en UTF-8 reparando
    # líneas mal formadas con el módulo csv estándar de Python.
    FIXED_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"no hay CSV en {RAW_DIR}")

    for src in files:
        dst = FIXED_DIR / src.name
        if not force and dst.exists():
            print(f"  [skip] {src.name}")
            continue
        print(f"  {src.name}")
        with (
            open(src, "r", encoding="iso-8859-1") as fin,
            open(dst, "w", encoding="utf-8", newline="") as fout,
        ):
            reader = csv.reader(fin, delimiter=";", quotechar='"')
            writer = csv.writer(fout, delimiter=";", quotechar='"',
                                quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                writer.writerow(row)


def scan(fixed_dir: Path = FIXED_DIR) -> pl.LazyFrame:
    # 2019-2022 tienen 15 columnas, 2023+ tienen 21.
    # diagonal_concat rellena con null las columnas ausentes en los años anteriores.
    files = sorted(fixed_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"no hay CSV en {fixed_dir} — ejecuta fix_encoding primero")

    return pl.concat(
        [
            pl.scan_csv(
                f,
                separator=";",
                encoding="utf8",
                schema_overrides=CSV_SCHEMA,
                infer_schema_length=10_000,
                truncate_ragged_lines=False,
            )
            for f in files
        ],
        how="diagonal",
        rechunk=False,
    )