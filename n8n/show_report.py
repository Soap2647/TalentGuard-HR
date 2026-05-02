"""
Execution 7 rapor node'unu çıkar.
"""
import requests, json

def dedup_decode(arr):
    if not isinstance(arr, list):
        return arr
    def resolve(obj):
        if isinstance(obj, str):
            try:
                idx = int(obj)
                if 0 < idx < len(arr):
                    return resolve(arr[idx])
            except (ValueError, TypeError):
                pass
            return obj
        elif isinstance(obj, dict):
            return {k: resolve(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [resolve(v) for v in obj]
        else:
            return obj
    return resolve(arr[0])

s = requests.Session()
s.post('http://localhost:5678/rest/login', json={
    'emailOrLdapLoginId': 'admin@churn.local',
    'password': 'Admin1234!'
})
token = dict(s.cookies).get('n8n-auth', '')
headers = {'Cookie': f'n8n-auth={token}'}

r = requests.get('http://localhost:5678/rest/executions/7',
                 headers=headers, params={'includeData': 'true'})
raw = r.json()['data']['data']
arr = json.loads(raw)
resolved = dedup_decode(arr)
run_data = resolved['resultData']['runData']

for node_name, runs in run_data.items():
    run = runs[0]
    if not isinstance(run, dict):
        continue
    main = run.get('data', {}).get('main', [[]])
    items = main[0] if main else []
    if not items:
        continue
    j = items[0].get('json', {}) if isinstance(items[0], dict) else {}

    if 'report' in j:
        print("=" * 60)
        print(j['report'])
        print("=" * 60)
    elif 'full_name' in j:
        print(f"[{node_name}] {len(items)} çalışan | ilk: {j.get('full_name')} churn={j.get('churn_prob')}")
    elif 'total_employees' in j:
        print(f"[{node_name}] KPI: total={j.get('total_employees')} high_risk={j.get('high_risk_count')}")
    elif 'access_token' in j:
        print(f"[{node_name}] Login OK")
    elif 'processed' in j:
        print(f"[{node_name}] Batch: {j.get('processed')} OK / {j.get('failed')} FAIL")
    else:
        print(f"[{node_name}] keys={list(j.keys())[:5]}")
