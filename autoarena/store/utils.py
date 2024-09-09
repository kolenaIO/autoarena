def id_slug(a: int, b: int) -> str:
    return f"{int(min(a, b))}-{int(max(a, b))}"  # matches duckdb implementation in schema.sql
