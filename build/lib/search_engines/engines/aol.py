from .yahoo import Yahoo
from ..config import PROXY, TIMEOUT
import aiohttp

class Aol(Yahoo):
    '''Searches aol.com'''
    
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Aol, self).__init__(proxy, timeout)
        self._base_url = 'https://search.aol.com'
        self._session = aiohttp.ClientSession()

    async def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = '{}/aol/search?q={}&ei=UTF-8&nojs=1'
        url = url_str.format(self._base_url, self._query)
        async with self._session.get(self._base_url) as response:
            if response.status != 200:
                response.raise_for_status()
        return {'url': url, 'data': None}

    async def close(self):
        '''Closes the HTTP session.'''
        await self._session.close()
