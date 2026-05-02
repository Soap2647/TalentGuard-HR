"""
n8n dedup array formatını parse et ve raporu göster.
"""
import requests
import json

def dedup_decode(arr):
    """n8n dedup array formatını çöz."""
    if not isinstance(arr, list) or len(arr) < 2:
        return arr
    lookup = arr  # arr[i] = değer, arr[0] = şema

    def resolve(obj):
        if isinstance(obj, str):
            # String index referansı
            try:
                idx = int(obj)
                if 0 <= idx < len(arr):
                    return resolve(arr[idx])
            except ValueError:
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

# Son 3 execution'ı al
r = requests.get(
    'http://localhost:5678/rest/executions',
    headers=headers,
    params={'limit': 3, 'includeData': 'true', 'workflowId': 'TqxLphYwOSyvDwsc'}
)
data = r.json().get('data', {})
execs = data if isinstance(data, list) else data.get('results', [])

for ex in execs[:1]:  # Sadece ilk (en yeni) execution
    print(f"=== Execution {ex['id']} | {ex['status']} | {ex.get('stoppedAt','?')} ===")
    raw = ex.get('data', '')

    if isinstance(raw, str):
        try:
            arr = json.loads(raw)
        except Exception as e:
            print("JSON parse error:", e)
            continue

        resolved = dedup_decode(arr)
        print("Resolved keys:", list(resolved.keys()) if isinstance(resolved, dict) else type(resolved))

        if isinstance(resolved, dict):
            result_data = resolved.get('resultData', {})
            run_data = result_data.get('runData', {})
            print("Nodes:", list(run_data.keys()))

            # Error kontrolü
            err = result_data.get('error')
            if err:
                print("ERROR:", err)

            # Her node için çıktı göster
            for node_name, runs in run_data.items():
                print(f"\n--- Node: {node_name} ---")
                for run_idx, run in enumerate(runs):
                    if not isinstance(run, dict):
                        print(f"  run[{run_idx}] is {type(run)}: {str(run)[:100]}")
                        continue
                    items_arr = run.get('data', {}).get('main', [[]])
                    if items_arr and items_arr[0]:
                        print(f"  {len(items_arr[0])} item(s)")
                        for item in items_arr[0][:2]:  # ilk 2 item
                            j = item.get('json', {}) if isinstance(item, dict) else {}
                            # Rapor varsa göster, yoksa keys
                            if 'report' in j:
                                print("  REPORT:")
                                print(j['report'])
                            elif 'full_name' in j:
                                print(f"  Employee: {j.get('full_name')} churn={j.get('churn_prob')}")
                            elif 'total_employees' in j:
                                print(f"  KPIs: total={j.get('total_employees')} high_risk={j.get('high_risk_count')}")
                            else:
                                print(f"  JSON keys: {list(j.keys())[:5]}")
                    else:
                        print("  No items")
