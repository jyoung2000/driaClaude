"""
Web interface routes for driaClaude
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Setup templates
template_dir = Path(__file__).parent.parent.parent / "templates"
template_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(template_dir))

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "driaClaude - TTS Web Service"}
    )

@router.get("/voices", response_class=HTMLResponse)
async def voices_page(request: Request):
    """Voice management page"""
    return templates.TemplateResponse(
        "voices.html",
        {"request": request, "title": "Voice Management - driaClaude"}
    )

@router.get("/api-docs", response_class=HTMLResponse)
async def api_docs_page(request: Request):
    """API documentation page"""
    return templates.TemplateResponse(
        "api-docs.html",
        {"request": request, "title": "API Documentation - driaClaude"}
    )