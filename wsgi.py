"""WSGI entry point for Azure/Gunicorn"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def application(environ, start_response):
    """Basic WSGI application"""
    start_response('200 OK', [('Content-Type', 'text/html')])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FoodXchange WSGI</title>
        <style>
            body {{ 
                font-family: -apple-system, Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background: rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            }}
            h1 {{ margin: 0 0 20px 0; font-size: 3em; }}
            .badge {{
                background: #10b981;
                padding: 10px 20px;
                border-radius: 20px;
                display: inline-block;
                margin: 20px 0;
            }}
            .info {{
                background: rgba(255,255,255,0.2);
                padding: 20px;
                border-radius: 10px;
                margin-top: 20px;
            }}
            a {{ color: white; text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🍎 FoodXchange</h1>
            <div class="badge">✅ WSGI Application Running!</div>
            
            <div class="info">
                <p><strong>Server:</strong> Azure App Service</p>
                <p><strong>Entry Point:</strong> wsgi.py</p>
                <p><strong>Port:</strong> {os.environ.get('PORT', 'Default')}</p>
                <p><strong>Python:</strong> {sys.version.split()[0]}</p>
            </div>
            
            <p style="margin-top: 30px;">
                <a href="/health">Health Check</a> | 
                <a href="/info">System Info</a>
            </p>
        </div>
    </body>
    </html>
    """.strip()
    
    path = environ.get('PATH_INFO', '/')
    
    if path == '/health':
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [b'{"status": "healthy", "app": "FoodXchange", "type": "WSGI"}']
    
    elif path == '/info':
        start_response('200 OK', [('Content-Type', 'application/json')])
        info = {
            'python_version': sys.version,
            'cwd': os.getcwd(),
            'files': os.listdir('.')[:10],
            'env_vars': {k: v for k, v in os.environ.items() if k.startswith(('PYTHON', 'WEBSITE', 'PORT'))}
        }
        import json
        return [json.dumps(info, indent=2).encode()]
    
    return [html.encode()]

# Try to import FastAPI app as fallback
try:
    from app.main import app as fastapi_app
    print("FastAPI app imported successfully")
    app = fastapi_app
except Exception as e:
    print(f"Could not import FastAPI app: {e}")
    app = application

# Gunicorn will look for 'application'
if not hasattr(sys.modules[__name__], 'application'):
    application = app