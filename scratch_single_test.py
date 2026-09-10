import requests
import json
import time

res = requests.post("http://localhost:8000/api/chat", json={
    "query": "Is it safe today?",
    "lat": 18.9667,
    "lon": 72.8333,
    "mode": "HYBRID"
}, timeout=35)
print(f"STATUS: {res.status_code}", flush=True)
data = res.json()
print(f"DETECTED LANG: {data.get('detected_language')}", flush=True)
print(f"FINAL ANSWER:\n{data.get('final_answer')}", flush=True)
