import requests
import dotenv
import os

dotenv.load_dotenv()


def getPokemonSet(setName):
  r = requests.get(f"https://tcgcsv.com/tcgplayer/3/groups")
  allPokemonSets = r.json()['results']

  matchingSets = [pokemonSet for pokemonSet in allPokemonSets if setName.lower()
                  in pokemonSet['name'].lower()]

  if matchingSets:
    print("Found multiple products:")
    for i, pokemonSet in enumerate(matchingSets, 1):
        print(f"{i}. {pokemonSet['name']}")
    try:
        choice = int(
            input("\nSelect product number (1-{0}): ".format(len(matchingSets))))
        if 1 <= choice <= len(matchingSets):
            return matchingSets[choice-1]['groupId']
    except ValueError:
        print("Invalid input")
        return None
  else:
      print("No matching set found")
      return None

def getPokemonProduct(groupId, productName):
  r = requests.get(
      f"https://tcgcsv.com/tcgplayer/3/{groupId}/products")
  products = r.json()['results']

  matchingProducts = [product for product in products if productName.lower() in product['name'].lower()]
  
  if matchingProducts:
    print("\nFound multiple products:")
    for i, product in enumerate(matchingProducts, 1):
            print(f"{i}. {product['productId']} - {product['name']}")
    try:
        choice = int(
          input("\nSelect product number (1-{0}): ".format(len(matchingProducts))))
        if 1 <= choice <= len(matchingProducts):
            return matchingProducts[choice-1]['productId']
    except ValueError:
        print("Invalid input")
        return None
  else:
      print("No matching products found")
      return None

def getPokemonPrices(groupId, productId):
  r = requests.get(f"https://tcgcsv.com/tcgplayer/3/{groupId}/prices")
  prices = r.json()['results']

  if any(price['productId'] == productId for price in prices):
      price = next((price['marketPrice'] for price in prices if price['productId'] == productId), None)
      return price

def getStock(tickerSymbol):
  apiKey = os.getenv('ALPHA_VANTAGE_API_KEY')
  url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={tickerSymbol}&apikey={apiKey}"
  r = requests.get(url)
  data = r.json()

  stockPrice = float(data['Time Series (Daily)'][data['Meta Data']
                                            ['3. Last Refreshed']]['4. close'])
  return stockPrice

def getCryptoPrice(coinTicker):
  apiKey = os.getenv('ALPHA_VANTAGE_API_KEY')
  url = f"https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol={coinTicker}&market=USD&apikey={apiKey}"
  # url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=EUR&apikey=demo"
  r = requests.get(url)
  data = r.json()


  cryptoPrice = float(data['Time Series (Digital Currency Daily)']
                    [data['Meta Data']['6. Last Refreshed'].split()[0]]['4. close'])

  return cryptoPrice

if __name__ == "__main__":
  # print("Welcome to the TCGPlayer Price Checker!")

  # setName = input("Please enter the name of the Pokémon set: ")
  # groupId = getPokemonSet(setName)
  # product = input("Enter the product name: ")
  # productId = getPokemonProduct(groupId, product)
  # print("Fetching data...")
  # price = getPokemonPrices(groupId, productId)
  # print(price)
  # getStock("AAPL")
  getCryptoPrice("BTC")

