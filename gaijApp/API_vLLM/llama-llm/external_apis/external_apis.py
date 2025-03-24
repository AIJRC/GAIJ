import requests
import json
from requests.adapters import HTTPAdapter, Retry

API_ENDPOINTS = [
    "https://data.brreg.no/enhetsregisteret/api/enheter/{id}",
    "https://data.brreg.no/enhetsregisteret/api/underenheter/{id}",
    "https://data.brreg.no/enhetsregisteret/api/enheter/{id}/roller",
]


## API helper functions
def create_requests_session():
    session = requests.Session()
    retries = Retry(total=3,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=frozenset(['GET', 'POST','PUT']))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session

def api_endpoint(api_url, method='get', verify=True, data=None, payload=None):
    ''' general function to call an API '''
    session = create_requests_session()
    headers = {
        'Content-type':'application/json', 
        'Accept':'application/json'
    }
    if method == 'get':
        resp = session.get(url=api_url, headers=headers, verify=verify)
    elif method == 'put' and data:
        resp = session.put(url=api_url, data=json.dumps(data), headers=headers)
    elif method == 'post' and payload:
        resp = session.post(url=api_url, json=payload, headers=headers)
    elif method == 'delete':
        resp = session.delete(url=api_url, headers=headers)
    return resp


def run_all_external_apis(id, ext_dir):
    results = []
    for url_template in API_ENDPOINTS:
        url = url_template.format(id=id)
        try:
            response = api_endpoint(url)
            results.append(response.text)
        except Exception as e:
            results.append(f"API call failed for {url}: {e}")
    return "\n".join(results)

# # This is for testing, I tested like python external_apis.py 810059672
# if __name__ == "__main__":
#     import sys

#     if len(sys.argv) < 2:
#         print("Usage: python external_apis.py <org_id> [ext_dir]")
#         sys.exit(1)

#     org_id = sys.argv[1]
#     ext_dir = sys.argv[2] if len(sys.argv) > 2 else "."

#     output = run_all_external_apis(org_id, ext_dir)
#     print(output)