import requests
from test_data import test_inputs

BASE_URL = "http://127.0.0.1:5000"

# Get JWT token for authentication
print("Getting authentication token...")
token_response = requests.post(f"{BASE_URL}/auth/token")

if token_response.status_code != 200:
    print("Failed to get token:", token_response.text)
    exit(1)

token_data = token_response.json()
token = token_data["token"]
headers = {"Authorization": f"Bearer {token}"}

print(f"Token received: {token[:20]}...")

for data in test_inputs:
    print("\nTesting:", data)

    r1 = requests.post(f"{BASE_URL}/describe", json=data, headers=headers)
    print("Describe:", r1.json())

    r2 = requests.post(f"{BASE_URL}/recommend", json=data, headers=headers)
    print("Recommend:", r2.json())

    r3 = requests.post(f"{BASE_URL}/generate-report", json=data, headers=headers)
    print("Report:", r3.json())