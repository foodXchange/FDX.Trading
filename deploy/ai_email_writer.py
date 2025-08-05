#!/usr/bin/env python3
"""
AI Email Writer for Outgoing Emails with Template Management
Simple and focused on business communication
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class AIEmailWriter:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),  
            base_url=os.getenv('AZURE_OPENAI_ENDPOINT', 'https://api.openai.com/v1')
        )
        
        # Title mappings for professional address
        self.titles = {
            'mr': 'Mr.',
            'mrs': 'Mrs.',
            'ms': 'Ms.',
            'dr': 'Dr.',
            'rabbi': 'Rabbi',
            'prof': 'Prof.',
            'sir': 'Sir',
            'madam': 'Madam'
        }
    
    def generate_email(self, template_type, recipient_name, recipient_title='mr', 
                      company_name='', product_details='', custom_notes=''):
        """
        Generate AI-powered email based on template type and recipient details
        """
        
        # Get proper title
        title = self.titles.get(recipient_title.lower(), 'Mr.')
        full_name = f"{title} {recipient_name}" if recipient_name else "Dear Sir/Madam"
        
        # Email templates with AI enhancement
        templates = {
            'inquiry': {
                'subject': f'Business Inquiry - Partnership Opportunity with FDX.trading',
                'prompt': f"""
Write a professional business inquiry email for FDX.trading. 

Recipient: {full_name}
Company: {company_name or 'your company'}
Product Interest: {product_details or 'food products'}
Additional Notes: {custom_notes or 'None'}

Create a professional email that:
1. Introduces FDX.trading as a food trading platform
2. Expresses interest in their products/services
3. Requests information about pricing, MOQ, certifications
4. Suggests next steps for partnership
5. Maintains formal business tone

Keep it concise but comprehensive. Include clear call-to-action.
"""
            },
            'follow_up': {
                'subject': f'Follow-up: Partnership Discussion with FDX.trading',
                'prompt': f"""
Write a professional follow-up email for FDX.trading.

Recipient: {full_name}
Company: {company_name or 'your company'}
Context: {custom_notes or 'Previous communication about business partnership'}

Create a polite follow-up email that:
1. References previous communication
2. Reiterates interest in partnership
3. Asks for updates or next steps
4. Offers additional information if needed
5. Maintains professional, non-pushy tone

Keep it brief and respectful of their time.
"""
            },
            'quotation_request': {
                'subject': f'Quotation Request - {product_details or "Product Information"}',
                'prompt': f"""
Write a professional quotation request email for FDX.trading.

Recipient: {full_name}
Company: {company_name or 'your company'} 
Products: {product_details or 'food products'}
Special Requirements: {custom_notes or 'Standard requirements'}

Create a detailed quotation request that includes:
1. Professional introduction of FDX.trading
2. Specific product requirements
3. Request for pricing, MOQ, lead times
4. Quality certifications needed
5. Shipping and payment terms inquiry
6. Timeline for decision making

Be specific about requirements while maintaining professional tone.
"""
            },
            'thank_you': {
                'subject': f'Thank You - FDX.trading Partnership Discussion',
                'prompt': f"""
Write a professional thank you email for FDX.trading.

Recipient: {full_name}
Company: {company_name or 'your company'}
Context: {custom_notes or 'Recent business discussion or meeting'}

Create a gracious thank you email that:
1. Thanks them for their time and consideration
2. Summarizes key points discussed
3. Confirms next steps if any
4. Leaves door open for future opportunities
5. Maintains warm professional relationship

Keep it genuine and appreciative.
"""
            }
        }
        
        template = templates.get(template_type, templates['inquiry'])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional business email writer for FDX.trading, a B2B food trading platform. Write clear, professional, and effective business emails."},
                    {"role": "user", "content": template['prompt']}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            email_body = response.choices[0].message.content.strip()
            
            return {
                'subject': template['subject'],
                'body': email_body,
                'recipient_title': title,
                'recipient_name': recipient_name,
                'company_name': company_name
            }
            
        except Exception as e:
            print(f"AI email generation error: {e}")
            # Fallback template
            return {
                'subject': template['subject'],
                'body': f"""Dear {full_name},

I hope this message finds you well. I am writing on behalf of FDX.trading regarding potential business opportunities.

We are interested in learning more about your products and services, and would appreciate the opportunity to discuss potential partnership opportunities.

Please let us know if you would be available for a brief discussion at your convenience.

Best regards,

The FDX.trading Team
Email: partnerships@fdx.trading
Platform: www.fdx.trading""",
                'recipient_title': title,
                'recipient_name': recipient_name,
                'company_name': company_name,
                'error': str(e)
            }
    
    def customize_template(self, template_content, recipient_name, recipient_title, 
                          company_name='', additional_vars=None):
        """
        Customize existing template with recipient-specific information
        """
        title = self.titles.get(recipient_title.lower(), 'Mr.')
        full_name = f"{title} {recipient_name}" if recipient_name else "Dear Sir/Madam"
        
        # Basic template variables
        variables = {
            '{RECIPIENT_NAME}': full_name,
            '{RECIPIENT_TITLE}': title,
            '{RECIPIENT_FIRST_NAME}': recipient_name,
            '{COMPANY_NAME}': company_name or '[Company Name]',
            '{DATE}': datetime.now().strftime('%B %d, %Y'),
            '{SENDER_NAME}': 'FDX.trading Team',
            '{SENDER_EMAIL}': 'partnerships@fdx.trading'
        }
        
        # Add any additional variables
        if additional_vars:
            variables.update(additional_vars)
        
        # Replace variables in template
        customized_content = template_content
        for variable, value in variables.items():
            customized_content = customized_content.replace(variable, value)
        
        return customized_content

# Test the AI email writer
def test_email_writer():
    """Test the AI email writer with sample data"""
    writer = AIEmailWriter()
    
    email = writer.generate_email(
        template_type='inquiry',
        recipient_name='Rodriguez',
        recipient_title='mrs',
        company_name='Mediterranean Oil Co.',
        product_details='Organic sunflower oil',
        custom_notes='Found through supplier database, ISO certified'
    )
    
    print("Generated Email:")
    print(f"Subject: {email['subject']}")
    print(f"To: {email['recipient_title']} {email['recipient_name']}")
    print("\nBody:")
    print(email['body'])

if __name__ == "__main__":
    test_email_writer()