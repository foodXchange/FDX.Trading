#!/usr/bin/env python3
"""
Simple AI Email Analyzer for Supplier Responses
Keeps it lean and focused on essential analysis
"""

import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class SupplierEmailAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            base_url=os.getenv('AZURE_OPENAI_ENDPOINT', 'https://api.openai.com/v1')
        )
    
    def analyze_supplier_response(self, email_content, supplier_name=None, project_name=None):
        """
        Analyze supplier email response with AI
        Returns structured data for easy processing
        """
        
        # Simple prompt focused on key business information
        prompt = f"""
Analyze this supplier email response and extract key business information.
Supplier: {supplier_name or 'Unknown'}
Project: {project_name or 'Unknown'}

Email Content:
{email_content}

Please analyze and return ONLY a JSON object with this exact structure:
{{
    "interest_level": "interested|not_interested|need_info|unclear",
    "priority_score": 0-100,
    "key_points": ["bullet", "points", "of", "main", "info"],
    "pricing_mentioned": true/false,
    "capacity_mentioned": true/false,
    "lead_time_mentioned": true/false,
    "certifications_mentioned": ["list", "of", "certifications"],
    "next_action": "follow_up|request_samples|negotiate|schedule_call|no_action",
    "summary": "Brief 2-sentence summary of response"
}}

Be concise and practical. Focus on actionable business intelligence.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business analyst specialized in B2B supplier communications. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Clean up response to ensure valid JSON
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '')
            
            analysis = json.loads(ai_response)
            
            # Validate and set defaults
            analysis.setdefault('interest_level', 'unclear')
            analysis.setdefault('priority_score', 50)
            analysis.setdefault('key_points', [])
            analysis.setdefault('summary', 'Email analysis completed')
            
            return analysis
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            # Return basic fallback analysis
            return {
                "interest_level": "unclear",
                "priority_score": 50,
                "key_points": ["Analysis failed - manual review needed"],
                "pricing_mentioned": False,
                "capacity_mentioned": False,
                "lead_time_mentioned": False,
                "certifications_mentioned": [],
                "next_action": "follow_up",
                "summary": "AI analysis failed, manual review required",
                "error": str(e)
            }
    
    def generate_tasks(self, analysis, supplier_email, project_id):
        """
        Generate simple tasks based on AI analysis
        Returns list of task dictionaries
        """
        tasks = []
        
        # Map analysis to task types
        if analysis['interest_level'] == 'interested':
            if analysis['next_action'] == 'request_samples':
                tasks.append({
                    'task_type': 'request_samples',
                    'title': f'Request samples from {supplier_email}',
                    'description': 'Follow up on interested supplier to request product samples',
                    'priority': 'high',
                    'due_date': datetime.now() + timedelta(days=2)
                })
            elif analysis['next_action'] == 'negotiate':
                tasks.append({
                    'task_type': 'negotiate',
                    'title': f'Negotiate pricing with {supplier_email}',
                    'description': 'Discuss pricing and terms with interested supplier',
                    'priority': 'high',
                    'due_date': datetime.now() + timedelta(days=3)
                })
            else:
                tasks.append({
                    'task_type': 'follow_up',
                    'title': f'Follow up with {supplier_email}',
                    'description': 'Continue conversation with interested supplier',
                    'priority': 'medium',
                    'due_date': datetime.now() + timedelta(days=5)
                })
        
        elif analysis['interest_level'] == 'need_info':
            tasks.append({
                'task_type': 'provide_info',
                'title': f'Provide additional info to {supplier_email}',
                'description': 'Send requested information to potential supplier',
                'priority': 'medium',
                'due_date': datetime.now() + timedelta(days=1)
            })
        
        elif analysis['interest_level'] == 'not_interested':
            tasks.append({
                'task_type': 'archive',
                'title': f'Archive response from {supplier_email}',
                'description': 'Supplier not interested - archive for future reference',
                'priority': 'low',
                'due_date': datetime.now() + timedelta(days=7)
            })
        
        return tasks

# Test function
def test_analyzer():
    """Test the email analyzer with sample data"""
    analyzer = SupplierEmailAnalyzer()
    
    sample_email = """
    Dear FDX Trading Team,
    
    Thank you for your inquiry about our organic sunflower oil products.
    
    We are very interested in working with you. We can supply:
    - Organic sunflower oil in 1L and 5L bottles
    - Minimum order: 1000 units
    - Lead time: 2-3 weeks
    - Price: $12 per liter (FOB)
    - We have ISO 22000 and organic certifications
    
    Would you like samples? We can send them next week.
    
    Best regards,
    Maria Rodriguez
    Mediterranean Oil Co.
    """
    
    result = analyzer.analyze_supplier_response(
        sample_email, 
        "Mediterranean Oil Co.", 
        "Sunflower Oil Project"
    )
    
    print("AI Analysis Result:")
    print(json.dumps(result, indent=2))
    
    tasks = analyzer.generate_tasks(result, "maria@medoil.com", 1)
    print("\nGenerated Tasks:")
    for task in tasks:
        print(f"- {task['title']} (Priority: {task['priority']})")

if __name__ == "__main__":
    test_analyzer()