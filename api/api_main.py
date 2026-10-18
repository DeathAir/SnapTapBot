import uvicorn
from fastapi import FastAPI, Depends

from api.dependencies import verify_api_key
from api.routes import system, tickets, users, admin, superadmin

app = FastAPI(
    title="SnapTapApi",
    description="API для SnapTapBot",
    version="1.0.0",
)


app.include_router(system.router)


app.include_router(tickets.router,    dependencies=[Depends(verify_api_key)])
app.include_router(users.router,      dependencies=[Depends(verify_api_key)])
app.include_router(admin.router,      dependencies=[Depends(verify_api_key)])
app.include_router(superadmin.router, dependencies=[Depends(verify_api_key)])

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)