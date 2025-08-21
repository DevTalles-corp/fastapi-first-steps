
from fastapi import FastAPI, Query

app = FastAPI(title="Mini Blog")

BLOG_POST = [
    {"id": 1, "title": "Hola desde FastAPI", "Content":"Mi primer post con FastAPI"},
    {"id": 2, "title": "Mi segundo Post con FastAPI", "Content":"Mi segundo post con FastAPI blablabla"},
    {"id": 3, "title": "Django vs FastAPI", "Content":"FastAPI es más rápido por x razones"},
]


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