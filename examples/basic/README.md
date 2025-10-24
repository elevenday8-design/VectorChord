# Basic VectorChord walkthrough

This example demonstrates the minimal steps required to use VectorChord in PostgreSQL:

1. Enable the `vchord` extension.
2. Create a table containing a `vector` column.
3. Insert a few sample embeddings.
4. Build a `vchordrq` index for efficient nearest-neighbor lookups.
5. Run a similarity search using the `<->` operator.

Run the script with:

```bash
psql -f examples/basic/basic_usage.sql
```

You should see three nearest neighbors printed with their distances.
