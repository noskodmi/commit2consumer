from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import json
import asyncio
from uuid import UUID, uuid4
import logging

from app.core.database import get_db, Repository, Document, Conversation, Message
from app.services.github_service import GitHubService
from app.services.rag_service import RAGService
from app.services.background_tasks import process_repository_task
from app.services.documentation_generator import DocumentationGenerator
from app.api.benchmark_routes import benchmark_router

logger = logging.getLogger(__name__)
router = APIRouter()
router.include_router(benchmark_router, prefix="/benchmark", tags=["benchmarks"])
# Pydantic models for request/response
from pydantic import BaseModel, HttpUrl

class RepositorySubmission(BaseModel):
    url: HttpUrl
    name: Optional[str] = None

class ChatMessage(BaseModel):
    content: str
    conversation_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    answer: str
    conversation_id: UUID
    sources: List[str]
    suggested_questions: Optional[List[str]] = None

class RepositoryResponse(BaseModel):
    id: UUID
    name: str
    full_name: str
    status: str
    processed_at: Optional[str] = None
    error_message: Optional[str] = None

# Repository endpoints
@router.post("/repositories/", response_model=Dict[str, any])
async def submit_repository(
    repo_data: RepositorySubmission,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit a repository for processing"""
    try:
        github_service = GitHubService()
        
        # Validate repository
        repo_info = await github_service.validate_repository(str(repo_data.url))
        
        # Check if repository already exists
        existing_repo = db.query(Repository).filter(
            Repository.full_name == repo_info['full_name']
        ).first()
        
        if existing_repo:
            if existing_repo.status == "completed":
                return {
                    "message": "Repository already processed",
                    "repository": {
                        "id": existing_repo.id,
                        "name": existing_repo.name,
                        "status": existing_repo.status
                    }
                }
            elif existing_repo.status == "processing":
                return {
                    "message": "Repository is currently being processed",
                    "repository": {
                        "id": existing_repo.id,
                        "name": existing_repo.name,
                        "status": existing_repo.status
                    }
                }
        
        # Create new repository record
        repository = Repository(
            name=repo_data.name or repo_info['name'],
            full_name=repo_info['full_name'],
            url=repo_info['url'],
            description=repo_info.get('description'),
            language=repo_info.get('language'),
            stars=repo_info.get('stars', 0),
            forks=repo_info.get('forks', 0),
            size=repo_info.get('size', 0),
            status="pending"
        )
        
        db.add(repository)
        db.commit()
        db.refresh(repository)
        
        # Start background processing
        background_tasks.add_task(
            process_repository_task.delay,
            str(repository.id),
            str(repo_data.url)
        )
        
        return {
            "message": "Repository submitted for processing",
            "repository": {
                "id": repository.id,
                "name": repository.name,
                "status": repository.status,
                "full_name": repository.full_name
            }
        }
        
    except Exception as e:
        logger.error(f"Repository submission error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/repositories/", response_model=List[RepositoryResponse])
async def list_repositories(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List repositories"""
    query = db.query(Repository)
    
    if status:
        query = query.filter(Repository.status == status)
    
    repositories = query.offset(skip).limit(limit).all()
    
    return [
        RepositoryResponse(
            id=repo.id,
            name=repo.name,
            full_name=repo.full_name,
            status=repo.status,
            processed_at=repo.processed_at.isoformat() if repo.processed_at else None,
            error_message=repo.error_message
        )
        for repo in repositories
    ]

@router.get("/repositories/{repo_id}")
async def get_repository(repo_id: UUID, db: Session = Depends(get_db)):
    """Get repository details"""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Get document count
    doc_count = db.query(Document).filter(Document.repository_id == repo_id).count()
    
    return {
        "id": repository.id,
        "name": repository.name,
        "full_name": repository.full_name,
        "url": repository.url,
        "description": repository.description,
        "language": repository.language,
        "stars": repository.stars,
        "forks": repository.forks,
        "status": repository.status,
        "processed_at": repository.processed_at,
        "error_message": repository.error_message,
        "document_count": doc_count,
        "created_at": repository.created_at,
        "updated_at": repository.updated_at
    }

@router.get("/repositories/{repo_id}/files")
async def get_repository_files(
    repo_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    language: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get repository files"""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    query = db.query(Document).filter(Document.repository_id == repo_id)
    
    if language:
        query = query.filter(Document.language == language)
    
    documents = query.offset(skip).limit(limit).all()
    
    return {
        "files": [
            {
                "id": doc.id,
                "file_path": doc.file_path,
                "language": doc.language,
                "size": doc.size,
                "chunk_count": doc.chunk_count
            }
            for doc in documents
        ],
        "total": query.count()
    }

# Chat endpoints
@router.post("/repositories/{repo_id}/chat")
async def chat_with_repository(
    repo_id: UUID,
    message: ChatMessage,
    db: Session = Depends(get_db)
):
    """Chat with repository using RAG"""
    try:
        # Verify repository exists and is processed
        repository = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        if repository.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Repository not ready for chat. Status: {repository.status}"
            )
        
        # Get or create conversation
        conversation_id = message.conversation_id
        if not conversation_id:
            conversation = Conversation(
                repository_id=repo_id,
                title=message.content[:50] + "..." if len(message.content) > 50 else message.content
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = conversation.id
        else:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.repository_id == repo_id
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get conversation history
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).all()
        
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Use RAG to answer question
        rag_service = RAGService()
        collection_name = f"repo_{str(repo_id).replace('-', '_')}"
        
        repository_info = {
            "name": repository.name,
            "description": repository.description,
            "language": repository.language
        }
        
        result = await rag_service.answer_question(
            collection_name=collection_name,
            question=message.content,
            conversation_history=conversation_history,
            repository_info=repository_info
        )
        
        # Save user message
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=message.content
        )
        db.add(user_message)
        
        # Save assistant response
        assistant_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=result['answer'],
            context_used=result['context_used']
        )
        db.add(assistant_message)
        
        db.commit()
        
        # Generate suggested questions for new conversations
        suggested_questions = None
        if len(conversation_history) == 0:  # First message in conversation
            suggested_questions = await rag_service.generate_suggested_questions(
                collection_name, repository_info
            )
        
        return ChatResponse(
            answer=result['answer'],
            conversation_id=conversation_id,
            sources=result['sources'],
            suggested_questions=suggested_questions
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/repositories/{repo_id}/conversations")
async def get_conversations(
    repo_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get repository conversations"""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    conversations = db.query(Conversation).filter(
        Conversation.repository_id == repo_id
    ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for conv in conversations:
        # Get message count and last message
        message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
        last_message = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at.desc()).first()
        
        result.append({
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "message_count": message_count,
            "last_message": last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else None
        })
    
    return {"conversations": result}

@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get conversation messages"""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).offset(skip).limit(limit).all()
    
    return {
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "context_used": msg.context_used,
                "created_at": msg.created_at
            }
            for msg in messages
        ],
        "conversation": {
            "id": conversation.id,
            "title": conversation.title,
            "repository_id": conversation.repository_id
        }
    }

# Documentation endpoints
@router.get("/repositories/{repo_id}/documentation")
async def get_documentation(repo_id: UUID, db: Session = Depends(get_db)):
    """Get generated documentation for repository"""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Documentation not available. Repository not fully processed."
        )
    
    try:
        # Get repository files for documentation generation
        documents = db.query(Document).filter(Document.repository_id == repo_id).all()
        
        repository_data = {
            'name': repository.name,
            'description': repository.description,
            'language': repository.language,
            'files': [
                {
                    'path': doc.file_path,
                    'content': doc.content,
                    'language': doc.language,
                    'size': doc.size
                }
                for doc in documents
            ]
        }
        
        doc_generator = DocumentationGenerator()
        documentation = await doc_generator.generate_documentation(repository_data)
        
        return {
            "repository_id": repo_id,
            "documentation": documentation,
            "generated_at": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"Documentation generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate documentation")

@router.get("/repositories/{repo_id}/faq")
async def get_faq(repo_id: UUID, db: Session = Depends(get_db)):
    """Get generated FAQ for repository"""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="FAQ not available. Repository not fully processed."
        )
    
    try:
        documents = db.query(Document).filter(Document.repository_id == repo_id).all()
        
        repository_data = {
            'name': repository.name,
            'description': repository.description,
            'language': repository.language,
            'files': [
                {
                    'path': doc.file_path,
                    'content': doc.content,
                    'language': doc.language
                }
                for doc in documents
            ]
        }
        
        doc_generator = DocumentationGenerator()
        faq = await doc_generator.generate_faq(repository_data)
        
        return {
            "repository_id": repo_id,
            "faq": faq,
            "generated_at": asyncio.get_event_loop().time()
        }
        
    except Exception as e:
        logger.error(f"FAQ generation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate FAQ")

# Health and utility endpoints
@router.get("/search/{repo_id}")
async def search_repository(
    repo_id: UUID,
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """Search within repository content"""
    repository = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    if repository.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Search not available. Repository not fully processed."
        )
    
    try:
        from app.services.vector_service import VectorService
        vector_service = VectorService()
        collection_name = f"repo_{str(repo_id).replace('-', '_')}"
        
        results = await vector_service.search_similar(
            collection_name=collection_name,
            query=query,
            n_results=limit
        )
        
        return {
            "query": query,
            "results": [
                {
                    "content": result['content'][:200] + "..." if len(result['content']) > 200 else result['content'],
                    "file_path": result['metadata']['file_path'],
                    "language": result['metadata'].get('language', 'unknown'),
                    "relevance_score": 1 - result['distance']
                }
                for result in results
            ]
        }
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")