import requests
import json
import configparser


class COTOHA:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.client_id = config.get('COTOHA_API', 'client_id')
        self.client_secret = config.get('COTOHA_API', "client_secret")
        self.endpoint_url_base = config.get('COTOHA_API', 'endpoint_url_base')
        self.access_token_url = config.get('COTOHA_API', 'access_token_url')
        self.access_token = ''

    def _get_access_token(self):
        # アクセストークンを取得
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        data = {'grantType': 'client_credentials', 'clientId': self.client_id, 'clientSecret': self.client_secret}
        data = json.dumps(data).encode()

        r = requests.post(self.access_token_url, data=data, headers=headers)
        res = json.loads(r.content)

        return res['access_token']

    def _get_header(self, update_access_token=True):
        if update_access_token or not self.access_token:
            self.access_token = self._get_access_token()
        return {'Authorization': 'Bearer ' + self.access_token,
                'Content-Type': 'application/json;charset=UTF-8'}

    def parse(self, sentence, type='', dic_type=[]):
        url = self.endpoint_url_base + "v1/parse"
        data = {'sentence': sentence}
        if type:
            data['type'] = type
        if dic_type:
            data['dic_type'] = dic_type
        data = json.dumps(data).encode()

        r = requests.post(url, data=data, headers=self._get_header())
        res = json.loads(r.content)

        return res.get('result')

    def similarity(self, s1, s2, type=None, dic_type=None):
        url = self.endpoint_url_base + 'v1/similarity'

        data = {'s1': s1, 's2': s2, 'a':''}
        if type:
            data['type'] = type
        if dic_type:
            data['dic_type'] = dic_type
        data = json.dumps(data).encode()

        r = requests.post(url, data=data, headers=self._get_header())
        res = json.loads(r.content)

        return res['result'].get('score', -1)


if __name__ == '__main__':
    a = COTOHA()
    # d = {'sentence': '今日は晴れています'}
    # print(a.parse('今日は晴れています'))
    print(a.similarity('林檎', 'りんご'))