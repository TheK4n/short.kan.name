import requests


class APIWrapper:

    def __init__(self, host: str):
        self.host = host

    def _make_post_request(self, method: str, body: str, **params) -> requests.Response:
        headers = {"Content-type": "text/plain"}

        uri = f"{self.host}/{method}?"
        for k, v in params.items():
            uri += f"{k}={v}&"

        resp = requests.post(uri, data=body, headers=headers)
        return resp

    def _make_get_request(self, path: str) -> requests.Response:
        uri = f"{self.host}/{path}?"
        return requests.get(uri, allow_redirects=False)

    def short_url(self, body: str, **params) -> requests.Response:
        return self._make_post_request(method="", body=body, **params)

    def expand_url(self, url_alias: str) -> requests.Response:
        return self._make_get_request(url_alias)

