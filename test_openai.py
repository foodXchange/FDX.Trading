"""Test Azure OpenAI Integration"""
import asyncio
from app.services.openai_service import openai_service

async def test_openai():
    # Test 1: Email parsing
    print("Testing email parsing...")
    email_content = """
    Dear Supplier,
    
    We need to order 500 kg of premium olive oil from Greece. 
    We require organic certification and need delivery by December 15th.
    Our budget is around $3000-$4000.
    
    Please send your best quote.
    
    Best regards,
    John from FoodXchange
    """
    
    result = await openai_service.parse_email_for_rfq(email_content)
    print("Email parsing result:")
    print(result)
    print("\n" + "="*50 + "\n")
    
    # Test 2: RFQ description generation
    print("Testing RFQ description generation...")
    description = await openai_service.generate_rfq_description(
        "Organic Olive Oil", 
        "Need 500kg for restaurant chain"
    )
    print("Generated RFQ description:")
    print(description)
    print("\n" + "="*50 + "\n")
    
    # Test 3: Quote analysis
    print("Testing quote analysis...")
    quotes = [
        {"id": "1", "supplier": "Greek Farms", "total_price": 3200, "delivery_time": "10 days"},
        {"id": "2", "supplier": "Med Suppliers", "total_price": 3500, "delivery_time": "7 days"},
        {"id": "3", "supplier": "Olive Co", "total_price": 2900, "delivery_time": "14 days"}
    ]
    
    analysis = await openai_service.analyze_quote_competitiveness(quotes)
    print("Quote analysis result:")
    print(analysis)

if __name__ == "__main__":
    asyncio.run(test_openai())