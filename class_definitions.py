import pandas as pd
from datetime import datetime as dt
import re
import unicodedata
import requests
import bs4
from bs4 import BeautifulSoup
from os import walk
import joblib

kcw_wines = pd.read_csv('kings_county_wines.csv',index_col=0)
wineSearcher = pd.read_csv('wine-searcher_data.csv')

def scrapeKCW_product(product_url):
    wine_page = requests.get(product_url)
    wine_bs = BeautifulSoup(wine_page.content,features='lxml')
    wine_dict = {}

    wine_dict['KCW_name']=wine_bs.find('h1').getText()

    offer = wine_bs.find('div',{'itemprop':'offers'})
    price = float(offer.find('span',{'itemprop':'price'}).getText())
    wine_dict['price']=price

    wine_dict['description'] = offer.p.getText()

    image_link = wine_bs.find('img',attrs={'itemprop':'image'})
    if image_link != None:
        wine_dict['image_link'] = image_link['src']
    else:
        wine_dict['image_link'] = 'null'

    in_stock = wine_bs.find('table',attrs={'class':'details'})
    if in_stock != None:
        in_stock = in_stock.find_all('td')[-1].getText().split(' \n')[0]
    else:
        in_stock = 'null'
    wine_dict['in_stock']=in_stock

    details_text = [
        x.getText() for x in wine_bs.find(
            'div',attrs={'class':'page info active'}).find_all('p')
    ]
    details = "".join([x for x in details_text if x != ' ' and x != '\xa0'])
    wine_dict['details'] = details
    
    return wine_dict
    
class Wine():
    
    pickled_wines = []
    for (dirpath,dirnames,filenames) in walk('Wines/'):
        pickled_wines.extend(filenames)
    
    pickled_wines = [x.strip('.pkl') for x in pickled_wines]
    
    headers = {
        'User-Agent': 
        """Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36""",
    'Connection': 'keep-alive',
    'Accept-Language': 'en-US,en;q=0.9',
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    'Upgrade-Insecure-Requests': '1',
    'cookie': 'cookie_enabled=true',
    #'referer': f'{wine_searcher_findURL}',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'cache-control': 'max-age=0',
    "sec-fetch-user": "?1"
}
    
    def _search_terms(self):
        name = self.name.replace("-"," ")
        terms = [x.replace('"','') for x in name.split(' ')]
        # get rid of numbers
        pattern = re.compile('[0-9]')
        parsed_terms = []
        for term in terms:
            if re.search(pattern,term) == None:
                parsed_terms.append(term.lower())
        
        search_terms_bytes = [unicodedata.normalize('NFKD', x).encode('ascii','ignore') 
                        for x in parsed_terms]
        search_terms = [x.decode() for x in search_terms_bytes]
        pattern = re.compile("[^a-zA-Z0-9-]")
        [re.sub(pattern,repl='',string=x) for x in search_terms]
        
        
        return search_terms
    
    def _vintage(self):
        terms = [x.replace('"','') for x in self.name.split(' ')]
        pattern = re.compile('[0-9]{4}')
        vintage = None
        for term in terms:
            if re.search(pattern,term):
                vintage = term
        return vintage
    
    def _get_searchURL(self,base_url,include_vintage=True):
        url = base_url+"".join([(x+'+') for x in self.search_terms])
        if include_vintage and self.vintage:
            return url+self.vintage
        else: 
            return url.strip('+')
    
    def _scrape_wine_searcher(self):
        url = self._get_searchURL('https://www.wine-searcher.com/find/')
        
        wine_dict = {'url':url}
        
        page = requests.get(url,headers=self.headers)
        if page.status_code != 200:
            return page.status_code
        bs = BeautifulSoup(page.content,'lxml')
        
        wine_dict['name'] = bs.find(
            'h1',attrs={'class':'wine'}).\
                getText(strip=True)
        
        wine_info_panel = bs.find('div',attrs={"class":'wine-info-panel'})
        if wine_info_panel==None:
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
        


        return wine_dict
    
    def _scrape_vivino(self):
        url = self._get_searchURL(
            'https://www.vivino.com/search/wines?q=',
            include_vintage=False
        )
        
        page = requests.get(url,headers=self.headers)
        bs = BeautifulSoup(page.content,'lxml')
    
        #possible matches 
        wine_cards = bs.find_all(attrs={'class':'wine-card__content'})
        possible_matches = []
        for card in wine_cards:
            d = {}
            d['wine_link'] = card.find('a')['href']
            d['wine_name'] = card.find('a').getText().replace('\n','')

            averages = card.find(
                'div',attrs={'class':"text-color-alt-gray wine-card__averages"}
            )
            average_rating = averages.find(
                attrs={'class':"text-inline-block light average__number"})\
            .getText(strip=True)
            
            d['average_rating']=float(average_rating)

            p_tags = averages.find_all('p')
            text = [p.getText(strip=True) for p in p_tags]
            for t in text:
                if 'rating' in t:
                    pattern = re.compile("[0-9]")
                    temp = re.findall(r'\d+',t)
                    ratings = list(map(int,temp))[0]
                    d['ratings_count'] = ratings
            possible_matches.append(d)
        return possible_matches
    
    def __init__(self,name=None,KCW_link=None,update=False):
        
        if name:
            name=name.replace('/','-')
            if name in Wine.pickled_wines and update==False:
                try:
                    pkl = joblib.load(f"Wines/name-search/{name}.pkl")
                    for k,v in pkl.__dict__.items():
                        setattr(self,k,v)
                except FileNotFoundError:
                    Wine.pickled_wines.remove(name)
            else:
                self.source = 'name-search'
                self.name=name
                self.search_terms = self._search_terms()
                self.vintage = self._vintage()
                
                # I don't like the repition, but I like the idea
                # CSVs with backed up data to check before sraping
                # need not to be de-duped, right?
                if name in wineSearcher['name'].to_list():
                    row = wineSearcher[wineSearcher['name']==name].iloc[0]
                    d = row.to_dict()
                    self.wineSearcher = d
                else:
                    self.wineSearcher = self._scrape_wine_searcher()
                
                if name in kcw_wines['name'].to_list():
                    row = kcw_wines[kcw_wines['name']==name].iloc[0]
                    d = row.to_dict()

                self.vivino = self._scrape_vivino()

                joblib.dump(self,f"Wines/name-search/{name}.pkl")
                Wine.pickled_wines.append(name)

        if KCW_link:
            self.source = 'KCW'
            self.KCW = scrapeKCW_product(KCW_link)
            self.name = self.KCW['KCW_name']
            self.search_terms = self._search_terms()
            self.vintage = self._vintage()
            self.wineSearcher = self._scrape_wine_searcher()
            
    def __repr__(self):
        return f"Wine: {self.name}, Source: {self.source}"