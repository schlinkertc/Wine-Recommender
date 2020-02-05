import requests
import bs4
from bs4 import BeautifulSoup
from datetime import datetime as dt

pages = set()
def getPages(pageURL="https://www.kingscountywines.com/wine/"):
    """
    This function goes to the Kings County Wines Wine page and gets the URLs that we'll need to scrape.
    """
    global pages
    page = requests.get(pageURL)

    bs = BeautifulSoup(page.content,features='lxml')
    for link in bs.find('ul',{"class":"right no-list-style"}).li.next_siblings:
        if type(link)==bs4.element.Tag:
            if link.a['href'] not in pages and '/wine/' in link.a['href']:
                #we have encountered a new page 
                newPage = link.a['href']
                print("new page: ",newPage)
                pages.add(newPage)
                getPages(newPage)

getPages()

def getWines(url):
    """
    take in a kingscountywines.com url and return the products listed on the page.
    """
    page = requests.get(url)
    bs = BeautifulSoup(page.content,features='lxml')

    wine_images = bs.find_all(attrs={'class':'image-wrap'})
    
    wines = []
    for image in wine_images:
        wine = {}
        wine['name'] = image.find('a')['title']
        wine['link'] = image.find('a')['href']
        
        wine_page = requests.get(wine['link'])
        wine_bs = BeautifulSoup(wine_page.content,features='lxml')
        offer = wine_bs.find('div',{'itemprop':'offers'})
        
        price = float(offer.find('span',{'itemprop':'price'}).getText())
        wine['price']=price
        
        wine['description'] = offer.p.getText()
        wines.append(wine)
        
        wine['date_collected'] = dt.now()
        
        image_link = wine_bs.find('img',attrs={'itemprop':'image'})
        if image_link != None:
            wine['image_link'] = image_link['src']
        else:
            wine['image_link'] = 'null'
        
        #holy shit this is messy...
        in_stock = wine_bs.find('table',attrs={'class':'details'})
        if in_stock != None:
            in_stock = in_stock.find_all('td')[-1].getText().split(' \n')[0]
        else:
            in_stock = 'null'
        wine['in_stock']=in_stock
        
        details_text = [x.getText() for x in wine_bs.find('div',attrs={'class':'page info active'}).find_all('p')]
        details = "".join([x for x in details_text if x != ' ' and x != '\xa0'])
        wine['details'] = details
    return wines

wines = []
for page in pages:
    wines.append(getWines(page))

wines = [item for sublist in wines for item in sublist]

import pandas as pd
df = pd.DataFrame.from_records(wines)

df.replace('','null',inplace=True)
df.replace(' ','null',inplace=True)

df.to_csv('kings_county_wines.csv')