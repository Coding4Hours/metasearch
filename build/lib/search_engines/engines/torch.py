import aiohttp
from bs4 import BeautifulSoup

from ..engine import SearchEngine
from ..config import TOR, TIMEOUT
from .. import output as out


class Torch(SearchEngine):
    '''Uses torch search engine. Requires TOR proxy.'''
    def __init__(self, proxy=TOR, timeout=TIMEOUT):
        super(Torch, self).__init__(proxy, timeout)
        self._base_url = u'http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion'
        if not proxy:
            out.console('Torch requires TOR proxy!', level=out.Level.warning)
        self._current_page = 1
        self._session = aiohttp.ClientSession()  # Initialize aiohttp session with proxy

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'h5 a[href]', 
            'title': 'h5 a[href]', 
            'text': 'p', 
            'links': 'div.result.mb-3', 
            'next': 'ul.pagination a.page-link'
        }
        return selectors[element]
    
    async def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = u'{}/search?query={}&action=search'
        url = url_str.format(self._base_url, self._query)
        response = await self._get_page(url)
        return {'url': url, 'data': None}
    
    async def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        self._current_page += 1
        url_str = u'{}/search?query={}&page={}'
        url = url_str.format(self._base_url, self._query, self._current_page)
        response = await self._get_page(url)
        return {'url': url, 'data': None}
    
    async def _get_page(self, url, data=None):
        '''Gets a page asynchronously using aiohttp with TOR.'''
        async with self._session.get(url, proxy=self.proxy, timeout=self.timeout) as response:
            if response.status != 200:
                response.raise_for_status()
            return await response.text()

    async def close(self):
        '''Closes the aiohttp session.'''
        await self._session.close()
