
from fastapi import FastAPI, Query, Body, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Mini Blog")

BLOG_POST = [
    {"id": 1, "title": "Hola desde FastAPI", "Content":"Mi primer post con FastAPI"},
    {"id": 2, "title": "Mi segundo Post con FastAPI", "Content":"Mi segundo post con FastAPI blablabla"},
    {"id": 3, "title": "Django vs FastAPI", "Content":"FastAPI es más rápido por x razones"},
]

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: str
    content: str


@app.get("/")
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}


@app.get("/posts")
def list_posts(query: str | None = Query(default=None, description="Texto para buscar por título")):
    
    if query:
        results = [post for post in BLOG_POST if query.lower() in  post["title"].lower() ]
        return {"data": results, "query": query}
    
    return {"data": BLOG_POST}
 
 
@app.get("/posts/{post_id}")
def get_post(post_id: int, include_content: bool = Query(default=True, description="Incluir o no el contenido")):
    for post in BLOG_POST:
        if post["id"] == post_id:
            if not include_content:
                return {"id": post["id"], "title": post["title"]}
            return {"data": post}
    
    return {"error": "Post no encontrado"}

@app.post("/posts")
def create_post(post: PostCreate):
    new_id = (BLOG_POST[-1]["id"]+1) if BLOG_POST else 1
    new_post = {"id": new_id, "title": post.title, "content": post.content}
    BLOG_POST.append(new_post)
    return {"message": "Post creado", "data": new_post}


@app.put("/posts/{post_id}")
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:
            playload = data.model_dump(exclude_unset=True) # {"title": "Ricardo", "content": None}
            if "title" in playload: post["title"] = playload["title"]
            if "content" in playload: post["content"] = playload["content"]
            return {"message": "Post actualizado", "data": post}
    
    raise HTTPException(status_code=404, detail="Post no encontrado")


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return
    raise HTTPException(status_code=404,detail="Post no encontrado")