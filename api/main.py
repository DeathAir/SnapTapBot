import uvicorn
from fastapi import FastAPI

from api.routes import system, tickets, users, admin, superadmin

app = FastAPI(title="SnapTapApi",
              description="API для SnapTapBot",
              version="1.0.0")

app.include_router(system.router)
app.include_router(tickets.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(superadmin.router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
