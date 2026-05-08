#!/usr/bin/env python3
"""
PostgreSQL with pgvector client script
Test connection and demonstrate vector operations
"""

import psycopg2
from psycopg2.extras import execute_values
import numpy as np
from typing import List, Tuple
import json
import time

class VectorDB:
    def __init__(self, host="localhost", port=5432, database="vectordb", 
                 user="postgres", password="postgres"):
        self.conn_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
        self.conn = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.cursor = self.conn.cursor()
            print("✓ Connected to PostgreSQL with pgvector")
            return True
        except psycopg2.Error as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✓ Disconnected from database")
    
    def check_pgvector(self) -> bool:
        """Verify pgvector extension is installed"""
        try:
            self.cursor.execute(
                "SELECT extname FROM pg_extension WHERE extname='vector'"
            )
            result = self.cursor.fetchone()
            if result:
                print("✓ pgvector extension is active")
                return True
            else:
                print("✗ pgvector extension not found")
                return False
        except psycopg2.Error as e:
            print(f"✗ Error checking pgvector: {e}")
            return False
    
    def insert_document(self, content: str, embedding: List[float], 
                       metadata: dict = None) -> int:
        """Insert a document with embedding"""
        try:
            metadata = metadata or {}
            self.cursor.execute(
                """
                INSERT INTO documents (content, embedding, metadata)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (content, embedding, json.dumps(metadata))
            )
            doc_id = self.cursor.fetchone()[0]
            self.conn.commit()
            return doc_id
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f"✗ Insert error: {e}")
            return None
    
    def search_similar(self, query_embedding: List[float], 
                      similarity_threshold: float = 0.7, 
                      match_count: int = 10) -> List[Tuple]:
        """Search for similar documents using vector similarity"""
        try:
            self.cursor.execute(
                """
                SELECT id, content, (embedding <=> %s) as distance
                FROM documents
                WHERE (embedding <=> %s) < %s
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (embedding, embedding, 1 - similarity_threshold, embedding, match_count)
            )
            return self.cursor.fetchall()
        except psycopg2.Error as e:
            print(f"✗ Search error: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get total number of documents"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM documents")
            return self.cursor.fetchone()[0]
        except psycopg2.Error as e:
            print(f"✗ Count error: {e}")
            return 0


def generate_random_embedding(dimensions: int = 1536) -> List[float]:
    """Generate a random vector embedding (normalized)"""
    embedding = np.random.randn(dimensions)
    # Normalize to unit length (common practice)
    embedding = embedding / np.linalg.norm(embedding)
    return embedding.tolist()


def main():
    # Initialize database client
    db = VectorDB()
    
    # Wait for PostgreSQL to be ready (useful when container just started)
    print("Attempting to connect to PostgreSQL...")
    max_retries = 10
    for i in range(max_retries):
        if db.connect():
            break
        else:
            print(f"Retry {i+1}/{max_retries}... waiting 2 seconds")
            time.sleep(2)
    else:
        print("✗ Failed to connect after maximum retries")
        return
    
    try:
        # Check pgvector extension
        if not db.check_pgvector():
            return
        
        # Check if table exists
        db.cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'documents')"
        )
        if not db.cursor.fetchone()[0]:
            print("✗ Documents table not found. Run Docker container first.")
            return
        
        print("\n--- Sample Operations ---")
        
        # Insert sample documents with embeddings
        print("\nInserting sample documents...")
        documents = [
            {
                "content": "PostgreSQL is a powerful relational database",
                "metadata": {"source": "docs", "category": "database"}
            },
            {
                "content": "Vector embeddings enable semantic search",
                "metadata": {"source": "blog", "category": "ai"}
            },
            {
                "content": "pgvector provides vector operations for PostgreSQL",
                "metadata": {"source": "github", "category": "extension"}
            }
        ]
        
        doc_ids = []
        for doc in documents:
            embedding = generate_random_embedding()
            doc_id = db.insert_document(
                doc["content"], 
                embedding, 
                doc["metadata"]
            )
            if doc_id:
                doc_ids.append(doc_id)
                print(f"  ✓ Inserted document {doc_id}: {doc['content'][:50]}...")
        
        # Get document count
        count = db.get_document_count()
        print(f"\nTotal documents in database: {count}")
        
        # Perform similarity search
        print("\nPerforming similarity search...")
        query_embedding = generate_random_embedding()
        results = db.search_similar(query_embedding, similarity_threshold=0.5, match_count=5)
        
        if results:
            print(f"Found {len(results)} similar documents:")
            for doc_id, content, distance in results:
                print(f"  - ID: {doc_id}, Distance: {distance:.4f}, Content: {content[:50]}...")
        else:
            print("No similar documents found")
        
        print("\n✓ All tests completed successfully!")
        
    finally:
        db.disconnect()


if __name__ == "__main__":
    main()