import uvicorn
from fastapi import FastAPI, Depends

from api.dependencies import verify_api_key
from api.routes import system, tickets, users, admin, superadmin

app = FastAPI(
    title="SnapTapApi",
    description="API для SnapTapBot",
    version="1.0.0",
)

# /health должен быть открыт — не защищаем
app.include_router(system.router)

# Все остальные — только с API-ключом
app.include_router(tickets.router,    dependencies=[Depends(verify_api_key)])
app.include_router(users.router,      dependencies=[Depends(verify_api_key)])
app.include_router(admin.router,      dependencies=[Depends(verify_api_key)])
app.include_router(superadmin.router, dependencies=[Depends(verify_api_key)])

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)