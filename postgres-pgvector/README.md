# PostgreSQL with pgvector on macOS using Docker Compose

This setup provides a fully functional PostgreSQL database with pgvector extension enabled, perfect for vector similarity searches and embeddings.

## Prerequisites

- **Docker Desktop for Mac** (with Apple Silicon or Intel support)
- **Docker Compose** (included with Docker Desktop)
- **Python 3.8+** (optional, for the test client)

## Quick Start

### 1. Create the project directory structure

```bash
mkdir -p postgres-pgvector/{init-scripts}
cd postgres-pgvector
```

### 2. Add the files

Copy these files into your project directory:
- `docker compose.yml` - Main Docker Compose configuration
- `init-scripts/01-setup-pgvector.sql` - SQL initialization script
- `test_pgvector.py` - Python test client (optional)

### 3. Start the database

```bash
make up
```

This will:
- Pull the pgvector Docker image
- Create and start the PostgreSQL container
- Initialize pgvector extension
- Create sample tables and functions
- Run health checks

### 4. Verify the setup

```bash
# Check container status
make ps

# View logs
make logs

# Connect via psql (if you have it installed)
psql -h localhost -U postgres -d vectordb
# Password: postgres

# Or better, connect with make
make shell
```

## Testing with Python

### Install dependencies

```bash
pip install psycopg2-binary numpy
```

### Run the test script

```bash
python test_pgvector.py
```

This will:
- Connect to the database
- Verify pgvector is installed
- Insert sample documents with embeddings
- Perform similarity searches
- Display results

## Using the Database

### Connect from your application

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="vectordb",
    user="postgres",
    password="postgres"
)
cursor = conn.cursor()
```

### Insert a document with embedding

```python
import json

embedding = [0.1, 0.2, 0.3, ...]  # Your 1536-dim embedding
content = "Your document text here"
metadata = {"source": "api", "category": "blog"}

cursor.execute(
    """
    INSERT INTO documents (content, embedding, metadata)
    VALUES (%s, %s, %s)
    """,
    (content, embedding, json.dumps(metadata))
)
conn.commit()
```

### Search by vector similarity

```sql
-- Using cosine distance (most common)
SELECT id, content, (embedding <=> %s) as distance
FROM documents
WHERE (embedding <=> %s) < 0.3
ORDER BY embedding <=> %s
LIMIT 10;

-- Or use the built-in search function
SELECT * FROM search_documents(%s, 0.7, 10);
```

### Using pgvector operators

- `<=>` - Cosine distance (recommended for normalized vectors)
- `<->` - Euclidean distance
- `<#>` - Negative inner product distance
- `<+>` - Taxicab distance

## Configuration

### Modify database credentials

Edit `docker compose.yml`:

```yaml
environment:
  POSTGRES_USER: your_user
  POSTGRES_PASSWORD: your_password
  POSTGRES_DB: your_dbname
```

### Change vector dimensions

Edit `init-scripts/01-setup-pgvector.sql`:

```sql
embedding vector(3072)  -- Change from 1536 to your dimension
```

### Adjust IVF index parameters

```sql
-- Increase lists for larger datasets (rule of thumb: lists = rows / 1000)
CREATE INDEX documents_embedding_idx 
ON documents 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 500);  -- Changed from 100
```

## Common Tasks

### View all documents

```bash
make shell
```

Then run:
```sql
SELECT id, content, created_at FROM documents LIMIT 10;
```

### Delete all documents

```bash
make db-clear
```

### Backup the database

```bash
make backup
```

### Restore from backup

```bash
make restore
```

### Access PostgreSQL shell directly

```bash
make shell
```

Inside the shell:
```sql
-- List tables
\dt

-- Describe documents table
\d documents

-- Check pgvector functions
\df search_documents

-- Exit
\q
```

## Stopping and Cleaning Up

### Stop the container (keeps data)

```bash
make down
```

### Stop and remove everything (including data)

```bash
make clean
```

### View data volume

```bash
docker volume ls | grep postgres
```

## Performance Tips

1. **Index tuning**: The IVF index with 100 lists works well for up to ~100k documents. Increase lists for larger datasets.

2. **Batch inserts**: Use `execute_values()` for inserting multiple rows:

```python
from psycopg2.extras import execute_values

rows = [(content1, embedding1), (content2, embedding2)]
execute_values(
    cursor,
    "INSERT INTO documents (content, embedding) VALUES %s",
    rows
)
```

3. **Connection pooling**: Use `pgbouncer` for production workloads.

4. **Vector normalization**: Always normalize your embeddings to unit length for cosine distance.

## Troubleshooting

### Container fails to start

```bash
# Check logs
make logs

# Common issue: Port 5432 already in use
# Solution: Change port in docker compose.yml or stop conflicting container
```

### Connection refused

```bash
# Wait for container to be fully ready
make ps  # Check status

# Ensure health check passes
make logs | grep healthcheck
```

### Out of memory errors

Increase Docker Desktop memory allocation:
- Docker Desktop menu → Preferences → Resources
- Set "Memory" to at least 4GB

### pgvector not found

```bash
# Verify extension in container
make shell
```

Then run:
```sql
SELECT * FROM pg_extension;
```

# Reinstall if needed
```bash
make clean
make up
```

## Next Steps

1. **Integration**: Integrate with your AI framework (LangChain, LlamaIndex, etc.)
2. **Scaling**: Add PgBouncer for connection pooling
3. **Monitoring**: Set up Prometheus/Grafana for database metrics
4. **Backup strategy**: Implement automated backups to S3 or cloud storage

## Resources

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [psycopg2 Documentation](https://www.psycopg.org/)

---

**Happy vector searching! 🚀**