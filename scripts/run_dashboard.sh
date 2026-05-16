#!/bin/bash
# Start Streamlit dashboard
cd "$(dirname "$0")/.."
streamlit run dashboard/app.py --server.port 8501
