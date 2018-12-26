# -*- coding: utf-8 -*-

import aiohttp
import json
from json import JSONDecodeError

import requests
# from requests.adapters import HTTPAdapter
# from requests.exceptions import RetryError
from urllib3.exceptions import MaxRetryError
from urllib3.util.retry import Retry
import urllib3

from src import Logger

log = Logger.get_logger()


# headers = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
#     'Accept-Encoding': 'gzip, deflate',
#     'Accept-Language': 'zh-CN,zh;q=0.9',
#     'Cache-Control': 'max-age=0',
#     'Connection': 'keep-alive',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
#     'Chrome/63.0.3239.132 Safari/537.36',
#     }
#
#
# def _init_retry_session(retries=3, backoff_factor=0.3,
#                         status_forcelist=(500, 502, 503, 504), session=None):
#     session = session or requests.Session()
#     retry = Retry(
#         total=retries,
#         backoff_factor=backoff_factor,
#         status_forcelist=status_forcelist,
#         method_whitelist=frozenset(['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'POST'])
#     )
#
#     adapter = requests.adapters.HTTPAdapter(max_retries=retry)
#
#     session.mount('http://', adapter)
#     session.mount('https://', adapter)
#
#     return session
#
#
# def get(url, payload=None):
#     if payload is None:
#         payload = {}
#
#     session = _init_retry_session(retries=5)
#
#     try:
#         response = session.get(url, params=payload)
#     except RetryError as re:
#         log.info("[%s] Response status error, url: %s" % (re.__class__.__name__, url))
#         return {}
#
#     try:
#         ret = response.json()
#     except JSONDecodeError as je:
#         log.info("[%s] Cannot parse the response from url: %s" % (je.__class__.__name__, url))
#         return {}
#
#     return ret
#
#
# def post(url, payload=None):
#     if payload is None:
#         payload = {}
#
#     session = _init_retry_session(retries=5)
#
#     try:
#         response = session.post(url, params=payload)
#     except RetryError as re:
#         log.info("[%s] Response status error, url: %s" % (re.__class__.__name__, url))
#         return {}
#
#     try:
#         ret = response.json()
#     except JSONDecodeError as je:
#         log.info("[%s] Cannot parse the response from url: %s" % (je.__class__.__name__, url))
#         return {}
#
#     return ret


def request(method, url, payload=None, retries=5, backoff_factor=0.3,
            status_forcelist=(500, 502, 503, 504),
            method_whitelist=frozenset(['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'POST']),
            is_json=True):
    payload = payload or {}

    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        method_whitelist=method_whitelist
    )

    http = urllib3.PoolManager()

    try:
        response = http.request(method, url, fields=payload, retries=retry)
    except MaxRetryError as re:
        log.info("HTTP %s requests exceed max retries with url: %s (reason: %r)" % (method, url, re.reason))
        return {}

    if is_json:
        try:
            ret = json.loads(response.data.decode('utf-8'))
        except JSONDecodeError as je:
            log.info("[%s] Cannot parse the response from url: %s" % (je.__class__.__name__, url))
            return {}
        return ret

    return response


def validate_download_url(url):
    response = requests.head(url, allow_redirects=True)
    content_type = response.headers.get('content-type', 0)
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


async def async_request(method, url, payload=None, headers=None, **kwargs):
    req_json = payload if method == 'POST' else None
    url = "%s?%s" % (url, "&".join(["%s=%s" % (k, v) for k, v in payload.items()])) if method == 'GET' else url

    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, json=req_json, headers=headers) as response:
            if kwargs == {}:
                return await response.text(encoding='utf-8')
            else:
                return await response.text(encoding='utf-8'), kwargs
