# Setup Kibana Visualizations - Complete Setup Script
# This script generates data and sets up Kibana automatically

Write-Host "================================" -ForegroundColor Green
Write-Host "🚀 KIBANA AUTO-SETUP" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Step 1: Activate venv
Write-Host "`n1️⃣  Activating Python environment..."
& .\venv\Scripts\Activate.ps1

# Step 2: Generate data
Write-Host "`n2️⃣  Generating IoT data..."
python scripts/generate_iot_data.py

Write-Host "`n⏳ Waiting 10 seconds for data to be processed..."
Start-Sleep -Seconds 10

# Step 3: Setup Kibana
Write-Host "`n3️⃣  Setting up Kibana visualizations..."
python scripts/setup_kibana_viz.py

Write-Host "`n================================" -ForegroundColor Green
Write-Host "✅ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host "`n🌐 Open Kibana: http://localhost:5601" -ForegroundColor Cyan
Write-Host "📊 Dashboard: IoT Smart Building - Monitoring" -ForegroundColor Cyan
Write-Host "`n✨ All visualizations are ready!" -ForegroundColor Yellow
