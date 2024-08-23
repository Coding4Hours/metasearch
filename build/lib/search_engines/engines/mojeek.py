from bs4 import BeautifulSoup
import aiohttp

from search_engines.engine import SearchEngine
from search_engines.config import PROXY, TIMEOUT, FAKE_USER_AGENT


class Mojeek(SearchEngine):
    '''Searches mojeek.com'''

    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Mojeek, self).__init__(proxy, timeout)
        self._base_url = 'https://www.mojeek.com'
        self.set_headers({'User-Agent': FAKE_USER_AGENT})
        self._session = aiohttp.ClientSession()

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.ob[href]',
            'title': 'a.ob[href]',
            'text': 'p.s',
            'links': 'ul.results-standard > li',
            'next': {'href': 'div.pagination li a[href]', 'text': 'Next'}
        }
        return selectors[element]

    async def _first_page(self):
        '''Returns the initial page and query.'''
        url = f'{self._base_url}/search?q={self._query}'
        return {'url': url, 'data': None}

    async def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = [
            i['href'] for i in tags.select(selector['href'])
            if i.text == selector['text']
        ]
        url = (self._base_url + next_page[0]) if next_page else None
        return {'url': url, 'data': None}

    async def _get_page(self, page, data=None):
        '''Gets a page asynchronously using aiohttp.'''
        async with self._session.get(page, params=data) as response:
            if response.status != 200:
                response.raise_for_status()
            return await response.text()

    async def close(self):
        '''Closes the aiohttp session.'''
        await self._session.close()
