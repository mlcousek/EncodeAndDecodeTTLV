# TTLV Encoder Test Suite
# PowerShell script to run all tests

Write-Host "TTLV Encoder Test Suite" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Using: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Python not found. Please install Python and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if required files exist
$requiredFiles = @("../encode_ttlv.py", "../decode_ttlv.py", "run_tests.py")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "ERROR: Required file $file not found." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Available test options:" -ForegroundColor Yellow
Write-Host "1. Run all tests (recommended)"
Write-Host "2. Run basic encoder test only"
Write-Host "3. Run comprehensive tests only"
Write-Host "4. Run KMIP protocol tests only"
Write-Host "5. Run specific KMIP test"
Write-Host ""

$choice = Read-Host "Select an option (1-5)"

switch ($choice) {
    "1" {
        Write-Host "Running all tests..." -ForegroundColor Green
        python run_tests.py
    }
    "2" {
        Write-Host "Running basic encoder test..." -ForegroundColor Green
        python run_tests.py basic
    }
    "3" {
        Write-Host "Running comprehensive tests..." -ForegroundColor Green
        python run_tests.py comprehensive
    }
    "4" {
        Write-Host "Running KMIP protocol tests..." -ForegroundColor Green
        python run_tests.py kmip
    }
    "5" {
        Write-Host ""
        Write-Host "Available KMIP tests:" -ForegroundColor Yellow
        Write-Host "- discover (Discover Versions)"
        Write-Host "- discover_batch (Discover Versions with Batch ID)"
        Write-Host "- create (Create Key)"
        Write-Host "- get (Get Key)"
        Write-Host "- getattr (Get Attributes)"
        Write-Host "- activate (Activate Key)"
        Write-Host "- addattr (Add Attribute)"
        Write-Host "- response (Response Structure)"
        $testName = Read-Host "Enter test name"
        Write-Host "Running KMIP test: $testName..." -ForegroundColor Green
        python kmip_protocol_tests.py $testName
    }
    default {
        Write-Host "Invalid choice. Running all tests..." -ForegroundColor Yellow
        python run_tests.py
    }
}

Write-Host ""
Write-Host "Test execution completed!" -ForegroundColor Green
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
