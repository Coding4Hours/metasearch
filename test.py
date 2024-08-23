from search_engines import Google

engine = Google()
results = engine.search("my query")
links = results.links()

print(links)
