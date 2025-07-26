# Azure Blob Storage Setup Guide for FoodXchange

## 🚀 Quick Setup (5 minutes)

### Option 1: Azure Portal (Easiest)

1. Go to [Azure Portal](https://portal.azure.com)
2. Click **"+ Create a resource"**
3. Search for **"Storage account"**
4. Click **Create**

### Configuration:
```
Resource Group: foodxchange-rg
Storage account name: foodxchangestorage
Region: France Central (same as other resources)
Performance: Standard
Redundancy: LRS (Locally-redundant storage) - cheapest
```

5. Click **Review + Create** → **Create**

### Option 2: Azure CLI (Fastest)

```bash
# Create storage account
az storage account create \
  --name foodxchangestorage \
  --resource-group foodxchange-rg \
  --location francecentral \
  --sku Standard_LRS \
  --kind StorageV2

# Get connection string
az storage account show-connection-string \
  --name foodxchangestorage \
  --resource-group foodxchange-rg \
  --query connectionString -o tsv
```

## 🔑 Get Your Connection String

1. Go to your Storage Account in Azure Portal
2. Click **Access keys** in the left menu
3. Copy **Connection string** from key1

It looks like:
```
DefaultEndpointsProtocol=https;AccountName=foodxchangestorage;AccountKey=...;EndpointSuffix=core.windows.net
```

## 📝 Update Your .env File

Add this line to your `.env`:
```env
# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=foodxchangestorage;AccountKey=YOUR_KEY_HERE;EndpointSuffix=core.windows.net
```

## 📦 Install Required Package

```bash
pip install azure-storage-blob
```

## 🧪 Test the Storage

Create `test_blob_storage.py`:

```python
import asyncio
from app.services.blob_storage_service import blob_storage_service

async def test_storage():
    # Test file upload
    test_content = b"This is a test PDF content"
    
    # Simulate file upload
    from io import BytesIO
    file = BytesIO(test_content)
    
    result = await blob_storage_service.upload_file(
        file=file,
        filename="test_quote.pdf",
        container_type="quotes",
        company_id=1,
        metadata={"supplier": "Test Supplier", "amount": "1000"}
    )
    
    if result:
        print(f"✅ Upload successful!")
        print(f"📎 File URL: {result['url']}")
        print(f"🔐 SAS URL (24h): {result['sas_url']}")
    else:
        print("❌ Upload failed")

# Run test
asyncio.run(test_storage())
```

## 💾 What Gets Stored Where

The service automatically creates 5 containers:

| Container | Purpose | File Types |
|-----------|---------|------------|
| `quotes` | Supplier quotes | PDF, DOC, XLS |
| `orders` | Purchase orders | PDF, DOC |
| `products` | Product images/specs | JPG, PNG, PDF |
| `suppliers` | Certificates, licenses | PDF, JPG, DOC |
| `email-attachments` | Email attachments | All types |

## 🔧 Integration Examples

### 1. Upload Quote PDF

```python
@router.post("/quotes/{quote_id}/upload")
async def upload_quote_document(
    quote_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Save to blob storage
    result = await blob_storage_service.upload_file(
        file=file.file,
        filename=file.filename,
        container_type="quotes",
        company_id=current_user.company_id,
        metadata={"quote_id": str(quote_id)}
    )
    
    if result:
        # Save URL to database
        quote = db.query(Quote).filter_by(id=quote_id).first()
        quote.document_url = result["url"]
        db.commit()
        
        return {"message": "File uploaded", "url": result["sas_url"]}
```

### 2. Store Email Attachments

```python
# In email processing
for attachment in email.attachments:
    result = await blob_storage_service.upload_file(
        file=attachment.content,
        filename=attachment.filename,
        container_type="emails",
        company_id=company_id,
        metadata={"email_id": str(email.id)}
    )
```

### 3. Product Images

```python
# Upload product image
result = await blob_storage_service.upload_file(
    file=image_file,
    filename="olive_oil.jpg",
    container_type="products",
    company_id=company_id,
    metadata={"product_name": "Extra Virgin Olive Oil"}
)
```

## 💰 Cost Breakdown

| Storage Amount | Monthly Cost |
|----------------|--------------|
| 0-5 GB | ~$0.10 |
| 5-50 GB | ~$1.00 |
| 50-100 GB | ~$2.00 |

**Transactions**: $0.0004 per 10,000 operations

**Bandwidth**: 
- Upload: Free
- Download: First 5GB/month free, then $0.087/GB

## 🔒 Security Features

1. **All files are private** by default
2. **SAS URLs** for temporary access (expire in 24 hours)
3. **Organized by company** for multi-tenant isolation
4. **File type validation** to prevent malicious uploads

## 🚨 Important Notes

1. **File Size Limit**: Default 10MB per file (configurable)
2. **Allowed Extensions**: Validated per container type
3. **Automatic Organization**: Files stored as `company_123/timestamp_filename`
4. **Metadata**: Store searchable information with each file

## 📈 Next Steps

1. **Test upload** with the test script
2. **Add file upload UI** to quotes/orders pages
3. **Implement cleanup job** for old files
4. **Add virus scanning** (Azure Defender optional)

## 🆘 Troubleshooting

**"Container not found"**: Wait 1 minute after storage account creation

**"Authentication failed"**: Check connection string in .env

**"File too large"**: Default limit is 10MB, increase in `validate_file_size()`

The storage is now ready to handle all your document needs! 📂