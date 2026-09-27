# CatVTON Quick Starter (Windows PowerShell, ASCII only)
$ErrorActionPreference = "Stop"

function info($m){ Write-Host $m -ForegroundColor Cyan }
function warn($m){ Write-Host $m -ForegroundColor Yellow }
function ok($m){ Write-Host $m -ForegroundColor Green }
function err($m){ Write-Host $m -ForegroundColor Red }

info "=================================="
info "CatVTON Quick Start (Windows)"
info "=================================="
Write-Host ""

# ---- Helpers ----
function Test-PyImport($module){
  & python -c "import $module" 2>$null
  if ($LASTEXITCODE -eq 0){ return $true } else { return $false }
}

# ---- 1) Dependencies ----
function Check-Dependencies {
  info "[1/4] Checking dependencies..."

  if (-not (Test-PyImport "flask")) {
    warn "Flask not found. Installing..."
    & python -m pip install flask flask-cors
  }

  if (-not (Test-PyImport "torch")) {
    err "PyTorch not found."
    Write-Host "Install: python -m pip install torch torchvision"
    throw "Missing dependency: torch"
  }

  if (-not (Test-PyImport "PIL")) {
    warn "Pillow not found. Installing..."
    & python -m pip install pillow
  }

  if (-not (Test-PyImport "cv2")) {
    warn "OpenCV not found. Installing..."
    & python -m pip install opencv-python
  }

  ok "Dependencies OK."
  Write-Host ""
}

# ---- 2) Test data ----
function Prepare-Test-Data {
  info "[2/4] Preparing test data..."
  if (-not (Test-Path "test_data\garments")) {
    warn "No test_data/garments folder."
    Write-Host "Choose:"
    Write-Host "  1) Auto collect via data_collector.py"
    Write-Host "  2) Create folders and add images manually"
    Write-Host "  3) Skip"
    $choice = Read-Host "Select (1/2/3)"
    switch ($choice) {
      "1" { & python data_collector.py }
      "2" {
        New-Item -ItemType Directory -Force -Path "test_data\garments\tops" | Out-Null
        New-Item -ItemType Directory -Force -Path "test_data\garments\outers" | Out-Null
        New-Item -ItemType Directory -Force -Path "test_data\garments\bottoms" | Out-Null
        New-Item -ItemType Directory -Force -Path "test_data\garments\dresses" | Out-Null
        New-Item -ItemType Directory -Force -Path "test_data\models\full_body" | Out-Null
        Write-Host "Add images, then press Enter..."
        Read-Host | Out-Null
      }
      "3" { warn "Proceeding without test data." }
      default { throw "Invalid selection." }
    }
  } else {
    ok "Test data found."
  }
  Write-Host ""
}

# ---- 3) Start server ----
$Global:ServerProcess = $null
function Start-Server {
  info "[3/4] Starting server..."
  Write-Host "Choose server:"
  Write-Host "  1) server.py"
  Write-Host "  2) server_enhanced.py (recommended)"
  $sel = Read-Host "Select (1/2)"
  $scriptFile = if ($sel -eq "1") { "server.py" } elseif ($sel -eq "2") { "server_enhanced.py" } else { $null }
  if (-not $scriptFile) { throw "Invalid selection." }

  ok ("Launching " + $scriptFile + " ...")
  $Global:ServerProcess = Start-Process -FilePath "python" -ArgumentList $scriptFile -PassThru -WindowStyle Hidden

  Write-Host "Waiting for health check (http://localhost:5000/health) ..."
  $healthy = $false
  for ($i=0; $i -lt 30; $i++) {
    try {
      Invoke-WebRequest -UseBasicParsing -Uri "http://localhost:5000/health" -TimeoutSec 2 | Out-Null
      $healthy = $true
      break
    } catch {
      Start-Sleep -Seconds 1
    }
  }

  if ($healthy) {
    ok "Server is up at http://localhost:5000"
  } else {
    err "Server failed to start."
    if ($Global:ServerProcess -and -not $Global:ServerProcess.HasExited) {
      $Global:ServerProcess.Kill()
      $Global:ServerProcess.WaitForExit() | Out-Null
    }
    throw "Server start failed."
  }
  Write-Host ""
}

# ---- 4) Performance test ----
function Run-Performance-Test {
  info "[4/4] Performance test..."
  $run = Read-Host "Run performance_test.py ? (y/n)"
  if ($run -match '^(y|Y)$') {
    & python performance_test.py

    ok "Performance test done."
    Write-Host "Results folder: test_data\results"

    $latest = Get-ChildItem -Path "test_data\results" -Filter "report_*.json" -ErrorAction SilentlyContinue |
              Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest) {
      Write-Host ("Latest report: " + $latest.FullName)
      try {
        $data = Get-Content $latest.FullName -Raw | ConvertFrom-Json
        if ($data.summary) {
          $s = $data.summary
          Write-Host ("Total tests: " + $s.total_tests)
          Write-Host ("Success rate: " + $s.success_rate)
          Write-Host ("Avg time: " + $s.avg_time)
          Write-Host ("Avg quality: " + $s.avg_quality)
        }
      } catch {
        warn "Could not read JSON summary."
      }
    }
  } else {
    warn "Skipped performance test."
  }
  Write-Host ""
}

# ---- Cleanup ----
function Cleanup {
  info "Cleaning up..."
  if ($Global:ServerProcess -and -not $Global:ServerProcess.HasExited) {
    Write-Host "Stopping server..."
    $Global:ServerProcess.Kill()
    $Global:ServerProcess.WaitForExit() | Out-Null
    ok "Server stopped."
  }
  info "All done."
}

# ---- Main ----
try {
  Write-Host ("Python: " + (& python -c "import sys; print(sys.executable)"))
  Check-Dependencies
  Prepare-Test-Data
  Start-Server
  Run-Performance-Test
} finally {
  Cleanup
}
