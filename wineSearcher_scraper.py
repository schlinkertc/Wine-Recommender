from class_definitions import *
import joblib

Wines = []
for (dirpath,dirnames,filenames) in walk('Wines/'):
    for filename in filenames:
        pkl = joblib.load(dirpath+'/'+filename)
        if pkl.__class__ == Wine:
            Wines.append(pkl)

need_to_scrape = [w for w in Wines if type(w.wineSearcher)!=dict]

import time
count = len(need_to_scrape)
for wine in need_to_scrape:
    wine.wineSearcher = wine._scrape_wine_searcher()
    joblib.dump(wine,f"Wines/name-search/{wine.name}.pkl")
    count = count - 1
    print(count)
    time.sleep(180)
    
    