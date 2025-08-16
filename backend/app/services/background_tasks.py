import asyncio
import tempfile
import shutil
import os
from celery import Celery
from sqlalchemy.orm import Session
from typing import Dict, any
import logging

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.database import Repository, Document
from app.services.github_service import GitHubService
from app.services.vector_service import VectorService
from app.services.documentation_generator import DocumentationGenerator

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'repo2chat',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

def setup_celery():
    """Setup Celery configuration"""
    return celery_app

@celery_app.task(bind=True)
def process_repository_task(self, repo_id: str, repo_url: str):
    """Celery task to process repository"""
    asyncio.run(_process_repository_async(self, repo_id, repo_url))

async def _process_repository_async(task, repo_id: str, repo_url: str):
    """Async function to process repository"""
    db = SessionLocal()
    temp_dir = None
    
    try:
        # Update status to processing
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise ValueError("Repository not found")
        
        repo.status = "processing"
        db.commit()
        
        # Initialize services
        github_service = GitHubService()
        vector_service = VectorService()
        doc_generator = DocumentationGenerator()
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Clone repository
        task.update_state(state='PROGRESS', meta={'step': 'cloning', 'progress': 20})
        cloned_path = await github_service.clone_repository(repo_url, temp_dir)
        
        # Process files
        task.update_state(state='PROGRESS', meta={'step': 'processing_files', 'progress': 40})
        files_data = await github_service.process_repository(cloned_path)
        
        # Create vector collection
        task.update_state(state='PROGRESS', meta={'step': 'creating_vectors', 'progress': 60})
        collection_name = await vector_service.create_collection(str(repo_id))
        
        # Generate embeddings and store documents
        vector_ids = await vector_service.add_documents(collection_name, files_data)
        
        # Store documents in database
        for i, file_data in enumerate(files_data):
            document = Document(
                repository_id=repo_id,
                file_path=file_data['path'],
                content=file_data['content'],
                language=file_data['language'],
                size=file_data['size'],
                chunk_count=1,  # Will be updated by vector service
                vector_ids=vector_ids[i:i+1] if i < len(vector_ids) else []
            )
            db.add(document)
        
        # Generate documentation
        task.update_state(state='PROGRESS', meta={'step': 'generating_docs', 'progress': 80})
        repository_data = {
            'name': repo.name,
            'description': repo.description,
            'language': repo.language,
            'files': files_data
        }
        
        documentation = await doc_generator.generate_documentation(repository_data)
        faq_data = await doc_generator.generate_faq(repository_data)
        
        # Update repository status
        task.update_state(state='PROGRESS', meta={'step': 'finalizing', 'progress': 95})
        repo.status = "completed"
        repo.processed_at = asyncio.get_event_loop().time()
        
        db.commit()
        
        task.update_state(state='SUCCESS', meta={'step': 'completed', 'progress': 100})
        
        return {
            'status': 'completed',
            'documents_processed': len(files_data),
            'documentation': documentation,
            'faq': faq_data
        }
        
    except Exception as e:
        logger.error(f"Repository processing failed: {str(e)}")
        
        # Update repository status to failed
        if db and repo:
            repo.status = "failed"
            repo.error_message = str(e)
            db.commit()
        
        task.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    
    finally:
        # Cleanup
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if db:
            db.close()
