from fastapi import FastAPI, Path, Body, Header, Cookie
from typing import Optional
from enum import Enum


class UserType(str, Enum):
    STANDARD = "standard"
    ADMIN = "admin"

app = FastAPI()
@app.get("/")
async def hello_world():
    return {"hello":"world"}

app2 = FastAPI()

@app2.get("/users/{type}/{id}")
async def get_user(type:UserType,id:int):
    return {"type":type,"id": id}

app3 = FastAPI()
@app3.get("/users/{id}")
async def get_user(id:int=Path(..., ge=1)):
    return {"id": id}

app4 = FastAPI()
@app4.get("/users")
async def get_user(page:int,size:int=10):
    return {"page": page, "size":size}

@app4.post("/users")
async def create_user(name:str = Body(...),
            age:int = Body(...)):
        return {"name":name, "age":age}

app5 = FastAPI()
@app5.get("/")
async def get_header(hello:str=Header(...)):
    return {"hello":hello}

app6 = FastAPI()
@app6.get("/")
async def get_cookie(hello:Optional[str]=Cookie(None)):
    return {"hello":hello}