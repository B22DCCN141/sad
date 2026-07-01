$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path "..\.venv\Scripts\python.exe")) {
    throw "Khong tim thay Python venv o ..\.venv\Scripts\python.exe"
}

& ..\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
& ..\.venv\Scripts\python.exe -m streamlit run .\kb_graph_chat_app.py
