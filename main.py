import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.dependencies.db import get_db
from src.routes import contacts, auth

app = FastAPI()

app.include_router(contacts.router, prefix='/api')
app.include_router(auth.router, prefix='/api')

@app.post("/halthchecker")
async def halthchecker(db: Session=Depends(get_db)):
    try:
        result = db.execute(text('SELECT 1')).fetchone()

        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        
    except Exception as err:
        raise HTTPException(status_code=500, detail="Error connecting to the database")
    
    return {"message": "Wellcome to FastAPI"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)