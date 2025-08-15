import os
from langchain_openai import ChatOpenAI
import chromadb
from config import settings

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)

def get_docs(repo_id: str):
    # For MVP, just return a placeholder
    return {"docs": f"Auto-generated docs for repo {repo_id}"}

def get_faq(repo_id: str):
    return {"faq": ["How to install?", "How to contribute?", "License info?"]}

def chat(repo_id: str, question: str):
    collection = client.get_collection(name=repo_id)
    results = collection.query(query_texts=[question], n_results=3)
    context = "\n".join([doc for doc in results["documents"][0]])
    prompt = f"Context:\n{context}\n\nQuestion: {question}"
    answer = llm.invoke(f"Context:\n{context}\n\nQuestion: {question}")
    return {"answer": answer}