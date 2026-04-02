from fastapi import FastAPI
from code import main   # имя твоего файла!

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API работает"}

@app.get("/run")
def run_simulation():
    return main()
# uvicorn api:app --reload