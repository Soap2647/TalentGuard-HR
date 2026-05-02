"""
n8n execution data - dedup array formatını handle et.
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

# Execution 7'yi getir
r = requests.get(
    'http://localhost:5678/rest/executions/7',
    headers=headers,
    params={'includeData': 'true'}
)
print("Status:", r.status_code)
ex = r.json().get('data', {})
print("Keys:", list(ex.keys()))

raw_data = ex.get('data', '')
print("data type:", type(raw_data).__name__)
if isinstance(raw_data, str):
    print("data length:", len(raw_data))
    print("first 100:", raw_data[:100])
elif isinstance(raw_data, dict):
    print("data keys:", list(raw_data.keys()))

# n8n "dedup" compressed format
# Format: base64(zlib(json_string)) OR
# n8n uses msgpack+dedup - let's try raw base64 decode
if isinstance(raw_data, str) and raw_data:
    import base64, zlib
    # padding ekle
    padded = raw_data + '=' * (4 - len(raw_data) % 4)
    try:
        raw_bytes = base64.b64decode(padded)
        print("Decoded bytes (first 20):", raw_bytes[:20])
        # zlib magic bytes: 0x789c, 0x7801, 0x78da
        if raw_bytes[:2] in (b'\x78\x9c', b'\x78\x01', b'\x78\xda'):
            decompressed = zlib.decompress(raw_bytes)
            data_json = json.loads(decompressed)
            print("Decompressed! Keys:", list(data_json.keys())[:5])
            rdata = data_json.get('resultData', {}).get('runData', {})
            print("runData nodes:", list(rdata.keys()))
            for node_name, runs in rdata.items():
                if 'Rapor' in node_name or '5.' in node_name:
                    print(f"\n=== {node_name} ===")
                    for run in runs:
                        items = run.get('data', {}).get('main', [[]])[0] or []
                        for item in items:
                            r_text = item.get('json', {}).get('report', '')
                            if r_text:
                                print(r_text)
        else:
            # Maybe it's already JSON after base64
            try:
                data_json = json.loads(raw_bytes)
                print("JSON after base64 decode! Keys:", list(data_json.keys()))
            except Exception as e2:
                print("Not JSON either:", e2)
                print("Raw bytes hex:", raw_bytes[:30].hex())
    except Exception as e:
        print("Base64 decode error:", e)
