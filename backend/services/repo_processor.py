import os
import uuid
import tempfile
import git
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import chromadb
from config import settings

TOPIC_FILTERS = ["mantle", "defi", "blockchain"]

async def process_repo(url: str):
    repo_id = str(uuid.uuid4())
    tmp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(url, tmp_dir, depth=1)

    # Filter files
    code_files = []
    for root, _, files in os.walk(tmp_dir):
        for f in files:
            if f.endswith((".py", ".js", ".ts", ".sol", ".md")):
                path = os.path.join(root, f)
                with open(path, "r", errors="ignore") as fp:
                    code_files.append(fp.read())

    # Chunk & embed
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = []
    for doc in code_files:
        chunks.extend(splitter.split_text(doc))

    embeddings = OpenAIEmbeddings()
    client = chromadb.PersistentClient(path=settings.VECTOR_DB_PATH)
    collection = client.create_collection(name=repo_id)
    for i, chunk in enumerate(chunks):
        collection.add(documents=[chunk], ids=[f"{repo_id}_{i}"])

    meta = {"id": repo_id, "url": url, "chunks": len(chunks)}
    return repo_id, meta