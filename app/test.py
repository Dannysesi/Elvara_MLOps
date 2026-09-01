# Frontend -> API (Request) -> Backend (DataBase)
# Backend (Database) -> API (Respond) -> Frontend (Visulise)

# CRUD -  PPGD - /user, /products, /todos, /orders/tywtw575
from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()


class Todo(BaseModel):
    id: int
    title: str

@app.get('/')
def homes():
    return {"message": "Hello World!"}


@app.get('/todos')
def get_todos():
    return [
        {'id': 1, 'title': 'Learn APIs'},
        {'id': 2, 'title': 'Building FastAPI project'},
        {'id': 3, 'title': 'Learn MLOps'},
        {'id': 4, 'title': 'Deploy ELvare Sepsis Model'},
    ]


@app.post('/todos')
def create_todo(todo: Todo):
    return todo