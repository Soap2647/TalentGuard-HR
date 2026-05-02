"""
n8n workflow'unu manuel çalıştır ve sonucu göster.
"""
import requests
import json
import time

s = requests.Session()
resp = s.post('http://localhost:5678/rest/login', json={
    'emailOrLdapLoginId': 'admin@churn.local',
    'password': 'Admin1234!'
})
token = dict(s.cookies).get('n8n-auth', '')
headers = {'Cookie': f'n8n-auth={token}', 'Content-Type': 'application/json'}

# Workflow detaylarını çek
r = requests.get('http://localhost:5678/rest/workflows/TqxLphYwOSyvDwsc', headers=headers)
wf = r.json()['data']

print("Nodes:")
for n in wf['nodes']:
    print(f"  [{n['id']}] type={n['type'].split('.')[-1]} name={n['name']!r}")

# Schedule trigger node'u bul
trigger_node = None
for n in wf['nodes']:
    if 'scheduleTrigger' in n['type'] or 'manualTrigger' in n['type']:
        trigger_node = n
        break

print("\nTrigger node:", trigger_node['name'] if trigger_node else "NONE")

# Manuel run için startNodes lazım
# n8n v1 API: POST /rest/workflows/{id}/run with startNodes
body = {
    "startNodes": [],
    "destinationNode": ""
}

if trigger_node:
    body["startNodes"] = [trigger_node['name']]

print("\nRunning with body:", json.dumps(body))
r2 = requests.post(
    'http://localhost:5678/rest/workflows/TqxLphYwOSyvDwsc/run',
    headers=headers,
    json=body
)
print("Run status:", r2.status_code)
if r2.status_code == 200:
    exec_id = r2.json().get('data', {}).get('executionId', '')
    print("Execution ID:", exec_id)

    # Sonucu bekle
    print("Sonuç bekleniyor...")
    for i in range(30):
        time.sleep(2)
        er = requests.get(
            f'http://localhost:5678/rest/executions/{exec_id}',
            headers=headers,
            params={'includeData': 'true'}
        )
        if er.status_code == 200:
            edata = er.json().get('data', {})
            status = edata.get('status', '?')
            print(f"  [{i+1}] status={status}")
            if status in ('success', 'error', 'crashed'):
                # Code node output'unu bul
                exec_data = edata.get('data', {})
                result_data = exec_data.get('resultData', {})
                run_data = result_data.get('runData', {})

                # node-summary / Rapor Oluştur node'unu bul
                for node_name, node_runs in run_data.items():
                    if 'Rapor' in node_name or 'summary' in node_name.lower():
                        print(f"\n=== {node_name} OUTPUT ===")
                        for run in node_runs:
                            data_arr = run.get('data', {}).get('main', [[]])
                            for items in data_arr:
                                for item in (items or []):
                                    if isinstance(item, dict):
                                        report = item.get('json', {}).get('report', '')
                                        if report:
                                            print(report)
                break
        else:
            print(f"  [{i+1}] fetch error {er.status_code}")
else:
    print("Error:", r2.text[:500])
