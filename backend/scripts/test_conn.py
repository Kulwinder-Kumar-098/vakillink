import http.client
try:
    conn = http.client.HTTPConnection("127.0.0.1", 8000, timeout=2)
    conn.request("GET", "/health")
    resp = conn.getresponse()
    print(f"Status: {resp.status}")
    print(resp.read().decode())
except Exception as e:
    print(f"Error: {e}")
