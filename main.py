
from fastapi import FastAPI

app = FastAPI(title="Mini Blog")

@app.get("/")
def home():
    return {'message': 'Bienvenidos a Mini Blog por Devtalles'}