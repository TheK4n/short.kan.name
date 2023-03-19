import requests
import time


PROTOCOL = "http://"
API_HOST = "127.0.0.1:8000"
HOST = f"{PROTOCOL}{API_HOST}"


TEST_URL = "https://github.com/thek4n/dotfiles"


def post(data: str, one_time: bool = False, ttl: int = 60) -> requests.Response:
    headers = {"Content-type": "text/plain"}
    resp = requests.post(f"{HOST}?ttl={ttl}&{'one-time=true' if one_time else ''}", data=data, headers=headers)
    return resp


def short_url(url: str) -> str:
    resp = post(url)
    return resp.text


def expand_url(url: str) -> requests.Response:
    return requests.get(f"{PROTOCOL}{url}", allow_redirects=False)


def test_shorting():
    shorted_url = short_url(TEST_URL)
    assert shorted_url.startswith(API_HOST)


def test_expanding():
    shorted_url = short_url(TEST_URL)
    expand_url_response = expand_url(shorted_url)
    assert expand_url_response.headers["Location"] == TEST_URL


def test_onetime_url():
    short_url_response = post(TEST_URL, one_time=True)
    expand_url_response = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response.status_code == 303
    expand_url_response_repeated = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response_repeated.status_code == 404


def test_url_lifetime():
    ttl = 5
    short_url_response = post(TEST_URL, ttl=ttl)
    expand_url_response = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response.status_code == 303
    expand_url_response_repeat_0 = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response_repeat_0.status_code == 303
    time.sleep(ttl+1)  # wait for url has expired
    expand_url_response_repeat_1 = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response_repeat_1.status_code == 404

