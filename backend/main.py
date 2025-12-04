"""Main FastAPI Application Entry Point"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
import os
from typing import Optional
import jwt
from pydantic import BaseModel
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "task_management")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Global database connection
db: Optional[AsyncIOMotorDatabase] = None
client: Optional[AsyncIOMotorClient] = None

# Pydantic Models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "developer"

class UserLogin(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    status: str = "todo"
    due_date: Optional[str] = None
    assignee_id: Optional[str] = None
    tags: list = []

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None
    assignee_id: Optional[str] = None
    tags: Optional[list] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# JWT Token Handler
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthCredentials = Depends(HTTPBearer())) -> dict:
    """Verify JWT token and return decoded data"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Lifespan Events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global client, db
    # Startup
    print("Starting up application...")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[MONGODB_DB_NAME]
    print("Connected to MongoDB")
    yield
    # Shutdown
    print("Shutting down application...")
    client.close()
    print("Disconnected from MongoDB")

# Create FastAPI app
app = FastAPI(
    title="AI Task Management System API",
    description="Full-stack task management system with AI capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Task Management System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Authentication Endpoints
@app.post("/api/v1/auth/register", response_model=dict)
async def register(user: UserCreate):
    """Register new user"""
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        new_user = {
            "email": user.email,
            "password": user.password,  # In production, hash this!
            "full_name": user.full_name,
            "role": user.role,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.users.insert_one(new_user)
        new_user["_id"] = str(result.inserted_id)
        del new_user["password"]
        return {"status": "success", "data": new_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    try:
        # Find user
        user = await db.users.find_one({"email": credentials.email})
        if not user or user["password"] != credentials.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user["_id"]), "email": user["email"], "role": user["role"]},
            expires_delta=access_token_expires
        )
        
        user_data = {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Task Endpoints
@app.get("/api/v1/tasks")
async def get_tasks(token: dict = Depends(verify_token), skip: int = 0, limit: int = 10):
    """Get all tasks"""
    try:
        tasks = []
        async for task in db.tasks.find().skip(skip).limit(limit):
            task["_id"] = str(task["_id"])
            tasks.append(task)
        
        total = await db.tasks.count_documents({})
        return {
            "data": tasks,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tasks")
async def create_task(task: TaskCreate, token: dict = Depends(verify_token)):
    """Create new task"""
    try:
        new_task = {
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "due_date": task.due_date,
            "assignee_id": task.assignee_id,
            "created_by": token["sub"],
            "tags": task.tags,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.tasks.insert_one(new_task)
        new_task["_id"] = str(result.inserted_id)
        return {"status": "success", "data": new_task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tasks/{task_id}")
async def get_task(task_id: str, token: dict = Depends(verify_token)):
    """Get specific task"""
    try:
        from bson import ObjectId
        task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        task["_id"] = str(task["_id"])
        return {"data": task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/tasks/{task_id}")
async def update_task(task_id: str, task_update: TaskUpdate, token: dict = Depends(verify_token)):
    """Update task"""
    try:
        from bson import ObjectId
        update_data = {k: v for k, v in task_update.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.tasks.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        updated_task = await db.tasks.find_one({"_id": ObjectId(task_id)})
        updated_task["_id"] = str(updated_task["_id"])
        return {"status": "success", "data": updated_task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/tasks/{task_id}")
async def delete_task(task_id: str, token: dict = Depends(verify_token)):
    """Delete task"""
    try:
        from bson import ObjectId
        result = await db.tasks.delete_one({"_id": ObjectId(task_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"status": "success", "message": "Task deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
