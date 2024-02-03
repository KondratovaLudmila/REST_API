import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis.asyncio as redis 

from src.dependencies.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    The lifespan function is a coroutine that runs when the application starts up.
    It's used to initialize any resources that need to be shared across requests, 
    such as database connections or caches. The lifespan function can also be used 
    to run background tasks.
    
    :param app: FastAPI: Pass the fastapi instance to the lifespan function
    :return: A generator
    :doc-author: Trelent
    """
    r = await redis.Redis(host=settings.redis.host, 
                          port=settings.redis.port, 
                          db=0, 
                          encoding="utf-8", 
                          decode_responses=True)
    await FastAPILimiter.init(r)
    yield


app = FastAPI(lifespan=lifespan)

origins = [ 
    "http://localhost:3000",
    "https://localhost:3000"
    ]

app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/halthchecker")
async def halthchecker(db: Session=Depends(get_db)):
    """
    The halthchecker function is used to check if the database connection is working.
    It will return a message with the status code 200 if everything works fine, otherwise it 
    will return an HTTPException 500.
    
    :param db: Session: Inject the database session into the function
    :return: A dict with a message
    :doc-author: Trelent
    """
    try:
        result = db.execute(text('SELECT 1')).fetchone()

        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        
    except Exception as err:
        raise HTTPException(status_code=500, detail="Error connecting to the database")
    
    return {"message": "Wellcome to FastAPI"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)