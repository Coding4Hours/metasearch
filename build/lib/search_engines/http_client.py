import aiohttp
from collections import namedtuple
from .config import TIMEOUT, PROXY, USER_AGENT
from . import utils as utl

class AsyncHttpClient:
    '''Performs asynchronous HTTP requests. An `aiohttp` wrapper, essentially'''
    def __init__(self, timeout=TIMEOUT, proxy=PROXY):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.proxy = self._set_proxy(proxy)
        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept-Language': 'en-GB,en;q=0.5'
        }
        self.response = namedtuple('response', ['http', 'html'])

    async def get(self, page):
        '''Submits an asynchronous HTTP GET request.'''
        page = self._quote(page)
        try:
            async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
                async with session.get(page, proxy=self.proxy) as req:
                    html = await req.text()
                    self.headers['Referer'] = page
                    return self.response(http=req.status, html=html)
        except aiohttp.ClientError as e:
            return self.response(http=0, html=str(e))

    async def post(self, page, data):
        '''Submits an asynchronous HTTP POST request.'''
        page = self._quote(page)
        try:
            async with aiohttp.ClientSession(headers=self.headers, timeout=self.timeout) as session:
                async with session.post(page, data=data, proxy=self.proxy) as req:
                    html = await req.text()
                    self.headers['Referer'] = page
                    return self.response(http=req.status, html=html)
        except aiohttp.ClientError as e:
            return self.response(http=0, html=str(e))

    def _quote(self, url):
        '''URL-encodes URLs.'''
        if utl.decode_bytes(utl.unquote_url(url)) == utl.decode_bytes(url):
            url = utl.quote_url(url)
        return url

    def _set_proxy(self, proxy):
        '''Returns HTTP or SOCKS proxy string.'''
        if proxy:
            if not utl.is_url(proxy):
                raise ValueError('Invalid proxy format!')
            return proxy
        return None