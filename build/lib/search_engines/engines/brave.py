from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT
import aiohttp

class Brave(SearchEngine):
    '''Searches brave.com'''

    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Brave, self).__init__(proxy, timeout)
        self._base_url = 'https://search.brave.com'
        self._session = aiohttp.ClientSession()

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.result-header[href]', 
            'title': 'a.result-header[href] span.snippet-title', 
            'text': 'div.snippet-content', 
            'links': 'div#results div[data-loc="main"]', 
            'next': {'tag': 'div#pagination a[href]', 'text': 'Next', 'skip': 'disabled'}
        }
        return selectors[element]

    async def _first_page(self):
        '''Returns the initial page and query.'''
        url = f'{self._base_url}/search?q={self._query}&source=web'
        async with self._session.get(url) as response:
            if response.status != 200:
                response.raise_for_status()
            data = await response.text()
        return {'url': url, 'data': data}

    async def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page_tags = [
            tag for tag in tags.select(selector['tag']) 
            if tag.get_text().strip() == selector['text'] and selector['skip'] not in tag.get('class', [])
        ]
        url = None
        if next_page_tags:
            next_page_url = next_page_tags[0]['href']
            url = self._base_url + next_page_url
            async with self._session.get(url) as response:
                if response.status != 200:
                    response.raise_for_status()
                data = await response.text()
            return {'url': url, 'data': data}
        return {'url': url, 'data': None}

    async def close(self):
        '''Closes the HTTP session.'''
        await self._session.close()
