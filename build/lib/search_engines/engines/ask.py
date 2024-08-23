from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT
import aiohttp

class Ask(SearchEngine):
    '''Searches ask.com'''
    
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Ask, self).__init__(proxy, timeout)
        self._base_url = 'https://uk.ask.com'
        self._session = aiohttp.ClientSession()
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.PartialSearchResults-item-title-link.result-link', 
            'title': 'a.PartialSearchResults-item-title-link.result-link', 
            'text': 'p.PartialSearchResults-item-abstract', 
            'links': 'div.PartialSearchResults-body div.PartialSearchResults-item', 
            'next': 'li.PartialWebPagination-next a[href]'
        }
        return selectors[element]
    
    async def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = '{}/web?o=0&l=dir&qo=serpSearchTopBox&q={}'
        url = url_str.format(self._base_url, self._query)
        async with self._session.get(url) as response:
            if response.status != 200:
                response.raise_for_status()
            data = await response.text()
        return {'url': url, 'data': data}
    
    async def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        next_page = tags.select_one(self._selectors('next'))
        url = None
        if next_page:
            url = self._base_url + next_page['href']
            async with self._session.get(url) as response:
                if response.status != 200:
                    response.raise_for_status()
                data = await response.text()
            return {'url': url, 'data': data}
        return {'url': url, 'data': None}

    async def close(self):
        '''Closes the HTTP session.'''
        await self._session.close()
