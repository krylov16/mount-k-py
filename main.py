from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
 
app = FastAPI()
 
@app.get("/")
def root():
    return FileResponse("templates/index.html")

 
@app.get("/about")
def about():
    html_content = "<h2>My name is Konstantin</h2>"
    return HTMLResponse(content=html_content)

 
@app.get("/getdata/{id}")
def getdata(id):
    return {"id": id}

@app.post("/user")
def user(data = Body()):
    name = data["name"]
    age = data["age"]
    return {"message": f"{name}, ваш возраст - {age}!!!"}