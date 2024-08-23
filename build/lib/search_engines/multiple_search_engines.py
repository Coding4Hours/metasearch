import asyncio
from .results import SearchResults
from .engines import async_search_engines_dict
from . import output as out
from . import config as cfg

class AsyncMultipleSearchEngines:
    '''Uses multiple search engines asynchronously.'''
    def __init__(self, engines, proxy=cfg.PROXY, timeout=cfg.TIMEOUT):
        self._engines = [
            se(proxy, timeout) 
            for se in async_search_engines_dict.values() 
            if se.__name__.lower() in engines
        ]
        self._filter = None
        self.ignore_duplicate_urls = False
        self.ignore_duplicate_domains = False
        self.results = SearchResults()
        self.banned_engines = []
    
    def disable_console(self):
        '''Disables console output'''
        out.console = lambda msg, end='\n', level=None: None
    
    def set_search_operator(self, operator):
        '''Filters search results based on the operator.'''
        self._filter = operator
    
    async def search(self, query, pages=cfg.SEARCH_ENGINE_RESULTS_PAGES): 
        '''Searches multiple engines concurrently and collects the results.'''
        self.results = SearchResults()
        tasks = []
        for engine in self._engines:
            engine.ignore_duplicate_urls = self.ignore_duplicate_urls
            engine.ignore_duplicate_domains = self.ignore_duplicate_domains
            if self._filter:
                engine.set_search_operator(self._filter)
            
            tasks.append(self._search_engine(engine, query, pages))
        
        await asyncio.gather(*tasks)
        return self.results

    async def _search_engine(self, engine, query, pages):
        '''Searches a single engine and processes its results.'''
        engine_results = await engine.search(query, pages)
        if engine.ignore_duplicate_urls:
            engine_results._results = [
                item for item in engine_results._results 
                if item['link'] not in self.results.links()
            ]
        if self.ignore_duplicate_domains:
            engine_results._results = [
                item for item in engine_results._results 
                if item['host'] not in self.results.hosts()
            ]
        self.results._results += engine_results._results
        if engine.is_banned:
            self.banned_engines.append(engine.__class__.__name__)
    
    def output(self, output=out.PRINT, path=None):
        '''Prints search results and/or creates report files.'''
        output = (output or '').lower()
        query = self._engines[0]._query if self._engines else u''
        if not path:
            path = cfg.OUTPUT_DIR + u'_'.join(query.split())
        out.console('')
        if out.PRINT in output:
            out.print_results(self._engines)
        if out.HTML in output:
            out.write_file(out.create_html_data(self._engines), path + u'.html') 
        if out.CSV in output:
            out.write_file(out.create_csv_data(self._engines), path + u'.csv') 
        if out.JSON in output:
            out.write_file(out.create_json_data(self._engines), path + u'.json')

class AsyncAllSearchEngines(AsyncMultipleSearchEngines):
    '''Uses all search engines asynchronously.'''
    def __init__(self, proxy=cfg.PROXY, timeout=cfg.TIMEOUT):
        super(AsyncAllSearchEngines, self).__init__(
            list(async_search_engines_dict), proxy, timeout
        )