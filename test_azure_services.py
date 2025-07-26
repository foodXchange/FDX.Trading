"""
Test Azure Services (Storage and OpenAI)
"""
import os
import asyncio
from io import BytesIO

# Test configuration
print("Testing Azure Services Configuration...\n")

# Check environment variables
storage_conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
openai_key = os.getenv("AZURE_OPENAI_API_KEY", "")
openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")

print("1. Environment Variables:")
print(f"   Storage Connection: {'✅ Set' if storage_conn else '❌ Not set'}")
print(f"   OpenAI Key: {'✅ Set' if openai_key else '❌ Not set'}")
print(f"   OpenAI Endpoint: {'✅ Set' if openai_endpoint else '❌ Not set'}")

async def test_blob_storage():
    """Test Blob Storage"""
    print("\n2. Testing Blob Storage...")
    
    try:
        from app.services.blob_storage_service import blob_storage_service
        
        # Test upload
        test_content = b"Test quote content for FoodXchange"
        test_file = BytesIO(test_content)
        
        result = await blob_storage_service.upload_file(
            file=test_file,
            filename="test_quote.pdf",
            container_type="quotes",
            company_id=1,
            metadata={"test": "true"}
        )
        
        if result:
            print("   ✅ Blob Storage working!")
            print(f"   📎 Uploaded to: {result['blob_name']}")
            print(f"   🔗 URL: {result['sas_url'][:50]}...")
        else:
            print("   ❌ Blob Storage upload failed")
            
    except Exception as e:
        print(f"   ❌ Blob Storage error: {str(e)}")

async def test_openai():
    """Test OpenAI"""
    print("\n3. Testing OpenAI Service...")
    
    try:
        from app.services.openai_service import openai_service
        
        # Test email parsing
        test_email = """
        Subject: RFQ - Extra Virgin Olive Oil
        
        We need 500 liters of extra virgin olive oil.
        Delivery by end of month.
        Please send best price.
        """
        
        result = await openai_service.parse_email_for_rfq(test_email)
        
        if result:
            print("   ✅ OpenAI working!")
            print(f"   📧 Detected type: {result.get('detected_type', 'unknown')}")
            print(f"   📦 Products found: {len(result.get('products', []))}")
        else:
            print("   ❌ OpenAI parsing failed")
            
    except Exception as e:
        print(f"   ❌ OpenAI error: {str(e)}")

async def test_rfq_generation():
    """Test RFQ description generation"""
    print("\n4. Testing RFQ Generation...")
    
    try:
        from app.services.openai_service import openai_service
        
        description = await openai_service.generate_rfq_description(
            "Premium Olive Oil",
            "For high-end restaurant chain"
        )
        
        if description:
            print("   ✅ RFQ Generation working!")
            print(f"   📝 Generated: {description[:100]}...")
        else:
            print("   ❌ RFQ Generation failed")
            
    except Exception as e:
        print(f"   ❌ RFQ Generation error: {str(e)}")

# Run tests
async def main():
    await test_blob_storage()
    await test_openai()
    await test_rfq_generation()
    
    print("\n✅ Testing complete!")
    print("\nNext steps:")
    print("1. If any services failed, check your .env file")
    print("2. Make sure you've deployed a model in OpenAI")
    print("3. Install required packages: pip install azure-storage-blob openai")

if __name__ == "__main__":
    asyncio.run(main())