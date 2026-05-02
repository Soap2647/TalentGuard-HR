"""
n8n workflow manuel run - workflowData ile tam body.
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

# Workflow verisini çek
r = requests.get('http://localhost:5678/rest/workflows/TqxLphYwOSyvDwsc', headers=headers)
wf = r.json()['data']

# startNodes için node objesi gerekiyor
trigger = None
for n in wf['nodes']:
    if 'scheduleTrigger' in n['type']:
        trigger = n
        break

# n8n v1 runManually body formatı:
# { workflowData: { ... }, startNodes: [{ name, sourceData: null }], destinationNode: '' }
body = {
    "workflowData": wf,
    "startNodes": [{"name": trigger['name'], "sourceData": None}] if trigger else [],
    "destinationNode": ""
}

print("POST /run ...")
r2 = requests.post(
    'http://localhost:5678/rest/workflows/TqxLphYwOSyvDwsc/run',
    headers=headers,
    json=body
)
print("Status:", r2.status_code)
print("Body:", r2.text[:400])

if r2.status_code == 200:
    exec_id = r2.json().get('data', {}).get('executionId', '')
    print("Execution ID:", exec_id)
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
                exec_data = edata.get('data', {})
                result_data = exec_data.get('resultData', {})
                run_data = result_data.get('runData', {})
                for node_name, node_runs in run_data.items():
                    if 'Rapor' in node_name or '5.' in node_name:
                        print(f"\n=== {node_name} ===")
                        for run in node_runs:
                            data_arr = run.get('data', {}).get('main', [[]])
                            for items in data_arr:
                                for item in (items or []):
                                    if isinstance(item, dict):
                                        report = item.get('json', {}).get('report', '')
                                        if report:
                                            print(report)
                if status == 'error':
                    err = result_data.get('error', {})
                    print("ERROR:", err.get('message', '?'))
                    print("Node:", err.get('node', {}).get('name', '?'))
                break
