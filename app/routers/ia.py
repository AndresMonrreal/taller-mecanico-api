from fastapi import APIRouter
from pydantic import BaseModel
import os
import httpx
from fastapi import HTTPException
from app.core.config import settings

router = APIRouter(prefix="/ia", tags=["ia"])


class EstimarRequest(BaseModel):
    """Schema para solicitar estimación de horas a la IA."""
    descripcion: str   # Descripción del servicio o reparación
    vehiculo: str      # Datos del vehículo (marca, modelo, año)


@router.post("/estimar")
def estimar_horas(req: EstimarRequest):
    """
    Estima horas de trabajo usando OpenAI GPT-4o-mini.
    Envía la descripción del servicio y datos del vehículo a la IA
    y retorna una estimación con recomendaciones adicionales.
    """
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
    print(f"OpenAI response: {data}")

    if "choices" not in data:
        raise HTTPException(status_code=500, detail=data.get("error", {}).get("message", "Error OpenAI"))

    return {"estimacion": data["choices"][0]["message"]["content"]}