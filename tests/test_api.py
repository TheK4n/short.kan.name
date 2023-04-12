import requests
import time


PROTOCOL = "http://"
API_HOST = "127.0.0.1:8000"
HOST = f"{PROTOCOL}{API_HOST}"


TEST_URL = "https://github.com/thek4n/dotfiles"


def post(data: str, **keys) -> requests.Response:
    headers = {"Content-type": "text/plain"}

    uri = f"{HOST}?"
    for k, v in keys.items():
        uri += f"{k}={v}&"

    resp = requests.post(uri, data=data, headers=headers)
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
    assert expand_url_response.status_code == 301
    expand_url_response_repeated = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response_repeated.status_code == 404


def test_url_lifetime():
    ttl = 5
    short_url_response = post(TEST_URL, ttl=ttl)
    expand_url_response = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response.status_code == 301
    expand_url_response_repeat_0 = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response_repeat_0.status_code == 301
    time.sleep(ttl+1)  # wait for url has expired
    expand_url_response_repeat_1 = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response_repeat_1.status_code == 404


def test_valid_custom_alias():
    alias = "testalias"
    shorten_url = post(TEST_URL, alias=alias, one_time=True).text
    assert shorten_url == f"{API_HOST}/{alias}"

    expand_url_response = expand_url(shorten_url)
    assert expand_url_response.headers["Location"] == TEST_URL

