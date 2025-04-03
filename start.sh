#!/bin/bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}  # Usa 8000 si PORT no existe