from fastapi import APIRouter

router = APIRouter(prefix="/ia", tags=["ia"])

@router.get("/")
def ia_status():
    return {"message": "IA endpoint listo"}