@echo off
echo Deploying to FDX.trading...
git add .
git commit -m %1
git push
ssh fdx-vm "cd ~/fdx/app && git pull && sudo systemctl restart fdx-app && echo 'Deployment complete!'"
echo Done! Check https://www.fdx.trading