import requests

ENDPOINT_OAUTH = 'https://api.yeeloc.com/oauth/access_token'
ENDPOINT_LOCKS = 'https://api.yeeloc.com/lock'
CLIENT_ID = 'yeeloc'
CLIENT_SECRET = 'adb03414981961952ccf40a1b4031d12'


def get_access_token(zone: str, username: str, password: str) -> str:
    params = {
        'grant_type': 'password',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'username': username,
        'password': password,
        'zone': zone
    }

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    response = requests.post(ENDPOINT_OAUTH, params=params, headers=headers)

    try:
        return response.json()['access_token']
    except KeyError:
        raise ValueError("Invalid response from server, received: " + str(response.json()))


def get_locks(access_token: str):
    response = requests.get(ENDPOINT_LOCKS, headers={'Authorization': 'Bearer ' + access_token}).json()

    result = []

    for row in response:
        result.append({
            'name': row['lock_name'],
            'sn': row['lock_sn'],
            'sign_key': row['ble_sign_key'],
            'unlock_count': row['unlock_times'],
            'add_time': row['add_time']
        })

    return result

