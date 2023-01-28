from typing import Optional
from pyfiglet import Figlet
from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from routers.auth import get_current_user, get_user_exception
from routers import auth

app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router)  ##swagger birleştirmeye yaradı, aynı anda çalıştı.

@app.get("/figlet")
async def figlets():
        f = Figlet(font='slant')
        print(f.renderText('Database Connections APIs'))
        return f.renderText("APIs")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@app.get("/")
async def read_database(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()

@app.get("/todos/user")
async def read_all_by_user(user: dict = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()

@app.get("/todo/{todo_id}")
async def read_tablo(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(models.Todos).filter(models.Todos.id==todo_id).first()
    if todo_model is not None:
        return todo_model
    raise http_exception()

def http_exception():
    return HTTPException(status_code=404, detail="Todo Not Found")

class Todo(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0, lt=6, description="The priority must be between 1-5")
    complete: bool

@app.post("/")
async def create_todo(todo: Todo,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description=todo.description
    todo_model.priority=todo.priority
    todo_model.priority=todo.priority
    todo_model.complete=todo.complete
    todo_model.owner_id = user.get("id")

    db.add(todo_model)
    db.commit()

    return {
        "status": 201,
        "transaction": "Successful"
    }

@app.put("/{todo_id}")
async def update_todo(todo_id: int, todo: Todo,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):

    if user is None:
        raise get_user_exception()

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id") ).first()

    if todo_model is None:
        raise http_exception()
    todo_model.title = todo.title
    todo_model.decsription = todo.description
    todo_model.priority=todo.priority
    todo_model.complete=todo.complete

    db.add(todo_model)
    db.commit()
    return {
        "status": 200,
        "transaction": "Successful"
    }

@app.delete("/{todo_id}")
async def delete_todo(todo_id: int,
                      user: dict = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    if user is None:
        raise get_user_exception()
    todo_model = db.query(models.Todos).filter(models.Todos.id==todo_id).filter(models.Todos.owner_id == user.get("id")).first()

    if todo_model is None:
        raise http_exception()

    db.query(models.Todos).filter(models.Todos.id == todo_id).delete()
    db.commit()

    return successfull_response(status_code = 200)

def successfull_response(status_code: int):
    return {
        "status": int,
        "transaction": "Successfull"
    }

"""
    ____        __        __                  
   / __ \____ _/ /_____ _/ /_  ____ _________
  / / / / __ `/ __/ __ `/ __ \/ __ `/ ___/ _ \
 / /_/ / /_/ / /_/ /_/ / /_/ / /_/ (__  )  __/
/_____/\__,_/\__/\__,_/_.___/\__,_/____/\___/

   ______                            __  _
  / ____/___  ____  ____  ___  _____/ /_(_)___  ____  _____
 / /   / __ \/ __ \/ __ \/ _ \/ ___/ __/ / __ \/ __ \/ ___/
/ /___/ /_/ / / / / / / /  __/ /__/ /_/ / /_/ / / / (__  )
\____/\____/_/ /_/_/ /_/\___/\___/\__/_/\____/_/ /_/____/

    ___    ____  ____
   /   |  / __ \/  _/____
  / /| | / /_/ // // ___/
 / ___ |/ ____// /(__  )
/_/  |_/_/   /___/____/

"""



