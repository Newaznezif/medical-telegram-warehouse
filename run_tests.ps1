# run_tests.ps1 - Run tests with proper Python path
$env:PYTHONPATH = "$PWD;$env:PYTHONPATH"
pytest tests/test_api.py -v
