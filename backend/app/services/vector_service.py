import chromadb
from chromadb.config import Settings as ChromaSettings
import uuid
from typing import List, Dict, Optional, Tuple
import logging
from sentence_transformers import SentenceTransformer
import tiktoken
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.core.config import settings
from app.services.text_splitter import TextSplitter

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = TextSplitter()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize tokenizer for context management
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            logger.warning("Could not load tiktoken encoder, using approximate token counting")
            self.tokenizer = None
    
    async def create_collection(self, repo_id: str) -> str:
        """Create a vector collection for a repository"""
        try:
            collection_name = f"repo_{repo_id.replace('-', '_')}"
            
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(name=collection_name)
            except Exception:
                pass  # Collection doesn't exist
            
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"repository_id": repo_id}
            )
            
            logger.info(f"Created vector collection: {collection_name}")
            return collection_name
            
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            raise ValueError(f"Failed to create vector collection: {str(e)}")
    
    async def add_documents(self, collection_name: str, documents: List[Dict[str, any]]) -> List[str]:
        """Add documents to vector collection"""
        try:
            collection = self.client.get_collection(name=collection_name)
            
            all_chunks = []
            all_embeddings = []
            all_metadatas = []
            all_ids = []
            
            for doc in documents:
                # Split document into chunks
                chunks = await self.text_splitter.split_code(
                    doc['content'], 
                    doc['language'],
                    doc['path']
                )
                
                for i, chunk in enumerate(chunks):
                    chunk_id = str(uuid.uuid4())
                    
                    all_chunks.append(chunk['content'])
                    all_metadatas.append({
                        'file_path': doc['path'],
                        'language': doc['language'],
                        'chunk_index': i,
                        'chunk_type': chunk['type'],
                        'start_line': chunk.get('start_line', 0),
                        'end_line': chunk.get('end_line', 0)
                    })
                    all_ids.append(chunk_id)
            
            # Generate embeddings in batches
            batch_size = 32
            for i in range(0, len(all_chunks), batch_size):
                batch_chunks = all_chunks[i:i+batch_size]
                batch_embeddings = await self._generate_embeddings(batch_chunks)
                all_embeddings.extend(batch_embeddings)
            
            # Add to collection
            collection.add(
                documents=all_chunks,
                embeddings=all_embeddings,
                metadatas=all_metadatas,
                ids=all_ids
            )
            
            logger.info(f"Added {len(all_chunks)} chunks to collection {collection_name}")
            return all_ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise ValueError(f"Failed to add documents to vector store: {str(e)}")
    
    async def search_similar(
        self, 
        collection_name: str, 
        query: str, 
        n_results: int = 5,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, any]]:
        """Search for similar content in vector collection"""
        try:
            collection = self.client.get_collection(name=collection_name)
            
            # Generate query embedding
            query_embedding = await self._generate_embeddings([query])
            
            # Search
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                where=filter_dict,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise ValueError(f"Vector search failed: {str(e)}")
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                self.executor,
                self.embedding_model.encode,
                texts
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Approximate: 1 token ≈ 4 characters
            return len(text) // 4
    
    async def delete_collection(self, collection_name: str):
        """Delete a vector collection"""
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.warning(f"Could not delete collection {collection_name}: {str(e)}")
