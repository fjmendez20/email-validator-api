from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
from app.schemas import EmailRequest, BulkEmailRequest, EmailResponse
from app.services.validator import EmailValidator
from app.services.cache import CacheManager
import ipaddress

app = FastAPI(
    title="Professional Email Validator API",
    description="API avanzada para validación de emails con verificación SMTP",
    version="2.1"  # Versión actualizada
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialización de dependencias
cache = CacheManager()

# Límites por endpoint (peticiones por día)
RATE_LIMITS = {
    "/validate": 100,
    "/bulk-validate": 10,
    "/premium-validate": 5
}

async def check_rate_limit(request: Request, endpoint: str):
    # Obtiene IP del cliente (soporta proxies)
    client_ip = request.client.host
    
    # Clave única para el contador en Redis
    redis_key = f"rate_limit:{endpoint}:{client_ip}"
    
    # Incrementa el contador
    current = await cache.incr(redis_key)
    
    # Si es la primera vez, establece expiración (24 horas)
    if current == 1:
        await cache.expire(redis_key, 86400)
    
    # Verifica límite
    if current > RATE_LIMITS[endpoint]:
        raise HTTPException(
            status_code=429,
            detail=f"Límite excedido. Máximo {RATE_LIMITS[endpoint]} peticiones/día. Actualiza a premium."
        )

def get_validator():
    return EmailValidator(cache)

@app.on_event("shutdown")
async def shutdown_event():
    await cache.close()

@app.post("/validate", response_model=EmailResponse)
async def validate_email(
    request: Request,  # Añadido para obtener IP
    email_request: EmailRequest,
    validator: EmailValidator = Depends(get_validator)
):
    await check_rate_limit(request, "/validate")
    return await validator.validate(email_request.email)

@app.post("/bulk-validate", response_model=List[EmailResponse])
async def bulk_validate(
    request: Request,  # Añadido
    email_request: BulkEmailRequest,
    validator: EmailValidator = Depends(get_validator)
):
    await check_rate_limit(request, "/bulk-validate")
    if len(email_request.emails) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 emails per request")
    return [await validator.validate(email) for email in email_request.emails]

@app.post("/premium-validate", response_model=EmailResponse)
async def premium_validate(
    request: Request,  # Añadido
    email_request: EmailRequest,
    validator: EmailValidator = Depends(get_validator)
):
    await check_rate_limit(request, "/premium-validate")
    return await validator.validate(email_request.email, smtp_check=True)

@app.get("/health")
async def health_check():
    try:
        redis_ok = await cache.ping()
        return {
            "status": "OK",
            "redis": "connected" if redis_ok else "disconnected",
            "version": "2.1"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))