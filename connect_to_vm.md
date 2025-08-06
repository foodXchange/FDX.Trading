# Connecting Cursor to VM

## Method 1: Remote SSH Extension

1. Open Cursor
2. Press `Ctrl+Shift+X` to open extensions
3. Search for "Remote - SSH"
4. Install it
5. Press `Ctrl+Shift+P`
6. Type "Remote-SSH: Connect to Host"
7. Select `fdx-vm`
8. Cursor will reopen connected to VM

## Method 2: Command Palette Quick Connect

1. Press `Ctrl+Shift+P`
2. Type: `Remote-SSH: Connect Current Window to Host`
3. Choose `fdx-vm`

## Method 3: Use SSH Config

Your SSH config is already set up at:
`C:\Users\foodz\.ssh\config`

## Once Connected:

- Open folder: `/home/fdxfounder/fdx/app`
- Terminal runs on VM
- File changes are immediate
- Use `sudo systemctl restart fdx-app` to apply changes

## To Disconnect:

1. Click the green "SSH" button in bottom-left corner
2. Select "Close Remote Connection"