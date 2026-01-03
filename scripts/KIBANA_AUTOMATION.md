# 🤖 KIBANA AUTOMATION & HELPER SCRIPTS

This file contains PowerShell and curl commands to automate Kibana setup.

---

## 📋 PREREQUISITE VERIFICATION SCRIPT

### Save as: `scripts/verify_kibana_setup.ps1`

```powershell
# Kibana Setup Verification Script
# Checks if all prerequisites are met

Write-Host "🔍 Kibana Setup Verification" -ForegroundColor Cyan
Write-Host "=" * 50

# 1. Check Docker Services
Write-Host "`n1️⃣ Checking Docker Services..." -ForegroundColor Yellow
$services = @("elasticsearch", "kibana", "mongodb", "redis", "webapp")
$status = docker-compose ps --format "{{.Service}},{{.Status}}"

foreach ($service in $services) {
    $running = $status | Select-String $service | Select-String "Up"
    if ($running) {
        Write-Host "  ✅ $service : Running" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $service : NOT Running" -ForegroundColor Red
    }
}

# 2. Check Elasticsearch
Write-Host "`n2️⃣ Checking Elasticsearch..." -ForegroundColor Yellow
try {
    $es = curl -s http://localhost:9200
    $version = $es | ConvertFrom-Json | Select-Object -ExpandProperty version | Select-Object -ExpandProperty number
    Write-Host "  ✅ Elasticsearch: Version $version" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Elasticsearch: Unreachable" -ForegroundColor Red
}

# 3. Check Kibana
Write-Host "`n3️⃣ Checking Kibana..." -ForegroundColor Yellow
try {
    $kb = curl -s http://localhost:5601/api/status | ConvertFrom-Json
    Write-Host "  ✅ Kibana: Status OK" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Kibana: Unreachable" -ForegroundColor Red
}

