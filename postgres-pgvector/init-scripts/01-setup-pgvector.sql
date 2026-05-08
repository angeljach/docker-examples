-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create a sample embeddings table
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create an index for faster similarity searches
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE documents TO postgres;
GRANT ALL PRIVILEGES ON SEQUENCE documents_id_seq TO postgres;

-- Optional: Create a function for similarity search
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding vector,
    similarity_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id int,
    content text,
    similarity float
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        (documents.embedding <=> query_embedding)::float as similarity
    FROM documents
    WHERE (documents.embedding <=> query_embedding) < (1 - similarity_threshold)
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;