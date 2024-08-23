import aiohttp
from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT
from ..utils import unquote_url
from bs4 import BeautifulSoup

class Yahoo(SearchEngine):
    '''Searches yahoo.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Yahoo, self).__init__(proxy, timeout)
        self._base_url = 'https://search.yahoo.com'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'div.compTitle h3.title a', 
            'title': 'div.compTitle h3.title', 
            'text': 'div.compText', 
            'links': 'div#web li div.dd.algo.algo-sr', 
            'next': 'a.next'
        }
        return selectors[element]
    
    async def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = u'{}/search?p={}&ei=UTF-8&nojs=1'
        url = url_str.format(self._base_url, self._query)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, proxy=self._proxy, timeout=self._timeout) as response:
                text = await response.text()
                return {'url': url, 'data': text}
    
    async def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page_link = tags.select_one(selector)
        url = self._get_tag_item(next_page_link, 'href') if next_page_link else None
        return {'url': url, 'data': None}

    def _get_url(self, link, item='href'):
        selector = self._selectors('url')
        url = self._get_tag_item(link.select_one(selector), 'href')
        url = url.split(u'/RU=')[-1].split(u'/R')[0]
        return unquote_url(url)

    def _get_title(self, tag, item='text'):
        '''Returns the title of search results items.'''
        title = tag.select_one(self._selectors('title'))
        for span in title.select('span'):
            span.decompose()
        return self._get_tag_item(title, item)

    def _get_tag_item(self, tag, item):
        '''Helper method to extract tag item'''
        if tag:
            return tag.get(item, '').strip()
        return ''
