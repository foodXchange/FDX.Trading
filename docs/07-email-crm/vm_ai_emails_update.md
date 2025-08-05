# Add AI Emails to VM Navigation

## Files to Edit on VM

### 1. Edit suppliers.html
Find the navigation section around line 90 and add this AI Emails link:

```html
<li class="nav-item">
    <a class="nav-link" href="/email">
        <i class="bi bi-envelope-at"></i> AI Emails
    </a>
</li>
```

### 2. Edit projects_lean.html  
Find the navigation around line 18 and add:

```html
<a class="nav-link" href="/email"><i class="bi bi-envelope-at"></i> AI Emails</a>
```

### 3. Edit base.html (if it exists)
Add to navigation:

```html
<li class="nav-item">
    <a class="nav-link" href="/email">
        <i class="bi bi-envelope-at"></i> AI Emails
    </a>
</li>
```

### 4. Add /email Route to app.py
Add this route to handle the email dashboard:

```python
@app.get("/email", response_class=HTMLResponse)
async def email_dashboard(request: Request):
    """AI Email Dashboard"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Email Center - FDX.trading</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="/dashboard">FDX.trading</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/suppliers">Search</a>
                    <a class="nav-link" href="/projects">Projects</a>
                    <a class="nav-link active" href="/email"><i class="bi bi-envelope-at"></i> AI Emails</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1><i class="bi bi-envelope-at"></i> AI Email Center</h1>
            
            <div class="row mt-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="bi bi-pencil-square"></i> Compose Email</h5>
                            <p class="card-text">Send AI-generated emails to selected suppliers</p>
                            <a href="/email/compose" class="btn btn-primary">Compose Email</a>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title"><i class="bi bi-people"></i> Select Suppliers</h5>
                            <p class="card-text">Search and select suppliers for email campaigns</p>
                            <a href="/suppliers" class="btn btn-success">Select Suppliers</a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="alert alert-info mt-4">
                <h6><i class="bi bi-robot"></i> AI-Powered Email Features</h6>
                <ul>
                    <li>Automatic email generation using Azure OpenAI</li>
                    <li>Personalized content for each supplier</li>
                    <li>Professional business email templates</li>
                    <li>Bulk email capabilities</li>
                </ul>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(html)
```

## Quick Commands for VM

1. SSH to VM: `ssh azureuser@4.206.1.15`
2. Navigate to project: `cd ~/foodxchange`
3. Edit files: `nano templates/suppliers.html`
4. Restart server: `sudo systemctl restart foodxchange`

## Test
After making changes, test at: http://4.206.1.15:8000/email