from fastapi import APIRouter
from pydantic import BaseModel
import os
import httpx
from fastapi import HTTPException
from app.core.config import settings

router = APIRouter(prefix="/ia", tags=["ia"])

class EstimarRequest(BaseModel):
    descripcion: str
    vehiculo: str

@router.post("/estimar")
def estimar_horas(req: EstimarRequest):
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "max_tokens": 500,
            "messages": [{
                "role": "user",
                "content": f"Eres un experto mecánico. Para un {req.vehiculo} con el servicio: {req.descripcion}. Estima cuántas horas tomará y qué revisiones adicionales recomiendas. Sé conciso."
            }]
        }
    )
    
    data = response.json()
    print(f"OpenAI response: {data}")  # ← agrega esto
    
    if "choices" not in data:
        raise HTTPException(status_code=500, detail=data.get("error", {}).get("message", "Error OpenAI"))
    
    return {"estimacion": data["choices"][0]["message"]["content"]}