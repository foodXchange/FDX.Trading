"""
CSV Data Import Agent - Handles bulk import of supplier data from CSV files
Supports multiple formats and languages with automatic translation
"""
import asyncio
import logging
import csv
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import chardet
from io import StringIO

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.supplier import Supplier
from app.models.product import Product
from app.config import get_settings

# Azure translation service
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential

settings = get_settings()
logger = logging.getLogger(__name__)


class CSVDataImportAgent:
    """
    Intelligent agent for importing supplier and product data from CSV files
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Azure Translation setup
        self.translator = TextTranslationClient(
            endpoint=settings.AZURE_TRANSLATOR_ENDPOINT,
            credential=AzureKeyCredential(settings.AZURE_TRANSLATOR_KEY)
        )
        
        # Common column mappings for different languages
        self.column_mappings = {
            # English
            'product': ['product', 'item', 'name', 'product_name', 'item_name'],
            'price': ['price', 'cost', 'rate', 'unit_price', 'price_per_unit'],
            'quantity': ['quantity', 'qty', 'amount', 'volume'],
            'unit': ['unit', 'uom', 'unit_of_measure', 'measurement'],
            'supplier': ['supplier', 'vendor', 'company', 'supplier_name'],
            'category': ['category', 'type', 'classification', 'product_category'],
            
            # Spanish
            'producto': ['producto', 'artículo', 'nombre'],
            'precio': ['precio', 'costo', 'tarifa'],
            'cantidad': ['cantidad', 'volumen'],
            'unidad': ['unidad', 'medida'],
            'proveedor': ['proveedor', 'vendedor', 'empresa'],
            
            # French
            'produit': ['produit', 'article', 'nom'],
            'prix': ['prix', 'coût', 'tarif'],
            'quantité': ['quantité', 'volume'],
            'unité': ['unité', 'mesure'],
            'fournisseur': ['fournisseur', 'vendeur', 'société'],
            
            # Italian
            'prodotto': ['prodotto', 'articolo', 'nome'],
            'prezzo': ['prezzo', 'costo', 'tariffa'],
            'quantità': ['quantità', 'volume'],
            'unità': ['unità', 'misura'],
            'fornitore': ['fornitore', 'venditore', 'azienda']
        }
        
    async def import_csv_file(self, file_path: str, supplier_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Import data from a CSV file
        """
        try:
            logger.info(f"Starting CSV import from: {file_path}")
            
            # Detect file encoding
            encoding = self._detect_encoding(file_path)
            
            # Read CSV with pandas for better handling
            df = pd.read_csv(file_path, encoding=encoding)
            
            # Detect language from column names
            detected_language = await self._detect_csv_language(df.columns.tolist())
            
            # Map columns to standard names
            column_mapping = self._map_columns(df.columns.tolist(), detected_language)
            
            # Process data
            import_results = await self._process_dataframe(df, column_mapping, supplier_id, detected_language)
            
            return {
                "file": file_path,
                "encoding": encoding,
                "detected_language": detected_language,
                "total_rows": len(df),
                "products_imported": import_results['products_imported'],
                "suppliers_created": import_results['suppliers_created'],
                "errors": import_results['errors'],
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"CSV import error: {str(e)}")
            return {
                "file": file_path,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding using chardet
        """
        with open(file_path, 'rb') as file:
            raw_data = file.read(10000)  # Read first 10KB
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    
    async def _detect_csv_language(self, columns: List[str]) -> str:
        """
        Detect language from column names
        """
        # Join column names for language detection
        text_sample = ' '.join(columns)
        
        try:
            response = self.translator.detect_language(
                body=[{"text": text_sample}]
            )
            
            if response and response[0].language:
                return response[0].language
        except:
            pass
        
        # Fallback: check for known column names
        for col in columns:
            col_lower = col.lower()
            if any(spanish in col_lower for spanish in ['producto', 'precio', 'cantidad']):
                return 'es'
            elif any(french in col_lower for french in ['produit', 'prix', 'quantité']):
                return 'fr'
            elif any(italian in col_lower for italian in ['prodotto', 'prezzo', 'quantità']):
                return 'it'
        
        return 'en'  # Default to English
    
    def _map_columns(self, columns: List[str], language: str) -> Dict[str, str]:
        """
        Map CSV columns to standard field names
        """
        mapping = {}
        columns_lower = [col.lower() for col in columns]
        
        # Map product name
        for col, col_lower in zip(columns, columns_lower):
            # Product column
            if any(keyword in col_lower for keyword in self.column_mappings.get('product', [])):
                mapping['product_name'] = col
            elif language != 'en' and any(keyword in col_lower for keyword in self.column_mappings.get('producto', [])):
                mapping['product_name'] = col
            elif language != 'en' and any(keyword in col_lower for keyword in self.column_mappings.get('produit', [])):
                mapping['product_name'] = col
            elif language != 'en' and any(keyword in col_lower for keyword in self.column_mappings.get('prodotto', [])):
                mapping['product_name'] = col
            
            # Price column
            elif any(keyword in col_lower for keyword in self.column_mappings.get('price', [])):
                mapping['price'] = col
            elif language != 'en' and any(keyword in col_lower for keyword in self.column_mappings.get('precio', [])):
                mapping['price'] = col
            elif language != 'en' and any(keyword in col_lower for keyword in self.column_mappings.get('prix', [])):
                mapping['price'] = col
            elif language != 'en' and any(keyword in col_lower for keyword in self.column_mappings.get('prezzo', [])):
                mapping['price'] = col
            
            # Quantity column
            elif any(keyword in col_lower for keyword in self.column_mappings.get('quantity', [])):
                mapping['quantity'] = col
            
            # Unit column
            elif any(keyword in col_lower for keyword in self.column_mappings.get('unit', [])):
                mapping['unit'] = col
            
            # Supplier column
            elif any(keyword in col_lower for keyword in self.column_mappings.get('supplier', [])):
                mapping['supplier_name'] = col
            
            # Category column
            elif any(keyword in col_lower for keyword in self.column_mappings.get('category', [])):
                mapping['category'] = col
        
        return mapping
    
    async def _process_dataframe(self, df: pd.DataFrame, column_mapping: Dict[str, str], 
                                supplier_id: Optional[int], language: str) -> Dict[str, Any]:
        """
        Process the dataframe and import data
        """
        results = {
            'products_imported': 0,
            'suppliers_created': 0,
            'errors': []
        }
        
        # Process in batches for better performance
        batch_size = 100
        total_rows = len(df)
        
        for start_idx in range(0, total_rows, batch_size):
            end_idx = min(start_idx + batch_size, total_rows)
            batch_df = df.iloc[start_idx:end_idx]
            
            # Process each row in the batch
            for idx, row in batch_df.iterrows():
                try:
                    # Extract product data
                    product_data = await self._extract_product_data(row, column_mapping, language)
                    
                    if not product_data['name']:
                        continue
                    
                    # Handle supplier
                    if not supplier_id and 'supplier_name' in column_mapping:
                        supplier_name = row[column_mapping['supplier_name']]
                        supplier_id = await self._get_or_create_supplier(supplier_name)
                        if supplier_id and supplier_name:
                            results['suppliers_created'] += 1
                    
                    # Save product
                    if supplier_id:
                        saved = await self._save_product(supplier_id, product_data)
                        if saved:
                            results['products_imported'] += 1
                    
                except Exception as e:
                    results['errors'].append({
                        'row': idx + 2,  # Excel row number (header is row 1)
                        'error': str(e),
                        'data': row.to_dict()
                    })
            
            # Add delay between batches (respecting rate limits)
            await asyncio.sleep(1)
            
            # Log progress
            logger.info(f"Processed {end_idx}/{total_rows} rows")
        
        return results
    
    async def _extract_product_data(self, row: pd.Series, column_mapping: Dict[str, str], 
                                   language: str) -> Dict[str, Any]:
        """
        Extract and translate product data from a row
        """
        data = {
            'name': None,
            'original_name': None,
            'price': None,
            'unit': None,
            'quantity': None,
            'category': None,
            'description': None
        }
        
        # Extract product name
        if 'product_name' in column_mapping:
            original_name = str(row[column_mapping['product_name']])
            data['original_name'] = original_name
            
            # Translate if needed
            if language != 'en' and original_name:
                data['name'] = await self._translate_text(original_name, language)
            else:
                data['name'] = original_name
        
        # Extract price
        if 'price' in column_mapping:
            try:
                price_val = row[column_mapping['price']]
                # Clean price string (remove currency symbols, spaces, etc.)
                price_str = str(price_val).replace('$', '').replace('€', '').replace('£', '')
                price_str = price_str.replace(',', '').strip()
                data['price'] = float(price_str)
            except:
                data['price'] = None
        
        # Extract unit
        if 'unit' in column_mapping:
            data['unit'] = str(row[column_mapping['unit']])
        
        # Extract quantity
        if 'quantity' in column_mapping:
            try:
                data['quantity'] = float(row[column_mapping['quantity']])
            except:
                data['quantity'] = None
        
        # Extract category
        if 'category' in column_mapping:
            category = str(row[column_mapping['category']])
            if language != 'en' and category:
                data['category'] = await self._translate_text(category, language)
            else:
                data['category'] = category
        
        return data
    
    async def _translate_text(self, text: str, source_language: str) -> str:
        """
        Translate text to English
        """
        if not text or source_language == 'en':
            return text
            
        try:
            response = self.translator.translate(
                body=[{"text": text}],
                to_language=["en"],
                from_language=source_language
            )
            
            if response and response[0].translations:
                return response[0].translations[0].text
                
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
        
        return text  # Return original if translation fails
    
    async def _get_or_create_supplier(self, supplier_name: str) -> Optional[int]:
        """
        Get existing supplier or create new one
        """
        if not supplier_name:
            return None
            
        # Check if supplier exists
        supplier = self.db.query(Supplier).filter(
            Supplier.name == supplier_name
        ).first()
        
        if supplier:
            return supplier.id
        
        # Create new supplier
        try:
            new_supplier = Supplier(
                name=supplier_name,
                email=f"contact@{supplier_name.lower().replace(' ', '')}.com",  # Placeholder
                is_active=True,
                is_verified=False,  # Needs verification
                created_at=datetime.utcnow()
            )
            self.db.add(new_supplier)
            self.db.commit()
            self.db.refresh(new_supplier)
            
            logger.info(f"Created new supplier: {supplier_name}")
            return new_supplier.id
            
        except Exception as e:
            logger.error(f"Error creating supplier: {str(e)}")
            self.db.rollback()
            return None
    
    async def _save_product(self, supplier_id: int, product_data: Dict[str, Any]) -> bool:
        """
        Save product to database
        """
        try:
            # Check if product exists
            existing = self.db.query(Product).filter(
                Product.supplier_id == supplier_id,
                Product.name == product_data['name']
            ).first()
            
            if existing:
                # Update existing product
                if product_data['price']:
                    existing.price = product_data['price']
                if product_data['unit']:
                    existing.unit = product_data['unit']
                if product_data['category']:
                    existing.category = product_data['category']
                existing.last_updated = datetime.utcnow()
            else:
                # Create new product
                new_product = Product(
                    supplier_id=supplier_id,
                    name=product_data['name'],
                    original_name=product_data['original_name'],
                    price=product_data['price'],
                    unit=product_data['unit'],
                    category=product_data['category'],
                    quantity_available=product_data['quantity'],
                    created_at=datetime.utcnow()
                )
                self.db.add(new_product)
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving product: {str(e)}")
            self.db.rollback()
            return False
    
    async def process_multiple_files(self, file_paths: List[str], 
                                   supplier_mapping: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Process multiple CSV files
        """
        results = {
            'files_processed': 0,
            'total_products': 0,
            'total_suppliers': 0,
            'file_results': []
        }
        
        for file_path in file_paths:
            # Determine supplier ID from mapping or filename
            supplier_id = None
            if supplier_mapping:
                file_name = Path(file_path).stem
                supplier_id = supplier_mapping.get(file_name)
            
            # Process file
            file_result = await self.import_csv_file(file_path, supplier_id)
            results['file_results'].append(file_result)
            
            if 'error' not in file_result:
                results['files_processed'] += 1
                results['total_products'] += file_result['products_imported']
                results['total_suppliers'] += file_result['suppliers_created']
            
            # Delay between files
            await asyncio.sleep(7)  # 7 seconds delay as required
        
        return results


class ExcelDataImportAgent:
    """
    Agent for importing Excel files (extension of CSV agent)
    """
    
    def __init__(self, db_session: Session):
        self.csv_agent = CSVDataImportAgent(db_session)
        
    async def import_excel_file(self, file_path: str, sheet_name: Optional[str] = None,
                               supplier_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Import data from an Excel file
        """
        try:
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                # Read first sheet by default
                df = pd.read_excel(file_path)
            
            # Convert to CSV in memory and process
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            # Create temporary CSV file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
                tmp_file.write(csv_buffer.getvalue())
                tmp_path = tmp_file.name
            
            # Process using CSV agent
            result = await self.csv_agent.import_csv_file(tmp_path, supplier_id)
            
            # Clean up
            Path(tmp_path).unlink()
            
            result['original_file'] = file_path
            result['file_type'] = 'excel'
            
            return result
            
        except Exception as e:
            logger.error(f"Excel import error: {str(e)}")
            return {
                "file": file_path,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }