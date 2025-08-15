from pydantic import BaseModel

class AddRepoRequest(BaseModel):
    url: str

class RepoMeta(BaseModel):
    id: str
    url: str
    chunks: int

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

class FAQResponse(BaseModel):
    faq: list[str]

class DocsResponse(BaseModel):
    docs: str