# ==============================================================================
# run_all.ps1: End-to-End PowerShell Execution Script for Windows
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  GRITO LABS: MARKETING ANALYTICS & ATTRIBUTION FRAMEWORK" -ForegroundColor Cyan
Write-Host "  Executing Full End-to-End Pipeline from Scratch" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[Step 1/5] Checking Python environment..." -ForegroundColor Yellow
python --version

# 2. Generate Synthetic Dataset
Write-Host "`n[Step 2/5] Generating reproducible synthetic dataset (seed=42)..." -ForegroundColor Yellow
python data_generation/generate_data.py

# 3. Ingest Database & Execute SQL Analytics Suite
Write-Host "`n[Step 3/5] Ingesting into SQLite, executing SQL models, and running attribution engines..." -ForegroundColor Yellow
python analysis/run_pipeline.py

# 4. Run Automated Unit Tests
Write-Host "`n[Step 4/5] Running automated pytest suite for Attribution Conservation Law..." -ForegroundColor Yellow
python -m pytest tests/test_attribution.py -v

# 5. Generate Executive PowerPoint Presentation
Write-Host "`n[Step 5/5] Generating 10-slide executive presentation (deck/Marketing_Attribution_Findings.pptx)..." -ForegroundColor Yellow
python deck/generate_deck.py

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host "  PIPELINE EXECUTION COMPLETED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "  - SQLite Database: data/db/marketing_analytics.db" -ForegroundColor Green
Write-Host "  - Executive Deck: deck/Marketing_Attribution_Findings.pptx" -ForegroundColor Green
Write-Host "  - Interactive HTML Dashboard: dashboard/index.html" -ForegroundColor Green
Write-Host "  - Streamlit App: streamlit run dashboard/app.py" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
