@echo off
az ad sp create-for-rbac --name "github-actions-foodxchange" --role "contributor" --scopes "/subscriptions/88931ed0-52df-42fb-a09c-e024c9586f8a/resourceGroups/foodxchange-rg"