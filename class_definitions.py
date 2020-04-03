import pandas as pd
from datetime import datetime as dt
import re
import unicodedata
import requests
import bs4
from bs4 import BeautifulSoup

kcw_wines = pd.read_csv('kings_county_wines.csv',index_col=0)

class KCW_product():
    """
    This class represents a record from the KCW csv. It includes methods for convenience and functionality.
    """
    name = None
    link = None 
    price = None
    description = None 
    date_collected = None 
    image_link = None 
    in_stock = None
    details = None 
    
    def __init__(self,wine_name):
        KCW_csvPath = "/Users/schlinkertc/code/wine_project/wine/kings_county_wines.csv"
        KCW_df = pd.read_csv(KCW_csvPath,index_col=0)
        
        KCW_record = (
            KCW_df.loc[KCW_df['name']==wine_name]
        )
        #make sure that we only have one wine under that name
        if len(KCW_record)!=1:
            print('more than 1 record found!')
            return None
        else:
            KCW_record = KCW_record.iloc[0] #returns a series
        
        self.name = KCW_record['name']
        self.link = KCW_record['link']
        self.price = KCW_record['price']
        self.description = KCW_record['description']
        if KCW_record['description']=='null' and KCW_record['details']!='null':
            self.description = KCW['details']
        self.date_collected = dt.strptime(KCW_record['date_collected'],'%Y-%m-%d %H:%M:%S.%f')
        self.image_link = KCW_record['image_link']
        self.in_stock = KCW_record['in_stock']
        self.details = KCW_record['details']
    
    def __repr__(self):
        return f"KCW_product: {self.name}"
    
    # each word in the wine name without punctuation or numbers 
    def search_terms(self):
        terms = [x.replace('"','') for x in self.name.split(' ')]
        # get rid of numbers
        pattern = re.compile('[0-9]')
        parsed_terms = []
        for term in terms:
            if re.search(pattern,term) == None:
                parsed_terms.append(term)
        
        search_terms_bytes = [unicodedata.normalize('NFKD', x).encode('ascii','ignore') 
                        for x in parsed_terms]
        search_terms = [x.decode().strip('*') for x in search_terms_bytes]
        
        return search_terms
    
    # parse a year from the wine name 
    def vintage(self):
        terms = [x.replace('"','') for x in self.name.split(' ')]
        pattern = re.compile('[0-9]{4}')
        vintage = None
        for term in terms:
            if re.search(pattern,term):
                vintage = term
        return vintage
    
    def wine_searcherURL(self):
        wine_searcher_findURL = 'https://www.wine-searcher.com/find/'
        
        # add a plus to each term
        search_terms = [x+'+' for x in self.search_terms()]
        
        for term in search_terms:
            # add the search terms to the URL 
            wine_searcher_findURL+=term
        # get rid of the last '+'
        return wine_searcher_findURL.strip('+')
    
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
    
    storage_directory = "/Wines"
    
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
        bs = BeautifulSoup(page.content,'lxml')
        wine_info_panel = bs.find('div',attrs={"class":'wine-info-panel'})
        if wine_info_panel==None:
            pass
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
        
        wine_dict['name'] = bs.find(
            'h1',attrs={'class':'wine'}).\
                getText(strip=True)
        return wine_dict
    
    def _scrape_vivino(self):
        url = self._get_searchURL(
            'https://www.vivino.com/search/wines?q=',
            include_vintage=False
        )
        
        page = requests.get(url,headers=self.headers)
        bs = BeautifulSoup(page.content,'lxml')
    
        return bs
    
    def __init__(self,name=None,KCW_link=None):
        
        if name:
            self.source = 'name-search'
            self.name=name
            self.search_terms = self._search_terms()
            self.vintage = self._vintage()
            self.wineSearcher = self._scrape_wine_searcher()
        
        if KCW_link:
            self.source = 'KCW'
            self.KCW = scrapeKCW_product(KCW_link)
            self.name = self.KCW['KCW_name']
            self.search_terms = self._search_terms()
            self.vintage = self._vintage()
            self.wineSearcher = self._scrape_wine_searcher()
            
    def __repr__(self):
        return f"Wine: {self.name}, Source: {self.source}"