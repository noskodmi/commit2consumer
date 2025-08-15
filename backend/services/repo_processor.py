import os
import uuid
import tempfile
import git
import logging
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import chromadb
from config import settings

logger = logging.getLogger(__name__)

# File extensions to include in processing
CODE_EXTENSIONS = (".py", ".js", ".ts", ".jsx", ".tsx", ".sol", ".md", ".go", ".rs", ".java", ".c", ".cpp", ".h")

async def process_repo(url: str):
    """Process a GitHub repository and store its chunks in ChromaDB"""
    logger.info(f"Processing repository: {url}")
    
    repo_id = str(uuid.uuid4())
    tmp_dir = tempfile.mkdtemp()
    
    try:
        # Clone repository
        logger.info(f"Cloning repository {url} to {tmp_dir}")
        git.Repo.clone_from(url, tmp_dir, depth=1)
        
        # Filter and read code files
        code_files = []
        for root, _, files in os.walk(tmp_dir):
            # Skip hidden directories and node_modules
            if any(part.startswith('.') for part in root.split(os.sep)) or 'node_modules' in root:
                continue
                
            for f in files:
                if f.endswith(CODE_EXTENSIONS) and not f.startswith('.'):
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", errors="ignore") as fp:
                            content = fp.read()
                            if content.strip():  # Skip empty files
                                code_files.append({
                                    "content": content,
                                    "path": os.path.relpath(path, tmp_dir)
                                })
                    except Exception as e:
                        logger.warning(f"Error reading file {path}: {str(e)}")
        
        logger.info(f"Found {len(code_files)} code files in repository")
        
        # Chunk the code files
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = []
        
        for file in code_files:
            file_chunks = splitter.split_text(file["content"])
            # Add file path as metadata to each chunk
            chunks.extend([f"File: {file['path']}\n\n{chunk}" for chunk in file_chunks])
        
        logger.info(f"Split repository into {len(chunks)} chunks")
        
        # Create embeddings and store in ChromaDB
        try:
            embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
            client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
            
            # Create a new collection for this repository
            collection = client.create_collection(name=repo_id)
            
            # Add chunks to collection
            for i, chunk in enumerate(chunks):
                collection.add(documents=[chunk], ids=[f"{repo_id}_{i}"])
            
            logger.info(f"Successfully stored {len(chunks)} chunks in ChromaDB")
            
            # Create metadata
            meta = {"id": repo_id, "url": url, "chunks": len(chunks)}
            return repo_id, meta
            
        except Exception as e:
            logger.error(f"Error creating embeddings or storing in ChromaDB: {str(e)}")
            raise
    
    except Exception as e:
        logger.error(f"Error processing repository {url}: {str(e)}")
        raise
    
    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(tmp_dir)
            logger.info(f"Cleaned up temporary directory {tmp_dir}")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory {tmp_dir}: {str(e)}")