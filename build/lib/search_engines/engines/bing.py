from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT
import aiohttp

class Bing(SearchEngine):
    '''Searches bing.com'''

    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Bing, self).__init__(proxy, timeout)
        self._base_url = 'https://www.bing.com'
        self._headers = {'User-Agent': FAKE_USER_AGENT}
        self._session = aiohttp.ClientSession()

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'div.b_attribution cite', 
            'title': 'h2', 
            'text': 'p', 
            'links': 'ol#b_results > li.b_algo', 
            'next': 'div#b_content nav[role="navigation"] a.sb_pagN'
        }
        return selectors[element]
    
    async def _first_page(self):
        '''Returns the initial page and query.'''
        url = f'{self._base_url}/search?q={self._query}&search=&form=QBLH'
        async with self._session.get(url, headers=self._headers) as response:
            if response.status != 200:
                response.raise_for_status()
            data = await response.text()
        return {'url': url, 'data': data}
    
    async def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page_tag = tags.select_one(selector)
        next_page_href = next_page_tag['href'] if next_page_tag else None
        url = None
        if next_page_href:
            url = self._base_url + next_page_href
            async with self._session.get(url, headers=self._headers) as response:
                if response.status != 200:
                    response.raise_for_status()
                data = await response.text()
            return {'url': url, 'data': data}
        return {'url': url, 'data': None}

    async def _get_url(self, tag, item='href'):
        '''Returns the URL of search results items.'''
        return super(Bing, self)._get_url(tag, 'text')

    async def close(self):
        '''Closes the HTTP session.'''
        await self._session.close()
