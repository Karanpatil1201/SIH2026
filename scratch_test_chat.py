import sys
import io
import requests
import json
import time

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000/api"

queries = [
    {"lang": "en", "query": "Is it safe today?", "lat": 18.9667, "lon": 72.8333},
    {"lang": "en", "query": "How are the waves?", "lat": 18.9667, "lon": 72.8333},
    {"lang": "hi", "query": "आज मछली पकड़ना सुरक्षित है?", "lat": 18.9667, "lon": 72.8333},
    {"lang": "mr", "query": "उद्या मासेमारीला जाऊ शकतो का?", "lat": 18.9667, "lon": 72.8333},
    {"lang": "ta", "query": "நாளை மீன்பிடிக்க பாதுகாப்பானதா?", "lat": 13.0827, "lon": 80.2707},
]

print("Testing /api/chat with multiple languages & queries...", flush=True)
for q in queries:
    t0 = time.time()
    try:
        res = requests.post(f"{BASE_URL}/chat", json={
            "query": q["query"],
            "lat": q["lat"],
            "lon": q["lon"],
            "mode": "HYBRID"
        }, timeout=45)
        dt = time.time() - t0
        if res.status_code == 200:
            data = res.json()
            answer = data.get("final_answer", "")
            det_lang = data.get("detected_language", "")
            print(f"\n=======================================================", flush=True)
            print(f"QUERY [{q['lang']}]: {q['query']}", flush=True)
            print(f"STATUS: {res.status_code} | TIME: {dt:.2f}s | DETECTED LANG: {det_lang}", flush=True)
            print(f"ANSWER PREVIEW:\n{answer[:300]}...", flush=True)
            print(f"FULL LENGTH: {len(answer)} chars", flush=True)
            print("=======================================================", flush=True)
        else:
            print(f"FAILED [{q['lang']}]: Status {res.status_code}, Body: {res.text}", flush=True)
    except Exception as e:
        print(f"ERROR [{q['lang']}]: {e}", flush=True)
