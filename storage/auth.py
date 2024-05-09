# auth.py
import json
import requests
import secret


def get_token(auth_url, tenant_id, username, password):
    """인증 서비스에서 액세스 토큰을 요청하는 함수"""
    token_url = auth_url + '/tokens'
    req_header = {'Content-Type': 'application/json'}
    req_body = {
        'auth': {
            'tenantId': tenant_id,
            'passwordCredentials': {
                'username': username,
                'password': password
            }
        }
    }

    response = requests.post(token_url, headers=req_header, json=req_body)
    token_data = response.json()

    # token의 id와 expires 필드만 추출하여 반환
    token_info = {
        "id": token_data["access"]["token"]["id"],
        "expires": token_data["access"]["token"]["expires"]
    }

    return token_info


if __name__ == '__main__':
    AUTH_URL = secret.object_storage_auth_url
    TENANT_ID = secret.object_storage_tenant_id
    USERNAME = secret.object_storage_username
    PASSWORD = secret.object_storage_password

    token = get_token(AUTH_URL, TENANT_ID, USERNAME, PASSWORD)
    print(json.dumps(token, indent=4))
