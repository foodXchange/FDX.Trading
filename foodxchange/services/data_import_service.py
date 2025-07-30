"""
Data Import Service for CSV/Excel file processing
Handles bulk import of buyers and suppliers data
"""

import pandas as pd
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class DataImportService:
    """Service for importing CSV and Excel data"""
    
    BUYER_REQUIRED_COLUMNS = ['name', 'email']
    BUYER_OPTIONAL_COLUMNS = ['company_name', 'phone', 'country', 'city', 'address', 
                              'industry', 'company_size', 'payment_terms']
    
    SUPPLIER_REQUIRED_COLUMNS = ['name', 'email']
    SUPPLIER_OPTIONAL_COLUMNS = ['company_name', 'phone', 'country', 'city', 'address',
                                 'industry', 'company_size', 'certifications', 
                                 'payment_terms', 'minimum_order']
    
    def __init__(self):
        """Initialize the data import service"""
        self.supported_formats = ['.csv', '.xlsx', '.xls']
        
    def read_file(self, file_path: str) -> pd.DataFrame:
        """
        Read CSV or Excel file into DataFrame
        
        Args:
            file_path: Path to the file
            
        Returns:
            DataFrame with the file contents
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                # Try different encodings
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
                for encoding in encodings:
                    try:
                        return pd.read_csv(file_path, encoding=encoding)
                    except UnicodeDecodeError:
                        continue
                raise ValueError(f"Unable to read CSV file with any encoding")
                
            elif file_ext in ['.xlsx', '.xls']:
                return pd.read_excel(file_path, engine='openpyxl')
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
                
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise
    
    def validate_columns(self, df: pd.DataFrame, data_type: str) -> Tuple[bool, List[str]]:
        """
        Validate that required columns are present
        
        Args:
            df: DataFrame to validate
            data_type: 'buyers' or 'suppliers'
            
        Returns:
            Tuple of (is_valid, missing_columns)
        """
        if data_type == 'buyers':
            required_cols = self.BUYER_REQUIRED_COLUMNS
        elif data_type == 'suppliers':
            required_cols = self.SUPPLIER_REQUIRED_COLUMNS
        else:
            raise ValueError(f"Invalid data type: {data_type}")
        
        # Convert column names to lowercase for comparison
        df_columns = [col.lower() for col in df.columns]
        missing_columns = []
        
        for col in required_cols:
            if col.lower() not in df_columns:
                missing_columns.append(col)
        
        return len(missing_columns) == 0, missing_columns
    
    def clean_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """
        Clean and standardize the data
        
        Args:
            df: DataFrame to clean
            data_type: 'buyers' or 'suppliers'
            
        Returns:
            Cleaned DataFrame
        """
        # Convert column names to lowercase
        df.columns = df.columns.str.lower().str.strip()
        
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Fill missing values
        df = df.fillna('')
        
        # Trim whitespace
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.strip()
        
        # Validate email format
        if 'email' in df.columns:
            df['email'] = df['email'].str.lower()
            # Basic email validation
            df['email_valid'] = df['email'].str.contains(r'^[\w\.-]+@[\w\.-]+\.\w+$', na=False)
        
        # Standardize phone numbers (remove special characters)
        if 'phone' in df.columns:
            df['phone'] = df['phone'].astype(str).str.replace(r'[^\d+\-\s()]', '', regex=True)
        
        return df
    
    def preview_import(self, file_path: str, data_type: str, limit: int = 10) -> Dict[str, Any]:
        """
        Preview the data to be imported
        
        Args:
            file_path: Path to the file
            data_type: 'buyers' or 'suppliers'
            limit: Number of rows to preview
            
        Returns:
            Dictionary with preview data and validation results
        """
        try:
            # Read the file
            df = self.read_file(file_path)
            
            # Validate columns
            is_valid, missing_columns = self.validate_columns(df, data_type)
            
            # Clean data
            df = self.clean_data(df, data_type)
            
            # Get statistics
            total_rows = len(df)
            valid_emails = df['email_valid'].sum() if 'email_valid' in df.columns else 0
            
            # Prepare preview data
            preview_data = df.head(limit).to_dict('records')
            
            # Column mapping suggestions
            if data_type == 'buyers':
                expected_columns = self.BUYER_REQUIRED_COLUMNS + self.BUYER_OPTIONAL_COLUMNS
            else:
                expected_columns = self.SUPPLIER_REQUIRED_COLUMNS + self.SUPPLIER_OPTIONAL_COLUMNS
            
            available_columns = list(df.columns)
            
            return {
                'success': True,
                'is_valid': is_valid,
                'missing_columns': missing_columns,
                'total_rows': total_rows,
                'valid_emails': valid_emails,
                'invalid_emails': total_rows - valid_emails,
                'preview_data': preview_data,
                'available_columns': available_columns,
                'expected_columns': expected_columns,
                'column_mapping': self._suggest_column_mapping(available_columns, expected_columns)
            }
            
        except Exception as e:
            logger.error(f"Error previewing import: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _suggest_column_mapping(self, available: List[str], expected: List[str]) -> Dict[str, str]:
        """
        Suggest column mappings based on similarity
        
        Args:
            available: Available columns in the file
            expected: Expected columns for the data type
            
        Returns:
            Dictionary mapping available columns to expected columns
        """
        mapping = {}
        
        # Direct matches
        for col in available:
            if col in expected:
                mapping[col] = col
        
        # Common variations
        variations = {
            'company': 'company_name',
            'business': 'company_name',
            'organization': 'company_name',
            'tel': 'phone',
            'telephone': 'phone',
            'mobile': 'phone',
            'location': 'city',
            'email_address': 'email',
            'mail': 'email',
            'contact_name': 'name',
            'full_name': 'name',
            'country_code': 'country',
            'nation': 'country',
            'minimum_order_quantity': 'minimum_order',
            'moq': 'minimum_order',
            'certificates': 'certifications',
            'payment': 'payment_terms',
            'terms': 'payment_terms'
        }
        
        for col in available:
            col_lower = col.lower()
            if col_lower in variations and variations[col_lower] in expected:
                if col not in mapping:
                    mapping[col] = variations[col_lower]
        
        return mapping
    
    def import_data(self, file_path: str, data_type: str, column_mapping: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Import data from file
        
        Args:
            file_path: Path to the file
            data_type: 'buyers' or 'suppliers'
            column_mapping: Optional custom column mapping
            
        Returns:
            Dictionary with import results
        """
        try:
            # Read and clean data
            df = self.read_file(file_path)
            df = self.clean_data(df, data_type)
            
            # Apply column mapping if provided
            if column_mapping:
                df = df.rename(columns=column_mapping)
            
            # Validate columns
            is_valid, missing_columns = self.validate_columns(df, data_type)
            if not is_valid:
                return {
                    'success': False,
                    'error': f"Missing required columns: {', '.join(missing_columns)}"
                }
            
            # Filter to only include expected columns
            if data_type == 'buyers':
                expected_cols = self.BUYER_REQUIRED_COLUMNS + self.BUYER_OPTIONAL_COLUMNS
            else:
                expected_cols = self.SUPPLIER_REQUIRED_COLUMNS + self.SUPPLIER_OPTIONAL_COLUMNS
            
            # Keep only columns that exist in both DataFrame and expected columns
            cols_to_keep = [col for col in expected_cols if col in df.columns]
            df = df[cols_to_keep]
            
            # Convert to records
            records = df.to_dict('records')
            
            # Add timestamps
            timestamp = datetime.now().isoformat()
            for record in records:
                record['created_at'] = timestamp
                record['updated_at'] = timestamp
            
            # Save to JSON file (since we don't have a database yet)
            output_dir = os.path.join(os.getcwd(), 'data', data_type)
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, f'{data_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'imported_count': len(records),
                'file_path': output_file,
                'message': f"Successfully imported {len(records)} {data_type}"
            }
            
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_import_template(self, data_type: str) -> pd.DataFrame:
        """
        Generate a template file for import
        
        Args:
            data_type: 'buyers' or 'suppliers'
            
        Returns:
            DataFrame with template structure
        """
        if data_type == 'buyers':
            columns = self.BUYER_REQUIRED_COLUMNS + self.BUYER_OPTIONAL_COLUMNS
            sample_data = {
                'name': ['John Smith', 'Jane Doe'],
                'email': ['john@example.com', 'jane@example.com'],
                'company_name': ['ABC Corp', 'XYZ Ltd'],
                'phone': ['+1-234-567-8900', '+1-234-567-8901'],
                'country': ['USA', 'Canada'],
                'city': ['New York', 'Toronto'],
                'address': ['123 Main St', '456 Oak Ave'],
                'industry': ['Food & Beverage', 'Retail'],
                'company_size': ['Medium', 'Large'],
                'payment_terms': ['Net 30', 'Net 60']
            }
        else:
            columns = self.SUPPLIER_REQUIRED_COLUMNS + self.SUPPLIER_OPTIONAL_COLUMNS
            sample_data = {
                'name': ['Supplier One', 'Supplier Two'],
                'email': ['supplier1@example.com', 'supplier2@example.com'],
                'company_name': ['Fresh Foods Inc', 'Quality Produce Ltd'],
                'phone': ['+1-234-567-8900', '+1-234-567-8901'],
                'country': ['USA', 'Mexico'],
                'city': ['Los Angeles', 'Mexico City'],
                'address': ['789 Farm Road', '321 Market St'],
                'industry': ['Agriculture', 'Food Processing'],
                'company_size': ['Large', 'Medium'],
                'certifications': ['ISO 9001, HACCP', 'Organic, Fair Trade'],
                'payment_terms': ['Net 30', 'Net 45'],
                'minimum_order': ['$5,000', '$10,000']
            }
        
        # Create DataFrame with sample data
        df = pd.DataFrame(sample_data)
        
        # Ensure all columns are present (fill with empty strings if not in sample)
        for col in columns:
            if col not in df.columns:
                df[col] = ''
        
        return df[columns]

# Create a singleton instance
data_import_service = DataImportService()