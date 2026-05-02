@echo off
echo n8n baslatiliyor...
SET PATH=C:\node20;C:\node20\node_modules\.bin;%PATH%
SET N8N_PORT=5678
SET N8N_BASIC_AUTH_ACTIVE=false
SET N8N_SKIP_WEBHOOK_DEREGISTRATION_SHUTDOWN=true
SET N8N_USER_FOLDER=%~dp0.n8n_data

cd /d "%~dp0"
node "C:\node20\node_modules\n8n\bin\n8n" start
pause
