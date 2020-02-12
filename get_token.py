import requests

try:
    from secret import CLIENT_SECRET, CODE

except ModuleNotFoundError:
    print('Файл с секретным ключом отсутствует, требуется ключ')

AUTH_URL = 'https://oauth.vk.com/authorize'
TOKEN_URL ='https://oauth.vk.com/access_token'

CLIENT_ID = '7299637'

params_code = {'client_id': CLIENT_ID,
        'redirect_uri': 'https://homutovan.github.io',
        'display': 'mobile',
        'response_type': 'code',
        'scope': 'offline',
        'v': '1.03'
        }

params_token = {'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': 'https://homutovan.github.io',
                'code': CODE,
                'scope': 'offline'
                }

#response_code = requests.get(AUTH_URL, params = params_code)
#response_token = requests.get(TOKEN_URL, params = params_token)
#print(response_code.request.url)
#webbrowser.open(response_code.request.url, new = 1, autoraise = True)
#######TOKEN = response_token.json()['access_token']##############################
#print(response_token.json()['access_token'])
#webbrowser.open(response_token.request.url, new = 1, autoraise = True)