# 4. Check Data
Write-Host "`n4️⃣ Checking Elasticsearch Data..." -ForegroundColor Yellow
try {
    $count = curl -s "http://localhost:9200/iot-logs-*/_count" | ConvertFrom-Json | Select-Object -ExpandProperty count
    if ($count -gt 500) {
        Write-Host "  ✅ Data: $count logs found" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Data: Only $count logs (recommend 1000+)" -ForegroundColor Yellow
        Write-Host "     Run: python scripts/generate_iot_data.py" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Data: Cannot query" -ForegroundColor Red
}

# 5. Check Index Pattern
Write-Host "`n5️⃣ Checking Index Pattern..." -ForegroundColor Yellow
try {
    $indices = curl -s "http://localhost:9200/_cat/indices?format=json" | ConvertFrom-Json
    $iot_indices = $indices | Where-Object { $_.index -like "iot-logs*" }
    if ($iot_indices) {
        Write-Host "  ✅ Index Pattern: $(($iot_indices | Measure-Object).Count) indices found" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Index Pattern: No iot-logs* indices yet" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ❌ Index Pattern: Cannot query" -ForegroundColor Red
}

Write-Host "`n" + ("=" * 50)
Write-Host "Verification Complete" -ForegroundColor Cyan
Write-Host "If all checks pass ✅, proceed with Kibana setup" -ForegroundColor Green
Write-Host "If any check fails ❌, see KIBANA_COMPLETE_SETUP.md" -ForegroundColor Yellow
```

### Run Verification
```powershell
.\scripts\verify_kibana_setup.ps1
```

---

## 🚀 DATA GENERATION & UPLOAD SCRIPT

### Save as: `scripts/generate_and_upload.ps1`

```powershell
# Automated Data Generation and Upload
# Generates IoT data and uploads via application API

Write-Host "📊 Generating IoT Test Data..." -ForegroundColor Cyan

# Activate venv
& .\venv\Scripts\Activate.ps1

# Generate data
python scripts/generate_iot_data.py

Write-Host "✅ Data generated in data/uploads/" -ForegroundColor Green
Write-Host "📤 Uploading to Elasticsearch..." -ForegroundColor Cyan

# Get list of CSV files
$csvFiles = Get-ChildItem -Path "data/uploads" -Filter "*.csv" | Select-Object -First 3

foreach ($file in $csvFiles) {
    Write-Host "  Uploading: $($file.Name)" -ForegroundColor Yellow
    
    # Upload via API
    $filePath = $file.FullName
    curl -X POST http://localhost:8000/upload/file `
        -F "file=@$filePath" `
        -H "Authorization: Bearer admin_token" `
        -s | Out-Null
    
    Write-Host "    ✅ Uploaded" -ForegroundColor Green
    Start-Sleep -Seconds 2  # Wait for processing
}

Write-Host "`n✅ All files uploaded. Data processing in Logstash..." -ForegroundColor Green
Write-Host "⏳ Waiting 30 seconds for Logstash..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Verify data
$count = curl -s "http://localhost:9200/iot-logs-*/_count" | ConvertFrom-Json | Select-Object -ExpandProperty count
Write-Host "`n📈 Total logs in Elasticsearch: $count" -ForegroundColor Green
Write-Host "✅ Ready for Kibana!" -ForegroundColor Green
```

### Run Data Upload
```powershell
.\scripts\generate_and_upload.ps1
```

---

## 🔧 KIBANA API HELPER FUNCTIONS

### Save as: `scripts/kibana_api_helpers.ps1`

```powershell
# Kibana API Helper Functions
# Use these to automate Kibana operations

$KIBANA_URL = "http://localhost:5601"
$ES_URL = "http://localhost:9200"

# Function: Create Index Pattern
function New-KibanaIndexPattern {
    param(
        [string]$Pattern = "iot-logs-*",
        [string]$TimeField = "@timestamp"
    )
    
    Write-Host "Creating Index Pattern: $Pattern" -ForegroundColor Cyan
    
    $body = @{
        attributes = @{
            title = $Pattern
            timeFieldName = $TimeField
            "fields" = "[]"
        }
    } | ConvertTo-Json
    
    $response = curl -X POST "$KIBANA_URL/api/saved_objects/index-pattern" `
        -H "kbn-xsrf: true" `
        -H "Content-Type: application/json" `
        -d $body
    
    Write-Host "✅ Index Pattern Created" -ForegroundColor Green
    return $response | ConvertFrom-Json
}

# Function: List Saved Objects (Visualizations, Dashboards)
function Get-KibanaSavedObjects {
    param(
        [string]$Type = "dashboard"  # "visualization", "dashboard", etc.
    )
    
    Write-Host "Fetching $Type objects..." -ForegroundColor Yellow
    
    $response = curl -s "$KIBANA_URL/api/saved_objects/$Type?per_page=100"
    $objects = $response | ConvertFrom-Json | Select-Object -ExpandProperty saved_objects
    
    Write-Host "Found $(($objects | Measure-Object).Count) $Type objects:" -ForegroundColor Green
    foreach ($obj in $objects) {
        Write-Host "  - $($obj.attributes.title)" -ForegroundColor Cyan
    }
    
    return $objects
}

# Function: Export Dashboard
function Export-KibanaDashboard {
    param(
        [string]$DashboardName,
        [string]$OutputPath = "config/kibana/dashboard_export.json"
    )
    
    Write-Host "Exporting Dashboard: $DashboardName" -ForegroundColor Cyan
    
    # First, find the dashboard by name
    $dashboards = Get-KibanaSavedObjects -Type "dashboard"
    $dashboard = $dashboards | Where-Object { $_.attributes.title -eq $DashboardName }
    
    if ($dashboard) {
        $id = $dashboard.id
        $response = curl -s "$KIBANA_URL/api/saved_objects/dashboard/$id"
        
        # Save to file
        $response | Out-File $OutputPath -Force
        Write-Host "✅ Exported to: $OutputPath" -ForegroundColor Green
        return $response | ConvertFrom-Json
    } else {
        Write-Host "❌ Dashboard not found: $DashboardName" -ForegroundColor Red
        return $null
    }
}

# Function: Import Dashboard from JSON
function Import-KibanaDashboard {
    param(
        [string]$JsonPath
    )
    
    Write-Host "Importing Dashboard from: $JsonPath" -ForegroundColor Cyan
    
    $content = Get-Content $JsonPath -Raw
    
    $response = curl -X POST "$KIBANA_URL/api/saved_objects/_import" `
        -H "kbn-xsrf: true" `
        -H "Content-Type: application/json" `
        -d $content
    
    Write-Host "✅ Dashboard Imported" -ForegroundColor Green
    return $response | ConvertFrom-Json
}

# Function: Test Kibana Connection
function Test-KibanaConnection {
    Write-Host "Testing Kibana Connection..." -ForegroundColor Yellow
    
    try {
        $response = curl -s -w "%{http_code}" "$KIBANA_URL/api/status"
        if ($response -match "200$") {
            Write-Host "✅ Kibana is accessible" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ Kibana returned: $response" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Cannot connect to Kibana: $_" -ForegroundColor Red
        return $false
    }
}

# Export functions for use in other scripts
Export-ModuleMember -Function @(
    'New-KibanaIndexPattern',
    'Get-KibanaSavedObjects',
    'Export-KibanaDashboard',
    'Import-KibanaDashboard',
    'Test-KibanaConnection'
)

Write-Host "✅ Kibana API Helpers Loaded" -ForegroundColor Green
```

### Use Helper Functions
```powershell
# Source the helpers
. .\scripts\kibana_api_helpers.ps1

# Create index pattern
New-KibanaIndexPattern -Pattern "iot-logs-*" -TimeField "@timestamp"

# List all dashboards
Get-KibanaSavedObjects -Type "dashboard"

# Export dashboard
Export-KibanaDashboard -DashboardName "IoT Smart Building - Monitoring" `
    -OutputPath "config/kibana/dashboard_iot.json"

# Test connection
Test-KibanaConnection
```

---

## 📸 AUTOMATED SCREENSHOT CAPTURE

### Save as: `scripts/capture_kibana_screenshots.ps1`

```powershell
# Automated screenshot capture for Kibana visualizations
# Requires: Selenium WebDriver or manual screenshots

Write-Host "📸 Kibana Screenshot Capture" -ForegroundColor Cyan
Write-Host "Note: Automated capture requires Selenium. Using manual method." -ForegroundColor Yellow

# Create directories if not exist
New-Item -ItemType Directory -Force -Path "docs/screenshots" | Out-Null

Write-Host "`n📋 Manual Screenshot Instructions:" -ForegroundColor Green
Write-Host "==================================`n" -ForegroundColor Green

$screenshots = @(
    @{
        Name = "kibana_dashboard_full.png"
        URL = "http://localhost:5601/app/dashboards"
        Description = "Full dashboard with all visualizations"
        Steps = @(
            "1. Open: http://localhost:5601/app/dashboards",
            "2. Search: 'IoT Smart Building'",
            "3. Click to open dashboard",
            "4. Press: PrtScn or Snip tool",
            "5. Capture entire dashboard",
            "6. Save to: docs/screenshots/kibana_dashboard_full.png"
        )
    },
    @{
        Name = "kibana_temperature_chart.png"
        URL = "http://localhost:5601/app/visualizations"
        Description = "Temperature line chart"
        Steps = @(
            "1. Open Visualizations: http://localhost:5601/app/visualizations",
            "2. Search: 'Temperature by Zone'",
            "3. Click to open",
            "4. Wait for chart to load",
            "5. Press: PrtScn",
            "6. Save to: docs/screenshots/kibana_temperature_chart.png"
        )
    },
    @{
        Name = "kibana_alerts_heatmap.png"
        URL = "http://localhost:5601/app/visualizations"
        Description = "Alerts distribution heatmap"
        Steps = @(
            "1. Open Visualizations",
            "2. Search: 'Alerts Heatmap'",
            "3. Click to open",
            "4. Press: PrtScn",
            "5. Save to: docs/screenshots/kibana_alerts_heatmap.png"
        )
    },
    @{
        Name = "kibana_energy_gauge.png"
        URL = "http://localhost:5601/app/visualizations"
        Description = "Energy consumption gauge"
        Steps = @(
            "1. Open Visualizations",
            "2. Search: 'Energy Consumption'",
            "3. Click to open",
            "4. Press: PrtScn",
            "5. Save to: docs/screenshots/kibana_energy_gauge.png"
        )
    }
)

foreach ($screenshot in $screenshots) {
    Write-Host "`n📷 Screenshot: $($screenshot.Name)" -ForegroundColor Cyan
    Write-Host "Description: $($screenshot.Description)" -ForegroundColor Yellow
    Write-Host "Steps:" -ForegroundColor Green
    
    foreach ($step in $screenshot.Steps) {
        Write-Host "   $step" -ForegroundColor White
    }
    
    Write-Host "`nTarget location: docs/screenshots/$($screenshot.Name)" -ForegroundColor Cyan
    Write-Host "━" * 60
}

Write-Host "`n✅ Screenshot instructions complete" -ForegroundColor Green
Write-Host "After taking all screenshots, verify files exist:" -ForegroundColor Yellow
Write-Host "   ls -la docs/screenshots/" -ForegroundColor Cyan
```

### Run Screenshot Guide
```powershell
.\scripts\capture_kibana_screenshots.ps1
```

---

## 🧹 CLEANUP & RESET SCRIPT

### Save as: `scripts/kibana_reset.ps1`

```powershell
# Reset Kibana to clean state
# WARNING: This deletes all Kibana saved objects

Write-Host "⚠️  Kibana Reset Script" -ForegroundColor Red
Write-Host "This will delete all dashboards and visualizations" -ForegroundColor Red

$confirm = Read-Host "Continue? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit
}

Write-Host "`nResetting Kibana..." -ForegroundColor Yellow

# Delete all saved objects
@("dashboard", "visualization", "index-pattern") | ForEach-Object {
    Write-Host "Deleting $_..." -ForegroundColor Yellow
    
    $objects = curl -s "http://localhost:5601/api/saved_objects/$_?per_page=1000" | ConvertFrom-Json | Select-Object -ExpandProperty saved_objects
    
    foreach ($obj in $objects) {
        curl -X DELETE "http://localhost:5601/api/saved_objects/$_/$($obj.id)" `
            -H "kbn-xsrf: true" | Out-Null
    }
    
    Write-Host "✅ Deleted $(($objects | Measure-Object).Count) $_" -ForegroundColor Green
}

Write-Host "`n✅ Kibana Reset Complete" -ForegroundColor Green
Write-Host "Now you can recreate dashboards fresh" -ForegroundColor Cyan
```

### Run Reset
```powershell
.\scripts\kibana_reset.ps1
```

---

## 🎯 COMPLETE AUTOMATION WORKFLOW

### Master Script - Save as: `scripts/setup_kibana_complete.ps1`

```powershell
# Complete Kibana Setup Automation
# Runs all steps in sequence

param(
    [switch]$SkipDataGeneration = $false,
    [switch]$SkipVerification = $false
)

Write-Host "🤖 Automated Kibana Setup" -ForegroundColor Cyan
Write-Host "=" * 60

# Step 1: Verify prerequisites
if (-not $SkipVerification) {
    Write-Host "`nStep 1: Verifying Prerequisites..." -ForegroundColor Yellow
    & .\scripts\verify_kibana_setup.ps1
    
    $proceed = Read-Host "Continue with setup? (yes/no)"
    if ($proceed -ne "yes") { exit }
}

# Step 2: Generate and upload data
if (-not $SkipDataGeneration) {
    Write-Host "`nStep 2: Generating and Uploading Data..." -ForegroundColor Yellow
    & .\scripts\generate_and_upload.ps1
}

# Step 3: Load helper functions
Write-Host "`nStep 3: Loading Kibana API Helpers..." -ForegroundColor Yellow
. .\scripts\kibana_api_helpers.ps1

# Step 4: Create index pattern via API
Write-Host "`nStep 4: Creating Index Pattern..." -ForegroundColor Yellow
$indexPattern = New-KibanaIndexPattern -Pattern "iot-logs-*" -TimeField "@timestamp"

Write-Host "`n✅ Automated setup complete!" -ForegroundColor Green
Write-Host "`nNext steps (Manual in Kibana UI):" -ForegroundColor Cyan
Write-Host "1. Open: http://localhost:5601" -ForegroundColor White
Write-Host "2. Create 3 visualizations:" -ForegroundColor White
Write-Host "   - Temperature Line Chart" -ForegroundColor White
Write-Host "   - Alerts Heatmap" -ForegroundColor White
Write-Host "   - Energy Gauge" -ForegroundColor White
Write-Host "3. Create dashboard combining all 3" -ForegroundColor White
Write-Host "4. Export dashboard as JSON" -ForegroundColor White
Write-Host "5. Take screenshots" -ForegroundColor White

Write-Host "`nFor detailed instructions, see:" -ForegroundColor Yellow
Write-Host "- KIBANA_COMPLETE_SETUP.md (detailed)" -ForegroundColor Cyan
Write-Host "- KIBANA_QUICK_START.md (quick)" -ForegroundColor Cyan
```

### Run Complete Setup
```powershell
.\scripts\setup_kibana_complete.ps1
```

---

## 📝 SUMMARY TABLE

| Script | Purpose | Time | Manual Steps |
|--------|---------|------|--------------|
| `verify_kibana_setup.ps1` | Pre-flight checks | 2 min | None |
| `generate_and_upload.ps1` | Data prep | 5 min | None |
| `kibana_api_helpers.ps1` | API utilities | 0 min | Load only |
| `capture_kibana_screenshots.ps1` | Screenshot guide | 15 min | Manual capture |
| `kibana_reset.ps1` | Clean slate | 3 min | Confirmation only |
| `setup_kibana_complete.ps1` | Full automation | 10 min | Visualizations manual |

---

## 🚀 QUICK START COMMAND

```powershell
# One command to set everything up!
.\scripts\setup_kibana_complete.ps1

# Then follow manual steps in Kibana UI for visualizations
```

---

## ⚡ FASTEST PATH (< 4 hours total)

```powershell
# 1. Verify (2 min)
.\scripts\verify_kibana_setup.ps1

# 2. Generate data (5 min)
.\scripts\generate_and_upload.ps1

# 3. Manual Kibana (180 min)
# - Follow KIBANA_QUICK_START.md steps

# 4. Export & screenshots (20 min)
# - Export JSON
# - Capture 4 screenshots

# Total: 207 minutes (3.5 hours)
```

---

**Status**: All automation scripts ready  
**Next**: Run verification script, then follow KIBANA_QUICK_START.md  
**Time**: 3-4 hours for complete setup
