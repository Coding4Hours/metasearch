from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT
from ..utils import unquote_url, quote_url
import aiohttp

class Duckduckgo(SearchEngine):
    '''Searches duckduckgo.com'''

    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Duckduckgo, self).__init__(proxy, timeout)
        self._base_url = 'https://html.duckduckgo.com'
        self._current_page = 1
        self.set_headers({'User-Agent': FAKE_USER_AGENT})
        self._session = aiohttp.ClientSession()

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.result__a',
            'title': 'a.result__a',
            'text': 'a.result__snippet',
            'links': 'div#links div.result',
            'next': 'input[value="next"]'
        }
        return selectors[element]

    async def _first_page(self):
        '''Returns the initial page and query.'''
        url = f'{self._base_url}/html/?q={quote_url(self._query, "")}'
        async with self._session.get(url) as response:
            if response.status != 200:
                response.raise_for_status()
            data = await response.text()
        return {'url': url, 'data': data}

    async def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        self._current_page += 1
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = None
        if next_page:
            url = self._base_url + next_page
            async with self._session.get(url) as response:
                if response.status != 200:
                    response.raise_for_status()
                data = await response.text()
            return {'url': url, 'data': data}
        return {'url': url, 'data': None}

    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results item.'''
        selector = self._selectors('url')
        url = self._get_tag_item(tag.select_one(selector), item)

        if url.startswith('/url?q='):
            url = url.replace('/url?q=', '').split('&sa=')[0]
        return unquote_url(url)

    async def close(self):
        '''Closes the HTTP session.'''
        await self._session.close()
