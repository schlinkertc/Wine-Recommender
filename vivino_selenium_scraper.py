from class_definitions import *
import joblib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")

    
chrome_driver_path = "/Users/schlinkertc/code/chromedriver"
driver = webdriver.Chrome(executable_path=chrome_driver_path)

import time
def selenium_scrape(wine_id,driver):
    url = f"https://vivino.com/wines/{str(wine_id)}"
    
    chrome_driver_path = "/Users/schlinkertc/code/chromedriver"
    driver = webdriver.Chrome(executable_path=chrome_driver_path)
    
    driver.get(url)
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 1200)")
    driver.execute_script("window.scrollTo(0, 1800)")
    time.sleep(2)
    master_wine_page = driver.find_element_by_id('master-wine-page-app')
    
    driver.set_window_size(width=742,height=983)
    a_tags = driver.find_elements_by_tag_name('a')
    
    for a in a_tags:
        a_class = a.get_attribute('class')
        if 'toggleShowAll' in a_class:
            show_all = a
            break

    a.click()
    time.sleep(5)
    text = master_wine_page.text
    notes = [x for x in text.split('\n') if 'mentions of' in x]
    
    svgs = master_wine_page.find_elements_by_tag_name('svg')

    tasteNotes = []
    for s in svgs:
        try:
            svg_class = s.get_attribute('class')
            if 'tasteNote' in svg_class:
                tasteNotes.append(s)
        except:
            continue 

    #notes = []
    note_tags = []
    for i in range(len(tasteNotes)):
        driver.execute_script("arguments[0].scrollIntoView();", tasteNotes[i])
        tasteNotes[i].click()
        time.sleep(5)
        spans = driver.find_elements_by_tag_name('span')
        for span in spans:
            try:
                span_class = span.get_attribute('class')
                if 'tasteReviews__capitalizedTastes' in span_class:
                    note_texts.append(span.text)
            except:
                continue
        divs = driver.find_elements_by_tag_name('div')
        
        
        for div in divs:
            try:
                div_class = div.get_attribute('class')
                if 'noteTag__name' in div_class:
                    note_tags.append({'index':i,'tag':div.text})
            except:
                continue
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        
      ## This is to get the indicator bars. not ready yet  
#     spans = [x for x in master_wine_page.find_elements_by_tag_name('span')]
#     styles = []
#     for span in spans:
#         try:
#             style = span.get_attribute('style')
#             if style.startswith('width'):
#                 styles.append(style)
#         except:
#             continue
    indexed_notes = [{'index':n,'note':note} for n,note in enumerate(notes)]
    for tag in note_tags:
        for note in indexed_notes:
            if note['index']==tag['index']:
                tag['note']=note['note']
                
    return {wine_id:note_tags}

if __name__ == "__main__":
    df = pd.read_csv('dataset.csv')
    vivino_ids = df['id'].to_list()
    for wine_id in vivino_ids:
        try:
            result = selenium_scrape(wine_id)
            joblib.dump(result,storage_directory+str(wine_id))
            print('*')
        except:
            continue