from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI()

# Set up templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "name": "Your Name"}
    )

@app.get("/{name}")
async def greet(request: Request, name: str):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "name": name}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
