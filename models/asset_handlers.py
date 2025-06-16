from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
from enum import Enum
import os


class AssetType(Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    POKEMON = "pokemon"

    def __str__(self) -> str:
        return self.value

class ValidationResult:
    def __init__(self, is_valid: bool, formatted_symbol: str = "",
                 data: Dict[str, Any] = None, error_message: str = ""):
        self.is_valid = is_valid
        self.formatted_symbol = formatted_symbol
        self.data = data or {}
        self.error_message = error_message


class AssetHandler(ABC):
    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        pass

    @abstractmethod
    def format_symbol(self, symbol: str) -> str:
        pass

    @abstractmethod
    def validate_and_enrich(self, symbol: str) -> ValidationResult:
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> Optional[float]:
        pass

class PolygonBaseHandler(AssetHandler):
    def __init__(self, api_key:str = None, asset_type: AssetType = None):
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        if not self.api_key:
            raise ValueError("API Key is required")
        
        self.asset_type = asset_type
        self.base_url = "https://api.polygon.io"
        self.session = requests.Session()
        self.session.params = {'apikey': self.api_key}

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        
    def _get_price_data(self, formatted_symbol: str) -> Optional[float]:
        try:
            price_endpoint = f"/v2/aggs/ticker/{formatted_symbol}/prev"
            price_data = self._make_request(price_endpoint)

            if price_data.get('status') == 'OK' and price_data.get('results'):
                return float(price_data['results'][0]['c'])
            return None
        except Exception as e:
            print(f"Error getting price for {formatted_symbol}: {e}")
            return None

class PolygonStockHandler(PolygonBaseHandler):
    def __init__(self, api_key: str = None):
        super().__init__(api_key=api_key, asset_type=AssetType.STOCK)

    def validate_symbol(self, symbol: str) -> bool:
        if not symbol or not isinstance(symbol, str):
            return False
        
        symbol = symbol.strip().upper()
        return symbol.isalpha() and 1 <= len(symbol) <= 5

    def format_symbol(self, symbol: str) -> str:
        return symbol.strip().upper()

    def validate_and_enrich(self, symbol: str) -> ValidationResult:
        if not self.validate_symbol(symbol):
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid symbol format: {symbol}. Must be 1-5 alphabetic characters."
            )

        formatted_symbol = self.format_symbol(symbol)

        try:
            ticker_endpoint = f"/v3/reference/tickers/{formatted_symbol}"
            ticker_data = self._make_request(ticker_endpoint)

            if ticker_data.get('status') != 'OK' or not ticker_data.get('results'):
                return ValidationResult(
                    is_valid=False,
                    formatted_symbol=formatted_symbol,
                    error_message=f"Stock symbol '{formatted_symbol}' not found."
                )

            ticker_info = ticker_data['results']
            current_price = self._get_price_data(formatted_symbol)

            stock_data = {
                'symbol': formatted_symbol,
                'name': ticker_info.get('name', formatted_symbol),
                'current_price': current_price,
                'currency': ticker_info.get('currency_name', 'USD'),
                'asset_type': self.asset_type
            }

            return ValidationResult(
                is_valid=True,
                formatted_symbol=formatted_symbol,
                data=stock_data
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                formatted_symbol=formatted_symbol,
                error_message=f"Error validating stock '{formatted_symbol}': {str(e)}"
            )

    def get_current_price(self, symbol: str) -> Optional[float]:
        formatted_symbol = self.format_symbol(symbol)
        return self._get_price_data(formatted_symbol)


class PolygonCryptoHandler(PolygonBaseHandler):
    def __init__(self, api_key: str = None):
        super().__init__(api_key=api_key, asset_type=AssetType.CRYPTO)

    def validate_symbol(self, symbol: str) -> bool:
        if not symbol or not isinstance(symbol, str):
            return False

        symbol = symbol.strip().upper()
        return 2 <= len(symbol) <= 10 and symbol.isalnum()

    def format_symbol(self, symbol: str) -> str:
        """Format to Polygon's format (X:SYMBOL-USD)."""
        formatted = symbol.strip().upper()
        return f"X:{formatted}USD"

    def validate_and_enrich(self, symbol: str) -> ValidationResult:
        if not self.validate_symbol(symbol):
            return ValidationResult(
                is_valid=False,
                error_message=f"Invalid crypto symbol format: {symbol}. Must be 2-10 alphanumeric characters."
            )

        original_symbol = symbol.strip().upper()
        formatted_symbol = self.format_symbol(symbol)

        try:
            ticker_endpoint = f"/v3/reference/tickers/{formatted_symbol}"
            ticker_data = self._make_request(ticker_endpoint)

            if ticker_data.get('status') != 'OK' or not ticker_data.get('results'):
                return ValidationResult(
                    is_valid=False,
                    formatted_symbol=original_symbol,
                    error_message=f"Cryptocurrency '{original_symbol}' not found or not supported."
                )

            ticker_info = ticker_data['results']
            current_price = self._get_price_data(formatted_symbol)

            crypto_data = {
                'symbol': original_symbol,
                'name': ticker_info.get('name', original_symbol),
                'current_price': current_price,
                'currency': ticker_info.get('currency_name', 'USD'),
                'market': ticker_info.get('market', 'crypto'),
                'polygon_ticker': formatted_symbol,
                'asset_type': self.asset_type 
            }

            return ValidationResult(
                is_valid=True,
                formatted_symbol=original_symbol,
                data=crypto_data
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                formatted_symbol=original_symbol,
                error_message=f"Error validating crypto '{original_symbol}': {str(e)}"
            )

    def get_current_price(self, symbol: str) -> Optional[float]:
        formatted_symbol = self.format_symbol(symbol)
        return self._get_price_data(formatted_symbol)


class AssetHandlerFactory:
    _handlers = {}

    @classmethod
    def initialize(cls, polygon_api_key: str = None):
        cls._handlers = {
            AssetType.STOCK: PolygonStockHandler(api_key=polygon_api_key),
            AssetType.CRYPTO: PolygonCryptoHandler(api_key=polygon_api_key)
        }

    @classmethod
    def get_handler(cls, asset_type: AssetType) -> Optional[AssetHandler]:
        if not cls._handlers:
            try:
                cls.initialize()
            except ValueError as e:
                print(f"Warning: {e}")
                return None

        return cls._handlers.get(asset_type)

    @classmethod
    def validate_asset(cls, asset_type: AssetType, symbol: str) -> ValidationResult:
        handler = cls.get_handler(asset_type)
        if not handler:
            return ValidationResult(
                is_valid=False,
                error_message=f"No handler available for asset type: {asset_type}. Make sure Polygon.io API key is configured."
            )

        return handler.validate_and_enrich(symbol)