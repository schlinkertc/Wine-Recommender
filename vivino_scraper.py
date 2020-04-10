from class_definitions import *
import joblib

Wines = []
for (dirpath,dirnames,filenames) in walk('Wines/'):
    if 'name-search' in dirpath:
        for filename in filenames:
            pkl = joblib.load(dirpath+'/'+filename)
            if pkl.__class__ == Wine:
                Wines.append(pkl)

vivino_wines = []
for w in Wines:
    vivino_wines.extend(w.vivino)

vivino_ids = [vw['wine_link'].split('/')[-1] for vw in vivino_wines]
storage_directory = "Wines/vivino/"


import json 

def scrape_vivino(wine_id):
    url = f"https://vivino.com/wines/{str(wine_id)}"
    page = requests.get(url,headers=Wine.headers)
    bs = BeautifulSoup(page.content,features='lxml',parser='lxml')
    
    ld_json = bs.find('script',attrs={'type':"application/ld+json"})
    overview = json.loads(ld_json.text)['mainEntity']
    
    scripts = bs.find_all('script')
    
    for s in scripts:
        if "winePageInformation" in s.text:
            info = s
    a = info.text.split(';')[1]
    b = a.strip('\n  window.__PRELOADED_STATE__.winePageInformation = ')
    
    wine_info = json.loads(b)
    
    return wine_info

import time 
for wine_id in vivino_ids:
    try:
        result = scrape_vivino(wine_id)
        joblib.dump(result,storage_directory+str(wine_id))
        print('*')
        time.sleep(10)
    except:
        continue