"""Health check endpoints"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil

router = APIRouter(prefix="", tags=["Health"])


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "RAG System API",
            "version": "1.0.0",
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/ready")
async def readiness_check():
    """Readiness check - system is ready to serve requests"""
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/health/live")
async def liveness_check():
    """Liveness check - service is alive"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }
