import polars as pl


def info(df: pl.DataFrame) -> pl.DataFrame:
    pl.Config.set_tbl_rows(-1)
    return pl.DataFrame({
        "col":    df.columns,
        "type":   [str(t) for t in df.dtypes],
        "nulls":  [df[c].null_count() for c in df.columns],
        "unique": [df[c].n_unique()   for c in df.columns],
    })


def info_lazy(lf: pl.LazyFrame) -> pl.DataFrame:
    schema = lf.collect_schema()
    cols   = schema.names()
    exprs  = [e for c in cols for e in (
        pl.col(c).null_count().alias(f"{c}__n"),
        pl.col(c).n_unique().alias(f"{c}__u"),
    )]
    m = lf.select(exprs).collect()
    pl.Config.set_tbl_rows(-1)
    return pl.DataFrame({
        "col":    cols,
        "type":   [str(t) for t in schema.dtypes()],
        "nulls":  [m[f"{c}__n"][0] for c in cols],
        "unique": [m[f"{c}__u"][0] for c in cols],
    })


def schema(lf: pl.LazyFrame) -> pl.DataFrame:
    s = lf.collect_schema()
    return pl.DataFrame({"col": s.names(), "type": [str(t) for t in s.dtypes()]})