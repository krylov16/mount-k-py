from fastapi import FastAPI
from fastapi.responses import HTMLResponse
 
app = FastAPI()
 
@app.get("/")
def read_root():
    html_content = "<h2>Hi, man! What's up?</h2>"
    return HTMLResponse(content=html_content)

 
@app.get("/about")
def read_root():
    html_content = "<h2>My name is Konstantin</h2>"
    return HTMLResponse(content=html_content)