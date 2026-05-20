import polars as pl

_RULES = {
    "strip": lambda col: pl.col(col).str.strip_chars(),
    "title": lambda col: pl.col(col).str.to_titlecase(),
    "upper": lambda col: pl.col(col).str.to_uppercase(),
    "lower": lambda col: pl.col(col).str.to_lowercase(),
}

_COLS = {
    "IdEstablecimiento":        ["strip"],
    "NEstablecimiento":         ["strip"],
    "NombreRegion":             ["strip", "title"],
    "NombreComuna":             ["strip", "title"],
    "NombreDependencia":        ["strip", "title"],
    "GLOSATIPOESTABLECIMIENTO": ["strip", "title"],
    "GLOSATIPOATENCION":        ["strip", "title"],
    "GlosaTipoCampana":         ["strip", "title"],
    "GlosaCausa":               ["strip"],
}


def clean(lf: pl.LazyFrame) -> pl.LazyFrame:
    present = set(lf.collect_schema().names())
    for col, rules in _COLS.items():
        if col not in present:
            continue
        for rule in rules:
            lf = lf.with_columns(_RULES[rule](col).alias(col))
    return lf