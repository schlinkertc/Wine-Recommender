from class_definitions import *
from vivino_db import database
db = database.db

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def match_toVivino(wine):
    vintages_df = pd.read_sql_table('vintages',db.db_engine)
    vivino_vintages = vintages_df['name'].to_list()
    
    wine_name = wine.wineSearcher['name']
    search_string = "".join([x+' ' for x in wine.search_terms]).strip(' ')
    
    matches = [
        {'vivino_name':x,
         'match_score':fuzz.token_sort_ratio(wine_name,x),
         'instance':wine
        }
        for x in vivino_vintages]
    
    name_match = sorted(matches,key=lambda x: x['match_score'],reverse=True)[0]
    
    matches = [
        {'vivino_name':x,
         'match_score':fuzz.token_sort_ratio(wine_name,x),
         'instance':wine
        }
        for x in vivino_vintages]
    searchString_match = sorted(matches,key=lambda x: x['match_score'],reverse=True)[0]
    
    if name_match['match_score']>searchString_match['match_score']:
        best_match = name_match
    else:
        best_match = searchString_match
    
    v_id = vintages_df[vintages_df['name']==best_match['vivino_name']]['id'].values[0]
    best_match['vintage_id']=v_id
    return best_match
    
def compile_data(wines):
    #wineSearcher 
    records = []
    for wine in wines:
        record = wine.wineSearcher
        record['instance']=wine
        records.append(record)
    df = pd.DataFrame.from_records(records)
    df.drop(columns=['url','Notes'],inplace=True)
    
    #vivino
    vivino_records = []
    for wine in wines:
        vivino_match = match_toVivino(wine)
        stmt = f"""
        SELECT 
            v.name as vivino_wine,
            v.id,
            ws.name as winery,
            r.name as region,
            s.name as style,
            s.varietal_name,
            s.regional_name,
            s.body,
            s.acidity,
            s.description as style_description,
            v.statistics_ratings_count as ratings_count,
            v.statistics_ratings_average as ratings_average,
            v.description as vintage_description,
            v.ranking_region_rank / v.ranking_region_total as ranking_region,
            v.ranking_global_rank / v.ranking_global_total as ranking_global,
            v.wine_facts_contains_added_sulfites as added_sulfites,
            v.wine_facts_certified_biodynamic as biodynamic,
            w.description as wine_description
        FROM 
            vintages v
        INNER JOIN 
            wines w on v.wine_id==w.id
        INNER JOIN 
            wineries ws on w.winery_id=ws.id
        INNER JOIN 
            styles s on s.id = w.style_id
        INNER JOIN 
            regions r on r.id = w.region_id
        WHERE
            v.id = "{vivino_match['vintage_id']}"
        """
        resultproxy = db.db_engine.execute(stmt)

        d, a = {}, []
        for rowproxy in resultproxy:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            a.append(d)
        try:
            vivino_record = a[0]
            vivino_record['instance']=vivino_match['instance']
            vivino_records.append(vivino_record)
        except:
            continue 
    return df,vivino_records

df,v_df = compile_data(Wines)

v_df =  pd.DataFrame.from_records(v_df)

df = pd.merge(left=df,right=v_df,on='instance')

## Messy/smelly updates that I need to clean up
region_country = pd.read_sql('select name as region,country_name from regions',db.db_engine)
df = pd.merge(df,region_country,on='region')

stmt="""
SELECT
    v.id,
    w.type_id
FROM
    vintages v
INNER JOIN
    wines w on v.wine_id = w.id
"""
types = pd.read_sql(stmt,db.db_engine)

df = pd.merge(df,types,on='id')

type_map = {
    1:'Red',
    2:'White',
    3:'Sparkling',
    4:'Rose'
}
df['type']=df['type_id'].map(type_map)

# messy manual updates for now
# need a better way to match vivino results with wineSearcher results
df.loc[31,'type_id']=3
df.loc[158,['Producer','Region/Appellation','Grape/Blend','Wine Style','Food Suggestion']] = ['Chateu Gassier', 'Cotes de Provence', 'Rare Rose Blend', 'Rose - Crisp and Dry', 'Tomato-based Dishes']
df.loc[53,['Producer','Region/Appellation','Grape/Blend','Wine Style','Food Suggestion']] = ['Weingut Karl Proidl',"Kremstal",'Riesling',"White - Green and Flinty", 'White Fish' ]
df.loc[4,['Producer','Region/Appellation','Grape/Blend','Wine Style','Food Suggestion']] = ['Weingut Koehler-Ruprecht','Pfalz','Pinot Noir','Red - Light and Perfumed','Meaty and Oily Fish']

# wines that are matched between vivino and wineSearcher
i = []
for t in type_map.values():
    i.extend(df[(df['Wine Style'].isna()==False)&(df['Wine Style'].str.contains(t))&(df['type']!=t)].index)

df = df.drop(index=i).reset_index()
df = df[df['Wine Style'].isna()==False]
df['Wine Style']=df.apply(lambda x: x['Wine Style'].split('-')[-1].strip(),axis=1)

if __name__ == "__main__":
    df.to_csv('dataset.csv',index=False)