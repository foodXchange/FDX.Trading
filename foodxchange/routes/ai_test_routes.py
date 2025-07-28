"""AI Test Routes for Azure OpenAI Integration"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from foodxchange.services.openai_service import openai_service

router = APIRouter(prefix="/api/ai-test", tags=["AI Test"])

class EmailTestRequest(BaseModel):
    email_content: str

class ProductTestRequest(BaseModel):
    product_name: str
    context: str = None

@router.get("/status")
async def ai_status():
    """Check AI service status"""
    return {
        "openai_available": openai_service.client is not None,
        "deployment_name": openai_service.deployment_name if openai_service.client else None,
        "endpoint": openai_service.settings.azure_openai_endpoint if openai_service.client else None
    }

@router.post("/parse-email")
async def test_parse_email(request: EmailTestRequest):
    """Test email parsing"""
    try:
        result = await openai_service.parse_email_for_rfq(request.email_content)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-rfq")
async def test_generate_rfq(request: ProductTestRequest):
    """Test RFQ generation"""
    try:
        description = await openai_service.generate_rfq_description(
            request.product_name, 
            request.context
        )
        return {"success": True, "description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))