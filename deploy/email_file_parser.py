#!/usr/bin/env python3
"""
Email File Parser for FDX.trading
Parses .eml and .msg files for AI analysis
Lean implementation focused on extracting key information
"""

import email
import email.utils
import re
from datetime import datetime
from typing import Dict, Optional

class EmailFileParser:
    def __init__(self):
        pass
    
    def parse_eml_file(self, file_content: bytes) -> Dict:
        """
        Parse .eml file content and extract key information
        """
        try:
            # Parse the email
            msg = email.message_from_bytes(file_content)
            
            # Extract basic information
            parsed_email = {
                'subject': self._clean_subject(msg.get('Subject', '')),
                'from_email': self._extract_email(msg.get('From', '')),
                'from_name': self._extract_name(msg.get('From', '')),
                'to_email': self._extract_email(msg.get('To', '')),
                'date': self._parse_date(msg.get('Date', '')),
                'message_id': msg.get('Message-ID', ''),
                'body': self._extract_body(msg),
                'is_reply': self._is_reply(msg.get('Subject', '')),
                'in_reply_to': msg.get('In-Reply-To', ''),
                'file_type': 'eml'
            }
            
            return parsed_email
            
        except Exception as e:
            return {
                'error': f'Failed to parse EML file: {str(e)}',
                'file_type': 'eml'
            }
    
    def parse_email_content(self, content: str, subject: str = '', from_email: str = '') -> Dict:
        """
        Parse plain text email content (for simple text uploads)
        """
        return {
            'subject': subject,
            'from_email': from_email,
            'from_name': self._extract_name_from_email(from_email),
            'to_email': 'udi@fdx.trading',
            'date': datetime.now().isoformat(),
            'message_id': '',
            'body': content,
            'is_reply': self._is_reply(subject),
            'in_reply_to': '',
            'file_type': 'text'
        }
    
    def _clean_subject(self, subject: str) -> str:
        """Clean and decode email subject"""
        if not subject:
            return ''
        
        # Decode encoded subjects
        decoded_parts = email.header.decode_header(subject)
        subject = ''
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                subject += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                subject += part
        
        return subject.strip()
    
    def _extract_email(self, email_field: str) -> str:
        """Extract email address from email field"""
        if not email_field:
            return ''
        
        # Use regex to find email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, email_field)
        return matches[0] if matches else ''
    
    def _extract_name(self, email_field: str) -> str:
        """Extract name from email field"""
        if not email_field:
            return ''
        
        # Try to parse with email.utils first
        name, email_addr = email.utils.parseaddr(email_field)
        if name:
            # Decode if needed
            decoded_parts = email.header.decode_header(name)
            decoded_name = ''
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_name += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_name += part
            return decoded_name.strip()
        
        # If no name found, try to extract from email
        return self._extract_name_from_email(self._extract_email(email_field))
    
    def _extract_name_from_email(self, email_addr: str) -> str:
        """Extract probable name from email address"""
        if not email_addr or '@' not in email_addr:
            return ''
        
        local_part = email_addr.split('@')[0]
        # Convert common patterns to names
        name = local_part.replace('.', ' ').replace('_', ' ').replace('-', ' ')
        return name.title()
    
    def _parse_date(self, date_str: str) -> str:
        """Parse email date to ISO format"""
        if not date_str:
            return datetime.now().isoformat()
        
        try:
            # Parse the date
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            return parsed_date.isoformat()
        except:
            return datetime.now().isoformat()
    
    def _extract_body(self, msg) -> str:
        """Extract email body content"""
        body = ''
        
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        charset = part.get_content_charset() or 'utf-8'
                        body_part = part.get_payload(decode=True)
                        if body_part:
                            body += body_part.decode(charset, errors='ignore')
                    elif content_type == 'text/html' and not body:
                        # Fall back to HTML if no plain text
                        charset = part.get_content_charset() or 'utf-8'
                        html_part = part.get_payload(decode=True)
                        if html_part:
                            body = self._strip_html(html_part.decode(charset, errors='ignore'))
            else:
                # Single part message
                charset = msg.get_content_charset() or 'utf-8'
                body_content = msg.get_payload(decode=True)
                if body_content:
                    if msg.get_content_type() == 'text/html':
                        body = self._strip_html(body_content.decode(charset, errors='ignore'))
                    else:
                        body = body_content.decode(charset, errors='ignore')
        
        except Exception as e:
            body = f"Error extracting body: {str(e)}"
        
        return self._clean_body(body)
    
    def _strip_html(self, html_content: str) -> str:
        """Strip HTML tags and return plain text"""
        import re
        # Remove HTML tags
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', html_content)
        # Decode HTML entities
        import html
        text = html.unescape(text)
        return text
    
    def _clean_body(self, body: str) -> str:
        """Clean email body content"""
        if not body:
            return ''
        
        # Remove excessive whitespace
        body = re.sub(r'\n\s*\n', '\n\n', body)
        body = re.sub(r' +', ' ', body)
        
        # Remove common email signatures and footers
        signature_patterns = [
            r'\n--\s*\n.*',
            r'\nSent from my .*',
            r'\nGet Outlook for .*',
            r'\n\[.*unsubscribe.*\].*',
        ]
        
        for pattern in signature_patterns:
            body = re.sub(pattern, '', body, flags=re.DOTALL | re.IGNORECASE)
        
        return body.strip()
    
    def _is_reply(self, subject: str) -> bool:
        """Check if email is a reply"""
        if not subject:
            return False
        
        reply_patterns = [r'^Re:', r'^RE:', r'^Fwd:', r'^FWD:']
        for pattern in reply_patterns:
            if re.match(pattern, subject):
                return True
        return False

# Test the parser
def test_parser():
    parser = EmailFileParser()
    
    # Test with sample content
    sample_content = """Subject: Re: Business Inquiry - Partnership Opportunity
From: Maria Rodriguez <maria@globalfood.com>
To: udi@fdx.trading
Date: Sat, 3 Aug 2024 10:30:00 +0000

Dear Udi,

Thank you for your inquiry about our sunflower oil products. 

We are interested in discussing a partnership opportunity. Our company specializes in high-quality sunflower oil production with organic certification.

We can offer:
- Bulk quantities starting from 1000L
- Competitive pricing for long-term contracts
- ISO 22000 and organic certifications

Please let me know your specific requirements and we can schedule a call.

Best regards,
Maria Rodriguez
Global Food Solutions Ltd
"""
    
    result = parser.parse_email_content(sample_content, 
                                      "Re: Business Inquiry - Partnership Opportunity",
                                      "maria@globalfood.com")
    
    print("Parsed email:")
    for key, value in result.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_parser()