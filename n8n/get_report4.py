"""
Execution 7'yi direkt çek, dedup parse et.
"""
import requests
import json

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
resp = s.post('http://localhost:5678/rest/login', json={
    'emailOrLdapLoginId': 'admin@churn.local',
    'password': 'Admin1234!'
})
token = dict(s.cookies).get('n8n-auth', '')
headers = {'Cookie': f'n8n-auth={token}', 'Content-Type': 'application/json'}

# Execution 7 - direkt fetch
r = requests.get(
    'http://localhost:5678/rest/executions/7',
    headers=headers,
    params={'includeData': 'true'}
)
print("Status:", r.status_code)
ex = r.json().get('data', {})
raw = ex.get('data', '')

print("data length:", len(raw) if raw else 0)
print("data[:150]:", str(raw)[:150])

if raw:
    arr = json.loads(raw)
    print("Array length:", len(arr))
    print("arr[0] type:", type(arr[0]))
    print("arr[0] keys:", list(arr[0].keys()) if isinstance(arr[0], dict) else "N/A")

    resolved = dedup_decode(arr)
    if isinstance(resolved, dict):
        result_data = resolved.get('resultData', {})
        run_data = result_data.get('runData', {})
        print("\nNodes with data:", list(run_data.keys()))

        # Error
        err = result_data.get('error')
        if err:
            print("ERROR:", err)

        # Report node
        for node_name, runs in run_data.items():
            print(f"\n[{node_name}]")
            for run in runs:
                if not isinstance(run, dict):
                    continue
                main = run.get('data', {}).get('main', [[]])
                items = main[0] if main else []
                if not items:
                    print("  (empty)")
                    continue
                print(f"  {len(items)} item(s)")
                item0 = items[0] if items else {}
                j = item0.get('json', {}) if isinstance(item0, dict) else {}
                if 'report' in j:
                    print("\n" + "="*50)
                    print(j['report'])
                    print("="*50)
                elif j:
                    keys = list(j.keys())
                    print(f"  json keys: {keys[:8]}")
                    if 'full_name' in j:
                        print(f"  -> {j.get('full_name')} | churn={j.get('churn_prob'):.3f}")
                    elif 'total_employees' in j:
                        print(f"  -> total={j.get('total_employees')} high_risk={j.get('high_risk_count')}")
                    elif 'access_token' in j:
                        print(f"  -> token_prefix: {str(j.get('access_token',''))[:20]}...")
