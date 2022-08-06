from fastapi import FastAPI, status , Response, Body, HTTPException
from pydantic import BaseModel

class Post(BaseModel):
    title : str

app = FastAPI()

@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    return post


class Post2(BaseModel):
    title: str
    nb_views: int

app2 = FastAPI()

# Dummy database:
posts = {
    1: Post2(title="Hello", nb_views=100),
}

#@app2.get("/posts/{id}")
#async def get_post(id: int):
#    return posts[id]

class PublicPost(BaseModel):
    title:str

@app2.get("/posts/{id}", response_model=PublicPost)
async def get_post(id:int):
    return posts[id]

app3 = FastAPI()

@app3.get("/")
async def custom_header(response: Response):
    response.headers['Custom-Header'] = "Custom-Header-Value"
    return {"hello":"world"}

posts2 = {
    1: Post(title="Hello", nb_views=100),
}

app4 = FastAPI()
@app4.put("/posts/{id}")
async def update_or_create_post(id:int, post:Post, response:Response):
    if id not in posts2:
        response.status_code = status.HTTP_201_CREATED
    posts2[id] = post
    return posts2[id]

app5 = FastAPI()
@app5.post("/password")
async def check_password(password: str = Body(...), password_confirm: str = Body(...)):
    if password != password_confirm:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Passwords don't match.",
        )
    return {"message":"Passwords match."}