import openai
from typing import List, Dict, Optional, Tuple
import asyncio
import logging
from app.core.config import settings
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.client = openai.AsyncOpenAI()
        self.vector_service = VectorService()
        self.max_context_tokens = 3000
        
    async def answer_question(
        self, 
        collection_name: str,
        question: str,
        conversation_history: List[Dict[str, str]] = None,
        repository_info: Dict[str, any] = None
    ) -> Dict[str, any]:
        """Answer a question using RAG"""
        try:
            # Retrieve relevant context
            context_chunks = await self.vector_service.search_similar(
                collection_name=collection_name,
                query=question,
                n_results=8
            )
            
            # Build context
            context = self._build_context(context_chunks)
            
            # Prepare conversation
            messages = self._prepare_messages(
                question=question,
                context=context,
                conversation_history=conversation_history or [],
                repository_info=repository_info
            )
            
            # Generate response
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.1,
                max_tokens=1000,
                stream=False
            )
            
            answer = response.choices[0].message.content
            
            return {
                'answer': answer,
                'context_used': [
                    {
                        'file_path': chunk['metadata']['file_path'],
                        'chunk_type': chunk['metadata'].get('chunk_type', 'unknown'),
                        'relevance_score': 1 - chunk['distance']  # Convert distance to relevance
                    }
                    for chunk in context_chunks[:3]  # Top 3 most relevant
                ],
                'sources': list(set(chunk['metadata']['file_path'] for chunk in context_chunks))
            }
            
        except Exception as e:
            logger.error(f"RAG answer generation error: {str(e)}")
            raise ValueError(f"Failed to generate answer: {str(e)}")
    
    def _build_context(self, chunks: List[Dict[str, any]]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        total_tokens = 0
        
        for chunk in chunks:
            chunk_content = f"File: {chunk['metadata']['file_path']}\n"
            chunk_content += f"Language: {chunk['metadata'].get('language', 'unknown')}\n"
            chunk_content += f"Content:\n{chunk['content']}\n"
            chunk_content += "---\n"
            
            chunk_tokens = self.vector_service.count_tokens(chunk_content)
            
            if total_tokens + chunk_tokens > self.max_context_tokens:
                break
                
            context_parts.append(chunk_content)
            total_tokens += chunk_tokens
        
        return "\n".join(context_parts)
    
    def _prepare_messages(
        self,
        question: str,
        context: str,
        conversation_history: List[Dict[str, str]],
        repository_info: Optional[Dict[str, any]] = None
    ) -> List[Dict[str, str]]:
        """Prepare messages for the LLM"""
        
        repo_context = ""
        if repository_info:
            repo_context = f"""
            Repository Information:
            - Name: {repository_info.get('name', 'Unknown')}
            - Description: {repository_info.get('description', 'No description')}
            - Main Language: {repository_info.get('language', 'Unknown')}
            """
        
        system_message = f"""You are an expert code assistant helping users understand a specific repository. 
        
        {repo_context}
        
        Your task is to answer questions about this codebase using the provided context. 
        
        Guidelines:
        - Provide accurate, helpful answers based on the code context
        - Reference specific files and functions when relevant
        - If you're not sure about something, say so clearly
        - Provide code examples when helpful
        - Be concise but thorough
        - If the context doesn't contain enough information, acknowledge this
        
        Context from the repository:
        {context}
        """
        
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history (last 10 messages to stay within limits)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        return messages
    
    async def generate_suggested_questions(
        self, 
        collection_name: str, 
        repository_info: Dict[str, any]
    ) -> List[str]:
        """Generate suggested questions based on repository content"""
        try:
            # Get a sample of different file types
            sample_chunks = await self.vector_service.search_similar(
                collection_name=collection_name,
                query="main function class API",
                n_results=5
            )
            
            context_sample = "\n".join([
                f"File: {chunk['metadata']['file_path']}\n{chunk['content'][:200]}..."
                for chunk in sample_chunks
            ])
            
            prompt = f"""
            Based on this repository sample, generate 5-7 relevant questions that developers might ask about this codebase.
            
            Repository: {repository_info.get('name', 'Unknown')}
            Language: {repository_info.get('language', 'Unknown')}
            
            Sample code:
            {context_sample}
            
            Generate practical questions about:
            - How to use key functions/classes
            - Architecture and design patterns
            - Configuration and setup
            - API endpoints (if applicable)
            - Common workflows
            
            Return as a simple list of questions, one per line.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant generating relevant questions about code repositories."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            questions = [
                q.strip().lstrip('- ').lstrip('1234567890. ')
                for q in response.choices[0].message.content.split('\n')
                if q.strip() and '?' in q
            ]
            
            return questions[:7]  # Limit to 7 questions
            
        except Exception as e:
            logger.error(f"Error generating suggested questions: {str(e)}")
            return [
                "What is the main purpose of this repository?",
                "How do I set up and run this project?",
                "What are the key components or modules?",
                "How does the main functionality work?",
                "What dependencies does this project have?"
            ]
