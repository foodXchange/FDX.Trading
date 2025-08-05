# FoodXchange VM Control Center

A modern, responsive web dashboard for managing the FoodXchange VM environment, built with FastAPI, Bootstrap, and Jinja templates.

## Features

- 🚀 **Modern UI**: Clean, responsive design with Bootstrap 5
- 📊 **Real-time Status**: Live service monitoring and status updates
- ⌨️ **Keyboard Shortcuts**: Quick access with number keys (1-4)
- 📋 **One-click Copy**: Copy URLs, SSH commands, and credentials
- 🔔 **Notifications**: Toast notifications for user feedback
- 📱 **Mobile Responsive**: Works perfectly on all devices
- 🔄 **Auto-refresh**: Automatic status updates every 30 seconds

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The dashboard will be available at: `http://localhost:8080`

### 3. Alternative: Using Uvicorn Directly

```bash
uvicorn app:app --host 0.0.0.0 --port 8080 --reload
```

## Project Structure

```
tools/vm-access/
├── app.py                 # FastAPI application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # Jinja templates
│   ├── base.html         # Base template
│   └── dashboard.html    # Main dashboard
├── static/               # Static files
│   ├── css/
│   │   └── styles.css    # Custom CSS
│   └── js/
│       └── app.js        # JavaScript functionality
└── quick_vm_access.html  # Original HTML file (legacy)
```

## API Endpoints

- `GET /` - Main dashboard page
- `GET /api/services` - Get service statuses
- `GET /api/vm-status` - Get VM status information
- `GET /health` - Health check endpoint

## Configuration

The VM configuration is stored in the `VM_CONFIG` dictionary in `app.py`. You can modify:

- Service URLs and ports
- SSH connection details
- Credentials
- Service descriptions

## Features in Detail

### Service Management
- **FastAPI App**: Main FoodXchange application
- **FDX Crawler**: Supplier database with 23,206 suppliers
- **Grafana**: System monitoring dashboard
- **Netdata**: Real-time system metrics

### SSH Access
- One-click SSH command copying
- SSH tunnel setup for blocked services
- Secure key-based authentication

### Keyboard Shortcuts
- `1` - Open FastAPI App
- `2` - Open FDX Crawler  
- `3` - Open Grafana
- `4` - Open Netdata
- `H` - Show help

### Status Monitoring
- Real-time service status checks
- Visual status indicators
- Automatic refresh every 30 seconds
- Uptime counter

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## Development

### Adding New Services

1. Add service configuration to `VM_CONFIG` in `app.py`:
```python
{
    "name": "New Service",
    "url": "http://4.206.1.15:8080",
    "port": 8080,
    "icon": "fas fa-cube",
    "description": "Service description",
    "status": "online",
    "warning": False
}
```

2. Update the dashboard template if needed
3. Add keyboard shortcut if desired

### Customizing Styles

Edit `static/css/styles.css` to customize:
- Colors and themes
- Animations
- Responsive behavior
- Component styling

### Extending Functionality

The JavaScript is organized in a class-based structure in `static/js/app.js`. You can:
- Add new event listeners
- Extend the notification system
- Add new API endpoints
- Implement additional features

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py` or kill the existing process
2. **Service not accessible**: Check firewall settings and service status
3. **Copy not working**: Ensure HTTPS or localhost for clipboard API

### Logs

Check the console output for:
- Service status check results
- API request logs
- Error messages

## Security Notes

- SSH keys should be properly secured
- Consider adding authentication for production use
- Monitor access logs
- Keep dependencies updated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the FoodXchange ecosystem. 