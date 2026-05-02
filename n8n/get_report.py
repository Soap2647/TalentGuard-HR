"""
Son execution'ın raporunu getir.
"""
import requests
import json

s = requests.Session()
resp = s.post('http://localhost:5678/rest/login', json={
    'emailOrLdapLoginId': 'admin@churn.local',
    'password': 'Admin1234!'
})
token = dict(s.cookies).get('n8n-auth', '')
headers = {'Cookie': f'n8n-auth={token}', 'Content-Type': 'application/json'}

# Son execution'ları listele
r = requests.get(
    'http://localhost:5678/rest/executions',
    headers=headers,
    params={'limit': 5, 'includeData': 'true', 'workflowId': 'TqxLphYwOSyvDwsc'}
)
print("Executions status:", r.status_code)
data = r.json().get('data', {})
execs = data if isinstance(data, list) else data.get('results', [])
print(f"Found {len(execs)} executions")

for ex in execs[:2]:
    print(f"\n--- Execution {ex['id']} | status={ex['status']} ---")
    raw_data = ex.get('data', '')

    # compressed format kontrolü
    if isinstance(raw_data, str):
        # zlib+base64 compressed olabilir
        try:
            import zlib, base64
            decoded = json.loads(zlib.decompress(base64.b64decode(raw_data)))
            raw_data = decoded
        except Exception as e:
            print("  Decompress failed:", e)
            print("  Raw data preview:", str(raw_data)[:200])
            raw_data = {}

    if isinstance(raw_data, dict):
        result_data = raw_data.get('resultData', {})
        run_data = result_data.get('runData', {})
        print(f"  Nodes with data: {list(run_data.keys())[:5]}")

        for node_name, node_runs in run_data.items():
            if 'Rapor' in node_name or '5.' in node_name:
                print(f"\n  === {node_name} OUTPUT ===")
                for run in node_runs:
                    try:
                        data_arr = run.get('data', {}).get('main', [[]])
                        for items in data_arr:
                            for item in (items or []):
                                if isinstance(item, dict):
                                    report = item.get('json', {}).get('report', '')
                                    if report:
                                        print(report)
                    except Exception as e:
                        print("  Parse error:", e)

        err = result_data.get('error')
        if err:
            print("\n  ERROR:", err.get('message', err))
