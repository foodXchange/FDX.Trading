from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/rfq-form", response_class=HTMLResponse)
async def rfq_form_page(request: Request):
    """Render the rfq-form page"""
    return templates.TemplateResponse(
        "v0-components/rfq-form.html",
        {"request": request, "title": "rfq-form".replace('-', ' ').title()}
    )

@router.post("/api/rfq-form")
async def rfq-form_api():
    """API endpoint for rfq-form functionality"""
    try:
        # Add your API logic here
        return {"status": "success", "message": "rfq-form processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
