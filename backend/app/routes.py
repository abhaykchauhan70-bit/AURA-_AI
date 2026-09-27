from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import get_db
from app.models import User, Conversation, Message, Task, StoredFile, Memory
from app.schemas import Credentials, Token, ConversationCreate, RunRequest, MemoryCreate
from app.security import current_user, hash_password, verify_password, make_token
from app.config import settings
from app.agents import make_plan, verify_result
from app.tools import profile_table, search_text

router = APIRouter()
@router.post("/auth/register", response_model=Token)
def register(data: Credentials, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == data.email.lower())): raise HTTPException(409, "Email already registered")
    user = User(email=data.email.lower(), password_hash=hash_password(data.password)); db.add(user); db.commit(); db.refresh(user)
    return Token(access_token=make_token(user.id))

@router.post("/auth/login", response_model=Token)
def login(data: Credentials, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash): raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=make_token(user.id))

@router.get("/conversations")
def conversations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": c.id, "title": c.title, "created_at": c.created_at} for c in db.scalars(select(Conversation).where(Conversation.user_id == user.id).order_by(Conversation.id.desc()))]

@router.post("/conversations")
def create_conversation(data: ConversationCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = Conversation(user_id=user.id, title=data.title); db.add(item); db.commit(); db.refresh(item); return {"id": item.id, "title": item.title}

@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    c = db.get(Conversation, conversation_id)
    if not c or c.user_id != user.id: raise HTTPException(404, "Conversation not found")
    return {"id": c.id, "title": c.title, "messages": [{"role": m.role, "content": m.content, "created_at": m.created_at} for m in c.messages]}

@router.post("/files/upload")
async def upload(file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    allowed = {".txt", ".md", ".csv", ".json", ".xlsx"}
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in allowed: raise HTTPException(415, "Supported file types: TXT, MD, CSV, JSON, XLSX")
    raw = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(raw) > settings.max_upload_mb * 1024 * 1024: raise HTTPException(413, "File exceeds configured size limit")
    folder = Path(settings.upload_dir).resolve(); folder.mkdir(parents=True, exist_ok=True)
    storage_name = f"{uuid4().hex}{suffix}"; target = folder / storage_name; target.write_bytes(raw)
    text = raw.decode("utf-8", errors="replace")[:2_000_000] if suffix in {".txt", ".md", ".csv", ".json"} else ""
    record = StoredFile(user_id=user.id, filename=Path(file.filename or "upload").name[:255], storage_name=storage_name, extracted_text=text)
    db.add(record); db.commit(); db.refresh(record)
    return {"id": record.id, "filename": record.filename, "message": "Stored privately"}

@router.get("/files")
def list_files(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": f.id, "filename": f.filename, "created_at": f.created_at} for f in db.scalars(select(StoredFile).where(StoredFile.user_id == user.id))]

@router.delete("/files/{file_id}")
def delete_file(file_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    f = db.get(StoredFile, file_id)
    if not f or f.user_id != user.id: raise HTTPException(404, "File not found")
    (Path(settings.upload_dir) / f.storage_name).unlink(missing_ok=True); db.delete(f); db.commit(); return {"deleted": True}

@router.post("/agent/run")
def run_agent(data: RunRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    if data.conversation_id:
        convo = db.get(Conversation, data.conversation_id)
        if not convo or convo.user_id != user.id: raise HTTPException(404, "Conversation not found")
    else:
        convo = Conversation(user_id=user.id, title=data.goal[:80]); db.add(convo); db.flush()
    attached = db.get(StoredFile, data.file_id) if data.file_id else None
    if data.file_id and (not attached or attached.user_id != user.id): raise HTTPException(404, "File not found")
    db.add(Message(conversation_id=convo.id, role="user", content=data.goal))
    plan = make_plan(data.goal, attached is not None)
    task = Task(user_id=user.id, goal=data.goal, status="COMPLETED", plan=plan); db.add(task); db.flush()
    evidence = ""; tool_result = None
    if attached:
        path = Path(settings.upload_dir) / attached.storage_name
        if path.suffix.lower() in {".csv", ".xlsx"} and any(k in data.goal.lower() for k in ["analy", "pattern", "dataset", "spreadsheet", "csv", "excel"]):
            try:
                tool_result = profile_table(path); evidence = f"Dataset profile: {tool_result}"
                for item in plan:
                    if item["agent"] == "data_agent": item["status"] = "COMPLETED"
            except Exception as exc:
                task.status = "FAILED"; evidence = f"Data analysis failed: {type(exc).__name__}: {exc}"
        elif attached.extracted_text:
            matches = search_text(attached.extracted_text, data.goal)
            evidence = "Document excerpts (keyword ranked):\n" + "\n".join(f"- {m}" for m in matches)
    if evidence:
        result = evidence + "\n\nThis result is based on the uploaded file and the operations listed above."
    else:
        result = "I recorded your task and created a plan. No external research or LLM reasoning was performed. Configure a provider or attach a supported file to enable those capabilities."
    task.result = result; task.verification = verify_result(data.goal, result)
    db.add(Message(conversation_id=convo.id, role="assistant", content=result)); db.commit(); db.refresh(task)
    return {"task_id": task.id, "conversation_id": convo.id, "status": task.status, "plan": plan, "result": result, "tool_result": tool_result, "verification": task.verification}

@router.get("/agent/tasks/{task_id}")
def get_task(task_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t or t.user_id != user.id: raise HTTPException(404, "Task not found")
    return {"id": t.id, "goal": t.goal, "status": t.status, "plan": t.plan, "result": t.result, "verification": t.verification}

@router.get("/memory")
def memories(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": m.id, "content": m.content, "type": m.memory_type, "important": m.important} for m in db.scalars(select(Memory).where(Memory.user_id == user.id))]
@router.post("/memory")
def add_memory(data: MemoryCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    m = Memory(user_id=user.id, content=data.content, memory_type=data.memory_type, important=data.important); db.add(m); db.commit(); db.refresh(m); return {"id": m.id}
@router.delete("/memory/{memory_id}")
def delete_memory(memory_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    m = db.get(Memory, memory_id)
    if not m or m.user_id != user.id: raise HTTPException(404, "Memory not found")
    db.delete(m); db.commit(); return {"deleted": True}
