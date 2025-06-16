from services.auth_service import AuthService
from services.portfolio_manager import PortfolioManager
from models.asset_handlers import AssetHandlerFactory, AssetType
import os


def initialize_services():
    polygon_api_key = os.getenv('POLYGON_API_KEY')
    AssetHandlerFactory.initialize(polygon_api_key)


def handle_portfolio_operations(user_id: str):
    portfolio = PortfolioManager()

    while True:
        print("\n=== Portfolio Management ===")
        print("1. Add New Stock")
        print("2. Add New Crypto")
        print("3. View Your Portfolio")
        print("4. Update Asset in Portfolio")
        print("5. Delete Asset from Portfolio")
        print("6. Return to Main Menu")

        choice = input("\nSelect an option (1-6): ")

        if choice == "1":
            symbol = input("Enter stock symbol (e.g., AAPL): ")
            try:
                quantity = float(input("Enter quantity: "))

                print(f"Validating stock symbol '{symbol}'...")
                validation_result = AssetHandlerFactory.validate_asset(
                    AssetType.STOCK, symbol)

                if not validation_result.is_valid:
                    print(f"Error: {validation_result.error_message}")
                    continue

                asset_data = validation_result.data
                asset_data['quantity'] = quantity 

                result = portfolio.add_asset(user_id, asset_data)

                if result:
                    print(f"\nStock added successfully!")
                    print(f"Symbol: {validation_result.formatted_symbol}")
                    print(f"Name: {asset_data.get('name', 'N/A')}")
                    print(f"Quantity: {quantity}")
                    if asset_data.get('current_price'):
                        print(
                            f"Current Price: ${asset_data['current_price']:.2f}")
                else:
                    print("Failed to add stock to portfolio")

            except ValueError:
                print("Please enter a valid number for quantity")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

        elif choice == "2":
            symbol = input("Enter crypto symbol (e.g., BTC): ")
            try:
                quantity = float(input("Enter quantity: "))

                print(f"Validating crypto symbol '{symbol}'...")
                validation_result = AssetHandlerFactory.validate_asset(
                    AssetType.CRYPTO, symbol)

                if not validation_result.is_valid:
                    print(f"Error: {validation_result.error_message}")
                    continue

                asset_data = validation_result.data
                asset_data['quantity'] = quantity

                result = portfolio.add_asset(user_id, asset_data)

                if result:
                    print(f"\nCryptocurrency added successfully!")
                    print(f"Symbol: {validation_result.formatted_symbol}")
                    print(f"Name: {asset_data.get('name', 'N/A')}")
                    print(f"Quantity: {quantity}")
                    if asset_data.get('current_price'):
                        print(
                            f"Current Price: ${asset_data['current_price']:.2f}")
                else:
                    print("Failed to add crypto to portfolio")

            except ValueError:
                print("Please enter a valid number for quantity")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

        elif choice == "3":
            print("\nFetching your portfolio...")
            result = portfolio.view_portfolio(user_id)
            if result and result.data:
                print(f"\n=== Your Portfolio ({len(result.data)} assets) ===")
                total_portfolio_value = 0

                stocks = [
                    asset for asset in result.data if asset['asset_type'] == 'stock']
                cryptos = [
                    asset for asset in result.data if asset['asset_type'] == 'crypto']

                if stocks:
                    print(f"\nSTOCKS ({len(stocks)})")
                    for asset in stocks:
                        print(f"   {asset['asset_name']} ({asset['symbol']})")
                        print(f"   Quantity: {asset['quantity']}")
                        if asset.get('current_price'):
                            asset_value = asset['current_price'] * \
                                asset['quantity']
                            print(f"   Price: ${asset['current_price']:.2f}")
                            print(f"   Total Value: ${asset_value:.2f}")
                            total_portfolio_value += asset_value
                        print()

                if cryptos:
                    print(f"\nCRYPTO ({len(cryptos)})")
                    for asset in cryptos:
                        print(f"   {asset['asset_name']} ({asset['symbol']})")
                        print(f"   Quantity: {asset['quantity']}")
                        if asset.get('current_price'):
                            asset_value = asset['current_price'] * \
                                asset['quantity']
                            print(f"   Price: ${asset['current_price']:.2f}")
                            print(f"   Total Value: ${asset_value:.2f}")
                            total_portfolio_value += asset_value
                        print()

                if total_portfolio_value > 0:
                    print(
                        f"Total Portfolio Value: ${total_portfolio_value:.2f}")
            else:
                print("No assets found in your portfolio")

        elif choice == "4":
            print("\nFetching your portfolio...")
            current_portfolio = portfolio.view_portfolio(user_id)

            if not current_portfolio or not current_portfolio.data:
                print("No assets found in your portfolio")
                continue

            print("\nYour current holdings:")
            for asset in current_portfolio.data:
                print(
                    f"   {asset['symbol']} ({asset['asset_type']}): {asset['quantity']} units")

            symbol = input(
                "\nEnter the symbol to update (e.g., AAPL, BTC): ").upper()

            symbol_exists = any(
                asset['symbol'] == symbol for asset in current_portfolio.data)
            if not symbol_exists:
                print(f"Error: You don't own any {symbol}")
                continue

            try:
                quantity = float(input("Enter new quantity: "))
                if quantity < 0:
                    print("Error: Quantity cannot be negative")
                    continue

                result = portfolio.update_asset(user_id, symbol, quantity)
                if result:
                    print(
                        f"Successfully updated {symbol} quantity to {quantity}")
                else:
                    print("Failed to update asset quantity")

            except ValueError:
                print("Please enter a valid number for quantity")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

        elif choice == "5":
            print("\nFetching your portfolio...")
            current_portfolio = portfolio.view_portfolio(user_id)

            if not current_portfolio or not current_portfolio.data:
                print("No assets found in your portfolio")
                continue

            print("\nYour current holdings:")
            for asset in current_portfolio.data:
                print(
                    f"   {asset['symbol']} ({asset['asset_type']}): {asset['quantity']} units")

            symbol = input(
                "\nEnter the symbol to delete (e.g., AAPL, BTC): ").upper()

            symbol_exists = any(
                asset['symbol'] == symbol for asset in current_portfolio.data)
            if not symbol_exists:
                print(f"Error: You don't own any {symbol}")
                continue

            confirm = input(
                f"Are you sure you want to delete {symbol}? (yes/no): ").lower()
            if confirm != 'yes':
                print("Operation cancelled")
                continue

            try:
                result = portfolio.delete_asset(user_id, symbol)
                if result:
                    print(f"Successfully deleted {symbol}")
                else:
                    print(f"Failed to delete {symbol}")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

        elif choice == "6":
            break


def main():
    initialize_services()
    auth = AuthService()

    while True:
        print("\n=== Portfolio Manager CLI ===")
        print("1. Signup")
        print("2. Login")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ")

        if choice == "1":
            email = input("Enter email: ")
            password = input("Enter password: ")
            try:
                auth.signup(email, password)
                print("Signup successful! Please check your email for verification.")
            except Exception as e:
                print(f"Signup failed: {e}")

        elif choice == "2":
            email = input("Enter email: ")
            password = input("Enter password: ")
            try:
                result = auth.login(email, password)
                print("Login successful!")
                handle_portfolio_operations(result.user.id)
            except Exception as e:
                print(f"Login failed: {e}")

        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
