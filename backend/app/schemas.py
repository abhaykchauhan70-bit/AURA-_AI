from pydantic import BaseModel, EmailStr, Field

class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
class ConversationCreate(BaseModel):
    title: str = Field(default="New conversation", max_length=200)
class RunRequest(BaseModel):
    goal: str = Field(min_length=1, max_length=10000)
    conversation_id: int | None = None
    file_id: int | None = None
class MemoryCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    memory_type: str = "semantic"
    important: bool = False
