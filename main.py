from fastapi import FastAPI

from routers import student

app = FastAPI()
app.include_router(student.router)

