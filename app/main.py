from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
from app.schemas import EmailRequest, BulkEmailRequest, EmailResponse
from app.services.validator import EmailValidator
from app.services.cache import CacheManager

app = FastAPI(
    title="Professional Email Validator API",
    description="API avanzada para validación de emails con verificación SMTP",
    version="2.0"
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

def get_validator():
    return EmailValidator(cache)

@app.on_event("shutdown")
async def shutdown_event():
    await cache.close()

@app.post("/validate", response_model=EmailResponse)
async def validate_email(
    request: EmailRequest,
    validator: EmailValidator = Depends(get_validator)
):
    return await validator.validate(request.email)

@app.post("/bulk-validate", response_model=List[EmailResponse])
async def bulk_validate(
    request: BulkEmailRequest,
    validator: EmailValidator = Depends(get_validator)
):
    if len(request.emails) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 emails per request")
    
    return [await validator.validate(email) for email in request.emails]

@app.post("/premium-validate", response_model=EmailResponse)
async def premium_validate(
    request: EmailRequest,
    validator: EmailValidator = Depends(get_validator)
):
    return await validator.validate(request.email, smtp_check=True)

@app.get("/health")
async def health_check():
    try:
        redis_ok = await cache.ping()
        return {
            "status": "OK",
            "redis": "connected" if redis_ok else "disconnected",
            "version": "2.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))