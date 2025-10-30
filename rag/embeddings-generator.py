#!/usr/bin/env python3
"""
Embeddings Generator for Aidemy Chatbot RAG System
Generates embeddings from processed documents and stores in Qdrant.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any
import time

from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from tqdm import tqdm
from dotenv import load_dotenv


class EmbeddingsGenerator:
    """Generate embeddings and store in Qdrant vector database."""

    def __init__(
        self,
        api_key: str = None,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "aidemy_knowledge",
        embedding_model: str = "openai/text-embedding-3-small"
    ):
        """
        Initialize embeddings generator.

        Args:
            api_key: OpenRouter API key (or OpenAI if using OpenAI directly)
            qdrant_host: Qdrant host
            qdrant_port: Qdrant port
            collection_name: Name of Qdrant collection
            embedding_model: Embedding model to use (OpenRouter format)
        """
        load_dotenv()

        # Use OpenRouter API (compatible with OpenAI SDK)
        self.openai_client = OpenAI(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.embedding_dimension = 1536  # text-embedding-3-small dimension
        self.processed_dir = Path("/app/processed")

    def create_collection(self):
        """Create Qdrant collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections().collections
            collection_names = [col.name for col in collections]

            if self.collection_name not in collection_names:
                print(f"Creating collection: {self.collection_name}")
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_dimension,
                        distance=Distance.COSINE
                    )
                )
                print(f"Collection '{self.collection_name}' created successfully")
            else:
                print(f"Collection '{self.collection_name}' already exists")

        except Exception as e:
            print(f"Error creating collection: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch

        Returns:
            List of embedding vectors
        """
        embeddings = []

        for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
            batch = texts[i:i + batch_size]

            try:
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                batch_embeddings = [data.embedding for data in response.data]
                embeddings.extend(batch_embeddings)

                # Rate limiting
                time.sleep(0.1)

            except Exception as e:
                print(f"Error in batch {i // batch_size}: {e}")
                # Retry individual items in batch
                for text in batch:
                    try:
                        embedding = self.generate_embedding(text)
                        embeddings.append(embedding)
                    except Exception as e2:
                        print(f"Failed to generate embedding: {e2}")
                        # Use zero vector as placeholder
                        embeddings.append([0.0] * self.embedding_dimension)

        return embeddings

    def store_embeddings_in_qdrant(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ):
        """
        Store embeddings and metadata in Qdrant.

        Args:
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        points = []

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = PointStruct(
                id=idx,
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "source_file": chunk["metadata"]["source_file"],
                    "source_type": chunk["metadata"]["source_type"],
                    "chunk_index": chunk["metadata"]["chunk_index"],
                    "token_count": chunk["metadata"]["token_count"],
                    "processed_at": chunk["metadata"]["processed_at"]
                }
            )
            points.append(point)

        # Upload in batches
        batch_size = 100
        for i in tqdm(range(0, len(points), batch_size), desc="Uploading to Qdrant"):
            batch = points[i:i + batch_size]
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=batch
            )

        print(f"Successfully stored {len(points)} vectors in Qdrant")

    def process_documents(self):
        """Load processed documents and generate embeddings."""
        # Load processed documents
        processed_file = self.processed_dir / "processed_documents.json"

        if not processed_file.exists():
            print(f"Error: Processed documents file not found: {processed_file}")
            print("Please run document-processor.py first")
            return

        print(f"Loading processed documents from: {processed_file}")
        with open(processed_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)

        # Collect all chunks
        all_chunks = []
        for doc in documents:
            all_chunks.extend(doc["chunks"])

        print(f"Total chunks to process: {len(all_chunks)}")

        # Extract texts for embedding
        texts = [chunk["text"] for chunk in all_chunks]

        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.generate_embeddings_batch(texts, batch_size=100)

        # Store in Qdrant
        print("Storing embeddings in Qdrant...")
        self.store_embeddings_in_qdrant(all_chunks, embeddings)

        # Save summary
        summary = {
            "total_documents": len(documents),
            "total_chunks": len(all_chunks),
            "embedding_model": self.embedding_model,
            "collection_name": self.collection_name
        }

        summary_file = self.processed_dir / "embedding_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"\nEmbedding summary saved to: {summary_file}")

    def test_search(self, query: str, top_k: int = 3):
        """
        Test similarity search with a query.

        Args:
            query: Search query
            top_k: Number of results to return
        """
        print(f"\nTesting search with query: '{query}'")

        # Generate query embedding
        query_embedding = self.generate_embedding(query)

        # Search
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )

        print(f"\nTop {top_k} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Score: {result.score:.4f}")
            print(f"   Source: {result.payload['source_file']}")
            print(f"   Text: {result.payload['text'][:200]}...")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Aidemy Chatbot - Embeddings Generator")
    print("=" * 60)

    # Get configuration from environment
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))

    # Initialize generator
    generator = EmbeddingsGenerator(
        qdrant_host=qdrant_host,
        qdrant_port=qdrant_port
    )

    # Create collection
    generator.create_collection()

    # Process documents and generate embeddings
    generator.process_documents()

    # Test search
    test_queries = [
        "Come funzionano i servizi Aidemy?",
        "Quanto costa l'Esplorazione Strategica?",
        "Avete case study?"
    ]

    for query in test_queries:
        generator.test_search(query, top_k=3)


if __name__ == "__main__":
    main()
