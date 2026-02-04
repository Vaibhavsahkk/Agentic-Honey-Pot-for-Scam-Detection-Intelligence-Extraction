
$mock = Start-Job -ScriptBlock { Set-Location D:\HACKATHON; d:\HACKATHON\venv\Scripts\python.exe d:\HACKATHON\mock_guvi_server.py }
Write-Host "Mock server started..."

$api = Start-Job -ScriptBlock { Set-Location D:\HACKATHON; d:\HACKATHON\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8010 }
Write-Host "API server started..."

Start-Sleep -Seconds 10

Receive-Job -Job $api -Keep
Receive-Job -Job $mock -Keep

Write-Host "Running test..."
d:\HACKATHON\venv\Scripts\python.exe d:\HACKATHON\run_test.py

Write-Host "Cleaning up..."
Stop-Job $mock
Stop-Job $api
