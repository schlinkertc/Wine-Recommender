# Humble Chuck's Wine Recommender 


![I like it, it's good](https://media.giphy.com/media/l3E6GY9hwCuzXL62k/giphy.gif)

## Motivation 

I keep having the same nightmare. I finally ask that girl to dinner, and against her better judgement, she agrees. It comes time to order drinks for our meal, and I'm faced with a list of 50 names in 3 languages I don't speak for wines I can't afford. This is an important moment. A reasonably priced chardonnay calls out to me as a safe choice but let's face it, no one goes on a second date with the guy who orders the wine that reminds them of their mom. I like to consider myself a man of good taste, so I know the greatest hits of wine apprectiation: you're supposed to smell it first, right? Tannins are involved somehow? I don't know what a tannin is but I think they're important. I order the third cheapest Italian wine even though I literally have no idea what it is. She prefers french wine. The night is ruined. 

But I'm a data scientist! I have the power of statistical decision making on my side. I don't need to listen to some top-chef hopefull tell me that this wine is more "flinty" than the other (gross), or how thick the skin of the grape is (I don't really care). Of course, a certain amount of domain knowledge is needed for any good data science project. So like any responsible scientist I'll taste-test my results thoroughly with the help of my amazing [local wine store](https://www.kingscountywines.com/).

## The Process 

### Data Gathering

To get the data to inform our recomender engine, we'll have to scrape from multiple sources. It's unlikely that we'll get much quantitative information on these wines, so a well-trained word-embedding model is critical. We'll start by scraping wine names from my local shop. [Wine-searcher](wine-searcher.com) will give us more information on these wines such as the producer, wine region, grape/blend, etc. [Wine Folly](winefolly.com) has some great general information on grape varieties as well as a useful glossary of terms. Finally, [Vivino](vivino.com) can give us more info on specific wines and access to user reviews. 

### Modeling

First, we compute the weighted score for each wine. 

To include tasting notes into our model, we'll compute TF-IDF vectors for the tags and notes for each wine. The TF-IDF score is the frequency of a word occuring in a document, down-weighted by the number of documents in which it occurs. 

![I'm a relative reference to a repository file](images/modeling.html)