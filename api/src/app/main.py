"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import (
    health_router,
    webhooks_router,
    investigations_router,
    services_router,
    remediation_router,
    evals_router,
    feedback_router,
    metrics_router,
)
from .config import API_BASE_URL, DEBUG, ALLOWED_ORIGINS

app = FastAPI(
    title="SherLock SRE Platform API",
    description="AI-powered incident investigation and remediation platform — Part 2 API Layer",
    version="0.1.0",
    debug=DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware — configure ALLOWED_ORIGINS env var in production
# e.g. ALLOWED_ORIGINS="https://your-app.streamlit.app,https://your-dashboard.vercel.app"
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOWED_ORIGINS != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(health_router)
app.include_router(webhooks_router)
app.include_router(investigations_router)
app.include_router(services_router)
app.include_router(remediation_router)
app.include_router(evals_router)
app.include_router(feedback_router)
app.include_router(metrics_router)


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API directory."""
    return {
        "name": "SherLock SRE Platform API",
        "version": "0.1.0",
        "description": "Autonomous SRE Platform — Part 2 API & Dashboard Layer",
        "endpoints": {
            "docs": f"{API_BASE_URL}/docs",
            "health": f"{API_BASE_URL}/health",
            "investigations": f"{API_BASE_URL}/investigations",
            "services": f"{API_BASE_URL}/services",
            "remediation_catalog": f"{API_BASE_URL}/remediation/catalog",
            "webhooks": f"{API_BASE_URL}/webhooks/alert",
            "evals": f"{API_BASE_URL}/evals/summary",
            "metrics": f"{API_BASE_URL}/metrics",
            "feedback": f"{API_BASE_URL}/feedback",
        }
    }
