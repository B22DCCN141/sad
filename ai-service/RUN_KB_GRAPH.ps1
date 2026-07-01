$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (-not (Test-Path "..\.venv\Scripts\python.exe")) {
    throw "Khong tim thay Python venv o ..\.venv\Scripts\python.exe"
}

Write-Host "[1/3] Cai package can thiet..."
& ..\.venv\Scripts\python.exe -m pip install neo4j pandas

Write-Host "[2/3] Chay neo4j graph build..."
# Mac dinh: bolt://localhost:7687, user neo4j, password neo4jpassword
# Co the doi bang env vars:
# $env:NEO4J_URI = 'bolt://localhost:7687'
# $env:NEO4J_USER = 'neo4j'
# $env:NEO4J_PASSWORD = 'your_password'
# $env:NEO4J_DATABASE = 'neo4j'

& ..\.venv\Scripts\python.exe .\build_kb_graph_neo4j.py

Write-Host "[3/3] Hoan tat. Mo Neo4j Browser va chay query trong kb_graph_queries.cypher"
