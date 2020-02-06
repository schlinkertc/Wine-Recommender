import pandas as pd
from datetime import datetime as dt
import re
import unicodedata
import requests
import bs4
from bs4 import BeautifulSoup

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