from bs4 import BeautifulSoup
import aiohttp

from search_engines.engine import SearchEngine
from search_engines.config import PROXY, TIMEOUT, FAKE_USER_AGENT


class Metager(SearchEngine):
    '''Searches metager.org'''

    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Metager, self).__init__(proxy, timeout)
        self._base_url = 'https://metager.org'
        self.set_headers({'User-Agent': FAKE_USER_AGENT})
        self._session = aiohttp.ClientSession()

    def _selectors(self, element):
        """Returns the appropriate CSS selector."""
        selectors = {
            'url': 'a.result-link',
            'title': 'h2.result-title a',
            'text': 'div.result-description',
            'links': '#results div.result',
            'next': '#next-search-link a',
        }
        return selectors[element]

    async def redirect(self, query):
        '''Redirects initial request to actual result page.'''
        response = await self._get_page(query)
        src_page = BeautifulSoup(response, "html.parser")
        iframe = src_page.select_one('iframe')
        url = iframe.get('src') if iframe else None
        return url

    async def _first_page(self):
        '''Returns the initial page and query.'''
        query = f'{self._base_url}/meta/meta.ger3?eingabe={self._query}'
        url = await self.redirect(query)

        return {'url': url, 'data': None}

    async def _next_page(self, tags):
        '''Returns the next page URL.'''
        next_page = tags.select_one(self._selectors('next'))
        url = None
        if next_page:
            url = await self.redirect(next_page['href'])

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
