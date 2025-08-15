import os
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import chromadb
from config import settings

logger = logging.getLogger(__name__)

# Initialize LLM with error handling
try:
    llm = ChatOpenAI(
        model="gpt-3.5-turbo", 
        temperature=0, 
        api_key=settings.OPENAI_API_KEY
    )
    logger.info("LLM service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM service: {str(e)}")
    llm = None

# Initialize ChromaDB client
try:
    client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
    logger.info(f"ChromaDB initialized with path: {settings.VECTOR_DB_PATH}")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {str(e)}")
    client = None

def get_docs(repo_id: str):
    """Generate documentation for a repository"""
    logger.info(f"Generating docs for repo {repo_id}")
    
    try:
        # Get repository context
        collection = client.get_collection(name=repo_id)
        results = collection.query(query_texts=["repository documentation overview"], n_results=5)
        context = "\n".join([doc for doc in results["documents"][0]])
        
        # Generate documentation using LLM
        prompt = f"""
        Based on the following code repository context, generate comprehensive documentation:
        
        {context}
        
        Include:
        1. Overview of the repository
        2. Main components
        3. Setup instructions
        4. Basic usage examples
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        docs = response.content
        
        logger.info(f"Successfully generated docs for {repo_id}")
        return {"docs": docs}
    
    except Exception as e:
        logger.error(f"Error generating docs for {repo_id}: {str(e)}")
        # Fallback to placeholder for MVP
        return {"docs": f"Auto-generated documentation for repository {repo_id}. (Error: {str(e)})"}

def get_faq(repo_id: str):
    """Generate FAQ for a repository"""
    logger.info(f"Generating FAQ for repo {repo_id}")
    
    try:
        # Get repository context
        collection = client.get_collection(name=repo_id)
        results = collection.query(query_texts=["common questions repository"], n_results=5)
        context = "\n".join([doc for doc in results["documents"][0]])
        
        # Generate FAQ using LLM
        prompt = f"""
        Based on the following code repository context, generate a list of 5 frequently asked questions and their answers:
        
        {context}
        
        Format each FAQ as a question followed by its answer.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Parse the response into a list of questions
        faq_text = response.content
        faq_items = faq_text.split("\n\n")
        faq_list = [item.strip() for item in faq_items if item.strip()]
        
        logger.info(f"Successfully generated {len(faq_list)} FAQ items for {repo_id}")
        return {"faq": faq_list}
    
    except Exception as e:
        logger.error(f"Error generating FAQ for {repo_id}: {str(e)}")
        # Fallback to placeholder for MVP
        return {"faq": [
            "How do I install this repository?",
            "What are the main features?",
            "How can I contribute to this project?",
            "What license is this project under?",
            "Who maintains this project?"
        ]}

def chat(repo_id: str, question: str):
    """Chat with a repository"""
    logger.info(f"Processing chat for repo {repo_id}: {question}")
    
    try:
        # Get relevant context from the repository
        collection = client.get_collection(name=repo_id)
        results = collection.query(query_texts=[question], n_results=3)
        context = "\n".join([doc for doc in results["documents"][0]])
        
        # Generate answer using LLM
        prompt = f"""
        Based on the following code repository context, answer the user's question:
        
        Context:
        {context}
        
        Question: {question}
        
        Provide a clear, concise, and accurate answer based only on the information in the context.
        """
        
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content
        
        logger.info(f"Successfully generated chat response for {repo_id}")
        return {"answer": answer}
    
    except Exception as e:
        logger.error(f"Error in chat for {repo_id}: {str(e)}")
        return {"answer": f"I'm sorry, I encountered an error while processing your question. Please try again later. Error: {str(e)}"}