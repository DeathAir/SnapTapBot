from fastapi import APIRouter


router = APIRouter(tags=["system"])

@router.get("/health")
async def system():
    return {"status": "ok"}
