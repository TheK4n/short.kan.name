import time
import requests
from api_wrapper import APIWrapper


PROTOCOL = "http://"
API_HOST = "127.0.0.1:8000"
HOST = f"{PROTOCOL}{API_HOST}"


TEST_URL = "https://github.com/thek4n/dotfiles"


def short_url(url: str, **params) -> requests.Response:
    api = APIWrapper(HOST)
    return api.short_url(body=url, **params)


def expand_url(alias: str) -> requests.Response:
    api = APIWrapper(HOST)
    return api.expand_url(alias)


def test_shorting():
    shorted_url_response = short_url(TEST_URL)
    assert shorted_url_response.text.startswith(API_HOST)


def test_expanding():
    shorted_url_response = short_url(TEST_URL)
    shorted_url_alias = shorted_url_response.text.split("/")[-1]
    expand_url_response = expand_url(shorted_url_alias)
    assert expand_url_response.headers["Location"] == TEST_URL


def test_onetime_url():
    short_url_response = short_url(TEST_URL, one_time=True)
    expand_url_response = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response.status_code == 301
    expand_url_response_repeated = requests.get(f"http://{short_url_response.text}", allow_redirects=False)
    assert expand_url_response_repeated.status_code == 404


def test_url_lifetime():
    ttl = 3
    short_url_response = short_url(TEST_URL, ttl=ttl)
    expand_url_response = expand_url(short_url_response.text.split("/")[-1])
    assert expand_url_response.status_code == 301
    expand_url_response_repeat_0 = expand_url(short_url_response.text.split("/")[-1])
    assert expand_url_response_repeat_0.status_code == 301
    time.sleep(ttl+1)  # wait for url has expired
    expand_url_response_repeat_1 = expand_url(short_url_response.text.split("/")[-1])
    assert expand_url_response_repeat_1.status_code == 404


def test_if_desired_alias_taken_generates_random_url():
    alias = "testalias"
    short_url(TEST_URL, alias=alias, one_time=True)
    shorted_url_response = short_url(TEST_URL, alias=alias, one_time=True)
    shorted_url_alias = shorted_url_response.text.split("/")[-1]
    assert shorted_url_alias != alias

    expand_url_response = expand_url(shorted_url_alias)
    assert expand_url_response.headers["Location"] == TEST_URL

