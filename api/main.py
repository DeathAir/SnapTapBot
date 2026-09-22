from fastapi import FastAPI

from api.routes import system

app = FastAPI(title="SnapTapApi",
              description="API для SnapTapBot",
              version="1.0.0")

app.include_router(system.router)

