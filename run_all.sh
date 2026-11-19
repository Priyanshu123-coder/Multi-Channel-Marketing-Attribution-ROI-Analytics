#!/usr/bin/env bash
# ==============================================================================
# run_all.sh: End-to-End Execution Script for Grito Labs Attribution Framework
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status

echo "======================================================================"
echo "  GRITO LABS: MARKETING ANALYTICS & ATTRIBUTION FRAMEWORK"
echo "  Executing Full End-to-End Pipeline from Scratch"
echo "======================================================================"

# 1. Check Python
echo "[Step 1/5] Checking Python environment..."
python --version

# 2. Generate Synthetic Dataset
echo -e "\n[Step 2/5] Generating reproducible synthetic dataset (seed=42)..."
python data_generation/generate_data.py

# 3. Ingest Database & Execute SQL Analytics Suite
echo -e "\n[Step 3/5] Ingesting into SQLite, executing SQL models, and running attribution engines..."
python analysis/run_pipeline.py

# 4. Run Automated Unit Tests
echo -e "\n[Step 4/5] Running automated pytest suite for Attribution Conservation Law..."
python -m pytest tests/test_attribution.py -v

# 5. Generate Executive PowerPoint Presentation
echo -e "\n[Step 5/5] Generating 10-slide executive presentation (deck/Marketing_Attribution_Findings.pptx)..."
python deck/generate_deck.py

echo -e "\n======================================================================"
echo "  PIPELINE EXECUTION COMPLETED SUCCESSFULLY!"
echo "  - SQLite Database: data/db/marketing_analytics.db"
echo "  - Executive Deck: deck/Marketing_Attribution_Findings.pptx"
echo "  - Interactive HTML Dashboard: dashboard/index.html"
echo "  - Streamlit App: streamlit run dashboard/app.py"
echo "======================================================================"
