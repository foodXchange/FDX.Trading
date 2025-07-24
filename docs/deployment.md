# Deployment Guide

## Azure Deployment

### Backend (App Service)
1. Create App Service
2. Configure environment variables
3. Deploy via Git or ZIP

### Frontend (Static Web App)
1. Build production bundle: `npm run build`
2. Create Static Web App
3. Deploy build folder

### Database
- Already on Cosmos DB
- Set up backups
- Configure scaling

## Production Checklist
- [ ] Change SECRET_KEY
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test email delivery
- [ ] Verify AI endpoints
- [ ] Load test with 1000 suppliers 