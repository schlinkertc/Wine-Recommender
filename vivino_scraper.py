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
    
    scripts = bs.find_all('script')
    
    for s in scripts:
        if "winePageInformation" in s.text:
            info = s
    a = "".join([x for x in info.text.split(';')[1:-1]])
    b = a.strip('\n  window.__PRELOADED_STATE__.winePageInformation = ')
    
    wine_info = json.loads(b)
    
    return wine_info

def update_wineSearcher_fromVivino(wine):
    vivino_match = match_toVivino(wine)
    search_terms=vivino_match['vivino_name'].replace(' ',"+")

    url = f'https://www.wine-searcher.com/find/{search_terms}'

    wine_dict = {'url':url}

    page = requests.get(url,headers=Wine.headers)
    if page.status_code != 200:
        return page.status_code
    bs = BeautifulSoup(page.content,'lxml')

    wine_dict['name'] = bs.find(
        'h1',attrs={'class':'wine'}).\
            getText(strip=True)

    wine_info_panel = bs.find('div',attrs={"class":'wine-info-panel'})
    if wine_info_panel==None:
        print(f"failure{wine}")
        return wine_dict
    wine_info = []

    for div in wine_info_panel.find_all('div',attrs={'class':'dtc'}):
        wine_info.append(
            [x.getText() for x in div.find_all(
                'span',attrs={'class':"dtlbl sidepanel-text"}
            ) 
             if type(x)==bs4.element.Tag])

    wine_info = [
        item.split('\n') for sublist in wine_info for item in sublist
    ]
    wine_info = [
        item.strip() for sublist in wine_info 
        for item in sublist if item not in  ['',' ']
    ]

    wine_dict_keys = [
        'Producer','Region/Appellation',
        'Grape/Blend','Food Suggestion',
        'Wine Style','Alcohol Content','Notes'
    ]

    for key in wine_dict_keys:
        try:
            key_index = wine_info.index(key)
            wine_dict[key]=wine_info[key_index+1]
        except:
            wine_dict[key]='null'
    
    wine.wineSearcher = wine_dict
    
    joblib.dump(wine,f"Wines/name-search/{wine.name}.pkl")
    print('success')

if __name__ == "__main__":
    import time 
    for wine_id in vivino_ids:
        try:
            result = scrape_vivino(wine_id)
            joblib.dump(result,storage_directory+str(wine_id))
            print('*')
            time.sleep(10)
        except:
            continue