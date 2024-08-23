import aiohttp
from yarl import URL
from .config import PYTHON_VERSION

async def quote_url(url, safe=';/?:@&=+$,#'):
    '''Encodes URLs.'''
    if PYTHON_VERSION == 2:
        url = await encode_str(url)
    return URL(url).update_query({}).human_repr()

async def unquote_url(url):
    '''Decodes URLs.'''
    if PYTHON_VERSION == 2:
        url = await encode_str(url)
    return await decode_bytes(str(URL(url)))

async def is_url(link):
    '''Checks if link is URL'''
    try:
        result = URL(link)
        return bool(result.scheme and result.host)
    except ValueError:
        return False

async def domain(url):
    '''Returns domain from URL'''
    host = URL(url).host
    if host:
        return host.lower().split(':')[0].replace('www.', '')
    return ''

async def encode_str(s, encoding='utf-8', errors='replace'):
    '''Encodes unicode to str, str to bytes.'''
    return s if isinstance(s, bytes) else s.encode(encoding, errors=errors)

async def decode_bytes(s, encoding='utf-8', errors='replace'):
    '''Decodes bytes to str, str to unicode.'''
    return s.decode(encoding, errors=errors) if isinstance(s, bytes) else s