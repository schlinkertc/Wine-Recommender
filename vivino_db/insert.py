import pandas as pd
import os
from os import walk
import joblib

vivino_results = []
for dirpath,directory,filenames in walk("../Wines/vivino/"):
    for filename in filenames:
        result = joblib.load(dirpath+filename)
        vivino_results.append(result)

def parse_dict(input_dict):
    new_dict = {}
    for k,v in input_dict.items():
        if type(v) != dict and type(v) != list and v != None:
            new_dict[k]=input_dict[k]
        if type(v)==dict: 
            if 'id' in v.keys():
                new_dict[f"{k}_id"] = input_dict[k]['id']
            else:
                for key,value in v.items():
                    new_dict[f"{k}_{key}"]=value
    return new_dict

records = []
for result in vivino_results:
    vintage_wine = result['vintage']['wine']
    records.append(parse_dict(vintage_wine))

wine_df = pd.DataFrame.from_records(records)

wine_df.drop(columns=[x for x in wine_df.columns if 'light_winery' in x],inplace=True)

wine_df.drop(columns=['vintage_mask_raw'],inplace=True)



records = []
for result in vivino_results:
    style = result['vintage']['wine']['style']
    if style !=None:
        record = {k:v for k,v in parse_dict(style).items() if type(v)!=dict and type(v)!= list}
        records.append(record)

style_df = pd.DataFrame.from_records(records)


records = []
for result in vivino_results:
    region = result['vintage']['wine']['region']
    if region !=None:
        record = {k:v for k,v in parse_dict(region).items() if type(v)!=dict and type(v)!= list}
        records.append(record)

region_df = pd.DataFrame.from_records(records)


records = []
for result in vivino_results:
    try:
        winery = result['vintage']['wine']['winery']
    except KeyError:
        winery=None
    if winery !=None:
        record = {k:v for k,v in parse_dict(winery).items() if type(v)!=dict and type(v)!= list}
        records.append(record)

winery_df = pd.DataFrame.from_records(records)

import sqlalchemy
from sqlalchemy import create_engine

class MyDatabase:
    # http://docs.sqlalchemy.org/en/latest/core/engines.html
    """
    Custom class for instantiating a SQL Alchemy connection. Configured here for SQLite, but intended to be flexible.
    Credit to Medium user Mahmud Ahsan:
    https://medium.com/@mahmudahsan/how-to-use-python-sqlite3-using-sqlalchemy-158f9c54eb32
    """
    DB_ENGINE = {
       'sqlite': 'sqlite:////{DB}'
    }

    # Main DB Connection Ref Obj
    db_engine = None
    def __init__(self, dbtype, 
                 username='', password='', 
                 dbname='',path=os.getcwd()+'/'):
        dbtype = dbtype.lower()
        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=path+dbname)
            self.db_engine = create_engine(engine_url)
            print(self.db_engine)
        else:
            print("DBType is not found in DB_ENGINE")

db = MyDatabase(dbtype='sqlite',dbname='vivino_wines.db')

def flatten_dicts(dictionary):
    """
    recursively flatten a dictionary of dictionaries
    """
    #base case 
    if dict not in [type(x) for x in dictionary.values()]:
        return dictionary
    else:
        for key, value in dictionary.items():
            if type(value)==dict:
                temp_dict = dictionary.pop(key)
                for k,v in temp_dict.items():
                    dictionary[f"{key}_{k}"]=v
                return flatten_dicts(dictionary)
            
records = []
for result in vivino_results:
    
    record = flatten_dicts(parse_dict(result['vintage']))
    records.append(record)
vintages_df = pd.DataFrame.from_records(records)

vintages_df = vintages_df[[x for x in vintages_df.columns if 'grape_composition' not in x and 'image' not in x]]


dfs = [
    {'name':'wines','df':wine_df},
    {'name':'styles','df':style_df},
    {'name':'regions','df':region_df},
    {'name':'wineries','df':winery_df},
    {'name':'vintages','df':vintages_df}
]
if __name__=='__main__':
    for df in dfs:
        df['df'].drop_duplicates(inplace=True)
        df['df'].to_sql(df['name'],db.db_engine,if_exists='replace',index=False)