# PowerShell script to set up and run Snowflake AI Agent

Write-Host "🚀 Snowflake AI Agent Setup Script" -ForegroundColor Blue
Write-Host "=================================" -ForegroundColor Blue

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "requirements.txt")) {
    Write-Host "❌ Please run this script from the snowflake project directory." -ForegroundColor Red
    exit 1
}

Write-Host "📦 Setting up virtual environment..." -ForegroundColor Yellow

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "✅ Virtual environment already exists." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install requirements
Write-Host "📥 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Dependencies installed successfully." -ForegroundColor Green

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚙️ Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️ Please edit .env file with your Snowflake and OpenAI credentials before running the agent." -ForegroundColor Yellow
    
    # Ask if user wants to open .env file
    $openEnv = Read-Host "Would you like to open the .env file now? (y/n)"
    if ($openEnv -eq "y" -or $openEnv -eq "Y") {
        notepad .env
    }
} else {
    Write-Host "✅ .env file already exists." -ForegroundColor Green
}

# Create sessions directory
if (-not (Test-Path "sessions")) {
    New-Item -ItemType Directory -Path "sessions" | Out-Null
    Write-Host "✅ Sessions directory created." -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your credentials" -ForegroundColor White
Write-Host "2. Test connection: python -m src.main test" -ForegroundColor White
Write-Host "3. Run interactive mode: python -m src.main interactive" -ForegroundColor White
Write-Host "4. Or run examples: python examples\example_usage.py" -ForegroundColor White
Write-Host ""

# Ask if user wants to test connection now
$testNow = Read-Host "Would you like to test the connection now? (y/n)"
if ($testNow -eq "y" -or $testNow -eq "Y") {
    Write-Host "🔍 Testing Snowflake connection..." -ForegroundColor Yellow
    python -m src.main test
}

Write-Host ""
Write-Host "Happy querying! 🎯" -ForegroundColor Blue