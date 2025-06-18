import os

from dotenv import load_dotenv
from models.asset_handlers import AssetHandlerFactory, AssetType
from utils.config import supabase
import requests
import time

load_dotenv()

def update_all_asset_prices():
  """
    Fetches all unique assets from portfolios, updates their prices,
    and saves them back to the database.
  """
  print("Starting daily asset price update...")

  polygon_api_key = os.getenv('POLYGON_API_KEY')
  if not polygon_api_key:
      print("POLYGON_API_KEY not found. Please set the environment variable.")
      return

  AssetHandlerFactory.initialize(polygon_api_key)

  try:
    response = supabase.table('portfoliosv2').select('user_id', 'symbol', 'asset_type').execute()
    if not response.data:
        print("No assets found in portfolios to update.")
        return
    
    unique_polygon_assets = {}
    unique_pokemon_assets = {}

    for item in response.data:
      symbol = item['symbol']
      asset_type_str = item['asset_type']

      if asset_type_str == AssetType.STOCK.value or asset_type_str == AssetType.CRYPTO.value:
        if symbol not in unique_polygon_assets:
          unique_polygon_assets[symbol] = asset_type_str
      elif asset_type_str == AssetType.POKEMON.value:
          if symbol not in unique_pokemon_assets:
            unique_pokemon_assets[symbol] = asset_type_str
      else:
          print(f"Warning: Unknown asset type '{asset_type_str}' for symbol '{symbol}'. Skipping.")

    if unique_pokemon_assets:
        print("\n--- Updating Pokemon Asset Prices ---")
        for symbol, asset_type_str in unique_pokemon_assets.items():
            print(f"  Processing Pokemon: {symbol}")
            try:
                handler = AssetHandlerFactory.get_handler(
                  AssetType.POKEMON)
                if handler:
                    current_price = handler.get_current_price(symbol)
                    if current_price is not None:
                        update_response = supabase.table('portfoliosv2') \
                            .update({'current_price': current_price}) \
                            .eq('symbol', symbol) \
                            .execute()
                        if update_response.data:
                            print(
                              f"  Updated price for Pokemon {symbol} to {current_price}")
                        else:
                            print(
                              f"  Failed to update price for Pokemon {symbol} in DB: {update_response.status_code}")
                    else:
                        print(
                          f"  Could not fetch price for Pokemon {symbol}.")
                else:
                    print(f"  No handler for Pokemon asset type.")
            except requests.exceptions.RequestException as req_e:
                print(
                  f"  Network error fetching price for Pokemon {symbol}: {req_e}")
            except Exception as e:
                print(f"  General error processing Pokemon {symbol}: {e}")

        if unique_polygon_assets:
            print("\n--- Updating Stock/Crypto Prices (with rate limiting) ---")

            # The rate limit is 5 requests per minute, so 1 request every 12 seconds (60/5).
            delay_between_polygon_calls_seconds = 13

            for i, (symbol, asset_type_str) in enumerate(unique_polygon_assets.items()):
                print(
                  f"  Processing Polygon asset: {symbol} (Type: {asset_type_str})")

                try:
                    asset_type = AssetType[asset_type_str.upper()]
                    handler = AssetHandlerFactory.get_handler(asset_type)

                    if handler:
                        current_price = handler.get_current_price(symbol)
                        if current_price is not None:
                            print(
                              f"  Successfully fetched price for {symbol}: {current_price}")
                            update_response = supabase.table('portfoliosv2') \
                                .update({'current_price': current_price}) \
                                .eq('symbol', symbol) \
                                .execute()
                            if update_response.data:
                                print(f"  Database updated for {symbol}.")
                            else:
                                print(
                                  f"  Failed to update database for {symbol}: {update_response.status_code} - {update_response.data}")
                        else:
                            print(
                              f"  Could not fetch price for {symbol}. API might have returned no data or hit limit.")
                    else:
                        print(f"  No handler for asset type: {asset_type_str}")
                except requests.exceptions.RequestException as req_e:
                    print(
                      f"  Network error fetching price for {symbol}: {req_e}")
                except Exception as e:
                    print(f"  General error processing {symbol}: {e}")

                if i < len(unique_polygon_assets) - 1:
                    print(
                      f"  Pausing for {delay_between_polygon_calls_seconds} seconds to respect API rate limits...")
                    time.sleep(delay_between_polygon_calls_seconds)

        else:
            print("No stock or crypto assets to update.")

  except Exception as e:
    print(f"An unexpected error occurred during price update: {e}")

  print("Daily asset price update complete.")


if __name__ == "__main__":
    update_all_asset_prices()