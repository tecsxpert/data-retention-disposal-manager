import requests

from test_data import test_inputs


BASE_URL = "http://127.0.0.1:5000"


def main():
    for data in test_inputs:
        print("\nTesting:", data)

        describe_response = requests.post(f"{BASE_URL}/describe", json=data, timeout=10)
        print("Describe:", describe_response.json())

        recommend_response = requests.post(f"{BASE_URL}/recommend", json=data, timeout=10)
        print("Recommend:", recommend_response.json())

        report_response = requests.post(f"{BASE_URL}/generate-report", json=data, timeout=10)
        print("Report:", report_response.json())


if __name__ == "__main__":
    main()
