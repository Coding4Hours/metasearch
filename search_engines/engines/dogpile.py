from ..engine import AsyncSearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT
from ..utils import unquote_url
import aiohttp

class Dogpile(AsyncSearchEngine):
    '''Searches dogpile.com'''

    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Dogpile, self).__init__(proxy, timeout)
        self._base_url = 'https://www.dogpile.com'
        self.set_headers({'User-Agent': FAKE_USER_AGENT})
        self._session = aiohttp.ClientSession()

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a[class$=title]', 
            'title': 'a[class$=title]', 
            'text': {'tag': 'span', 'index': -1}, 
            'links': 'div[class^=web-] div[class$=__result]', 
            'next': 'a.pagination__num--next'
        }
        return selectors[element]

    async def _first_page(self):
        '''Returns the initial page and query.'''
        url = f'{self._base_url}/serp?q={self._query}'
        async with self._session.get(url) as response:
            if response.status != 200:
                response.raise_for_status()
            data = await response.text()
        return {'url': url, 'data': data}

    async def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._base_url + next_page) if next_page else None
        if url:
            async with self._session.get(url) as response:
                if response.status != 200:
                    response.raise_for_status()
                data = await response.text()
            return {'url': url, 'data': data}
        return {'url': url, 'data': None}

    def _get_text(self, tag, item='text'):
        '''Returns the text of search results items.'''
        selector = self._selectors('text')
        tag = tag.select(selector['tag'])[selector['index']]
        return self._get_tag_item(tag, 'text')

    async def close(self):
        '''Closes the HTTP session.'''
        await self._session.close()
