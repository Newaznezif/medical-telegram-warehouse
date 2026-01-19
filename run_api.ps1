# run_api.ps1 - Run the API with proper Python path
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
