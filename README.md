# Humble Chuck's Wine Recommender 


![I like it, it's good](https://media.giphy.com/media/l3E6GY9hwCuzXL62k/giphy.gif)

## Motivation 

I keep having the same nightmare. I finally ask that girl to dinner, and against her better judgement, she agrees. It comes time to order drinks for our meal, and I'm faced with a list of 50 names in 3 languages I don't speak for wines I can't afford. This is an important moment. A reasonably priced chardonnay calls out to me as a safe choice but let's face it, no one goes on a second date with the guy who orders the wine that reminds them of their mom. I like to consider myself a man of good taste, so I know the greatest hits of wine apprectiation: you're supposed to smell it first, right? Tannins are involved somehow? I don't know what a tannin is but I think they're important. I order the third cheapest Italian wine even though I literally have no idea what it is. She prefers french wine. The night is ruined. 

But I'm a data scientist! I have the power of statistical decision making on my side. I don't need to listen to some top-chef hopefull tell me that this wine is more "flinty" than the other, or how thick the skin of the grape is. Of course, a certain amount of domain knowledge is needed for any good data science project. So like any responsible scientist I'll taste-test my results thoroughly with the help of my amazing [local wine store](https://www.kingscountywines.com/).

## The Process 

### Data Gathering

The primary challenge in the data gathering step of the process is matching the name of wine across multiple sources. I'm using the [Kings County Wines](https://www.kingscountywines.com/) website as my starting point, and they don't provide formatted information that can reliably identify a wine. All we have to start with is the name of the wine which may or may not include the vintage (or the year it was produced), the winery, region, grape type, etc. This is a familiar problem to anyone staring down an unfamiliar wine list. 

Once we've [scraped the wine names](scraping/kings_county_scraper.py) from Kings County Wines, we'll have to collect some supporting data to inform our recommender engine. I used [Wine-searcher](wine-searcher.com) and [Vivino](vivino.com) to get the data. Both have their advantages, but neither have a formal API. I web-scraped these sites using Beautiful Soup and Selenium. 

Wine-Searcher was relatively straight-forward to scrape, and it conveniently groups certain rare grape blends into their own categories. It also provides generic wine styles like "Bold & Stuctured" or "Green & Flinty", which was a nice starting point for understanding different types of wine beyond just red or white. 

Vivino, on the other hand, is a little more sophisticated, but it has greater benefits to offer. It wasn't possible to scrape all of the necessary information with Beautiful Soup alone, but I was able to find an html script with nested JSON dictionaries that seemed to be based on a formal database with primary and foreign keys. I was able to [re-create a version of this database](vivino_db/database.py) to use in my model. There was still more information available on my browser page that I couldn't see in the parsed HTML. I [used Selenium](vivino_selenium_scraper.py) to find and store the data that couldn't be accessed with more typical scraping techniques. The Vivino database offered some more formal definitions, and it's user base seems to be larger than Wine-Seachers, giving us more accurate ratings. Vivino also provides tasting notes that are based on user reviews that provided critical functionality to our model. 

Our original problem still prevails, though. After collecting all of this information, how can we be sure that our data is correctly mapped to the oringal list of wine names that we might see on a menu or on our local wine store's website? I tried to address this with the Python [FuzzyWuzzy library](https://github.com/seatgeek/fuzzywuzzy) that measures string similarity with Levenshtein Distance. Wine-Searcher only provides one result for a search query, while Vivino returns several. For each wine, I inintially trusted Wine-Searcher to give me the right result, scraped all of Vivino's possible matches, and used fuzzy matching to determine which Vivino result was the most likely. If Wine-Searcher failed to return a result or returned a result that wasn't consistent with vivino, I re-scraped Wine-Searcher using the search terms provided by Vivino. This yielded suboptimal results. I could only be confident in 128 matches out of 247 possible results. The first improvement to this model should be a more robust matching process. 

### Exploring the Data

I used plotly to explore and vizualize our results. Our data contains 128 wines offered on the Kings County Wines website from 13 countries and 105 unique regions. ![countries_regions]('images/countries_regions.html')

### Modeling

First, we compute the weighted score for each wine. 

To include tasting notes into our model, we'll compute TF-IDF vectors for the tags and notes for each wine. The TF-IDF score is the frequency of a word occuring in a document, down-weighted by the number of documents in which it occurs. 

[content-based recommender system](modeling.py)

