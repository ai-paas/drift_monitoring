@echo off
cd /d %~dp0..
python -m uvicorn test_feeder_server.app.main:app --host 127.0.0.1 --port 8772
