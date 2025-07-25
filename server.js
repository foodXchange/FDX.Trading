// Simple Node.js server for Azure
const http = require('http');
const port = process.env.PORT || 8000;

const server = http.createServer((req, res) => {
    if (req.url === '/') {
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>FoodXchange</title>
                <style>
                    body { 
                        font-family: Arial; 
                        text-align: center; 
                        padding: 50px;
                        background: #f0f0f0;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        display: inline-block;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    h1 { color: #10b981; }
                    .status { 
                        background: #10b981; 
                        color: white; 
                        padding: 10px 20px; 
                        border-radius: 5px; 
                        display: inline-block;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🍎 FoodXchange</h1>
                    <div class="status">✅ Node.js Server Running on Azure!</div>
                    <p>Port: ${port}</p>
                    <p>This confirms Azure App Service is working.</p>
                    <p>Python app configuration may need adjustment.</p>
                </div>
            </body>
            </html>
        `);
    } else if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'healthy', runtime: 'node.js' }));
    } else {
        res.writeHead(404);
        res.end('Not Found');
    }
});

server.listen(port, () => {
    console.log(`FoodXchange Node.js server running on port ${port}`);
});