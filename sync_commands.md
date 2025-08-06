# Quick Sync Commands for FDX

## Check Status (What's different?)
```bash
git status
```

## Get Latest from VM/GitHub to Local
```bash
git pull
```

## Send Local Changes to VM
```bash
# Three steps:
git add .
git commit -m "What you changed"
git push

# Then on VM:
ssh fdx-vm "cd ~/fdx/app && git pull && sudo systemctl restart fdx-app"
```

## One-Line Deploy (after local changes)
```bash
git add . && git commit -m "Update" && git push && ssh fdx-vm "cd ~/fdx/app && git pull && sudo systemctl restart fdx-app"
```

## Check if VM and Local are in Sync
```bash
# Local
git log --oneline -1

# VM
ssh fdx-vm "cd ~/fdx/app && git log --oneline -1"

# If they show same commit ID = synced!
```

## Emergency: VM Has Changes You Don't Have Locally
```bash
# First, save your local work
git stash

# Get VM's version
git pull

# Re-apply your local changes
git stash pop
```

## See What Will Change Before Pulling
```bash
git fetch
git diff HEAD origin/main
```