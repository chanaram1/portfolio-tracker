# Creating a Portfolio Tracker
This tracker is tailored to specific things that I own and look at currently such as stocks, crypto and Pokemon TCG (yes, pokemon it does well).
It will send me a updated price of my portfolio at each day.

# TCG
Things I have considered doing in this project. Creating a way to scrape data for Pokemon TCG like Collectr (TCG tracking app) but it costed money using
their API. So I thought of using a web scraping like selenium to scrape data of TCGPlayer.com which people use to compare prices of what the market value is.
Scraping wasn't allowed so I pivoted to digging more and finding posts on Reddit about this. It led to finding various links of but came across these API links.
https://mp-search-api.tcgplayer.com/v1/product/{id}/details and https://mpapi.tcgplayer.com/v2/product/42346/pricepoints
These were helpful for getting information on the product and prices. I kept these on the side while I digged a little more and found a website that
provides a CSV file of all TCG prices and products. https://tcgcsv.com/

# Stock & Crypto
I researched and compared between some API providers such as CoinMarketCap, Yahoo Finance, etc., but ended up using AlphaVantage since it was free and provided
enough API calls for me to use for this project. But if I would scale this project, I would need to look for providers that didn't have low limit calls and pay a subscription.

# Future
Possibly play with Telegram API and send myself a message on it to say this is your current portfolio value "XXX.XX".
Create a front-end and turn it into like a leaderboard game with friends.
Use Supabase for authentication and authorization.
