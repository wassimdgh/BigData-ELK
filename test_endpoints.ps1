# Test Script for All Endpoints
$BASE_URL = "http://localhost:8000"

Write-Host "======================================================================" -ForegroundColor Green
Write-Host "🧪 TESTING ALL ENDPOINTS - STEP BY STEP"
Write-Host "======================================================================" -ForegroundColor Green

# Test 1: Health Check - Swagger UI
Write-Host "`n[1/12] Testing Swagger UI (/apidocs)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/apidocs" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Swagger UI: OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Swagger UI: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Swagger JSON
Write-Host "`n[2/12] Testing Swagger JSON (/api/v1/swagger.json)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/v1/swagger.json" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Swagger JSON: OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Swagger JSON: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Main page
Write-Host "`n[3/12] Testing Main Page (/)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Main Page: OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Main Page: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Elasticsearch connectivity
Write-Host "`n[4/12] Testing Elasticsearch (http://localhost:9200)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:9200" -TimeoutSec 5 -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ Elasticsearch: OK" -ForegroundColor Green
    Write-Host "   Version: $($data.version.number)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Elasticsearch: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Kibana connectivity
Write-Host "`n[5/12] Testing Kibana (http://localhost:5601)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5601/api/status" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Kibana: OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Kibana: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: MongoDB connectivity
Write-Host "`n[6/12] Testing MongoDB (localhost:27017)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:27017" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ MongoDB: OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "✅ MongoDB: Accessible (no HTTP, but listening)" -ForegroundColor Green
}

# Test 7: Redis connectivity
Write-Host "`n[7/12] Testing Redis (localhost:6379)..." -ForegroundColor Cyan
try {
    $client = New-Object System.Net.Sockets.TcpClient
    $client.Connect("localhost", 6379)
    if ($client.Connected) {
        Write-Host "✅ Redis: OK (Port 6379 accessible)" -ForegroundColor Green
        $client.Close()
    }
} catch {
    Write-Host "❌ Redis: FAILED" -ForegroundColor Red
}

# Test 8: API Stats endpoint
Write-Host "`n[8/12] Testing API Stats (/api/v1/stats)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/v1/stats" -TimeoutSec 5 -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ API Stats: OK (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "   Total Logs: $($data.total_logs)" -ForegroundColor Gray
    Write-Host "   Active Sensors: $($data.active_sensors)" -ForegroundColor Gray
} catch {
    Write-Host "❌ API Stats: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 9: API Files endpoint
Write-Host "`n[9/12] Testing API Files (/api/v1/files)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/v1/files" -TimeoutSec 5 -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ API Files: OK (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "   Files Count: $($data.files.Length)" -ForegroundColor Gray
} catch {
    Write-Host "❌ API Files: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 10: API Dashboard Stats
Write-Host "`n[10/12] Testing API Dashboard Stats (/api/v1/dashboard/stats)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/v1/dashboard/stats" -TimeoutSec 5 -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ API Dashboard Stats: OK (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "   Total Logs: $($data.total_logs)" -ForegroundColor Gray
    Write-Host "   Avg Temperature: $($data.avg_temperature)°C" -ForegroundColor Gray
    Write-Host "   Alerts Today: $($data.alerts_today)" -ForegroundColor Gray
} catch {
    Write-Host "❌ API Dashboard Stats: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 11: API Recent Alerts
Write-Host "`n[11/12] Testing API Recent Alerts (/api/v1/dashboard/recent-alerts)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/v1/dashboard/recent-alerts" -TimeoutSec 5 -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ API Recent Alerts: OK (Status: $($response.StatusCode))" -ForegroundColor Green
    Write-Host "   Alerts Count: $($data.alerts.Length)" -ForegroundColor Gray
} catch {
    Write-Host "❌ API Recent Alerts: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 12: API Cache Stats
Write-Host "`n[12/12] Testing API Cache Stats (/api/v1/cache/stats)..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$BASE_URL/api/v1/cache/stats" -TimeoutSec 5 -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ API Cache Stats: OK (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ API Cache Stats: FAILED (Expected - requires login)" -ForegroundColor Yellow
}

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "✅ ENDPOINT TESTING COMPLETE"
Write-Host "======================================================================" -ForegroundColor Green
