from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
from enum import Enum
import os


class AssetType(Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    POKEMON = "pokemon"


class ValidationResult:
    """Result of asset validation with additional data."""

    def __init__(self, is_valid: bool, formatted_symbol: str = "",
                 data: Dict[str, Any] = None, error_message: str = ""):
        self.is_valid = is_valid
        self.formatted_symbol = formatted_symbol
        self.data = data or {}
        self.error_message = error_message


class AssetHandler(ABC):
    """Abstract base class for asset handlers."""

    @abstractmethod
    def validate_symbol(self, symbol: str) -> bool:
        """Basic symbol format validation."""
        pass

    @abstractmethod
    def format_symbol(self, symbol: str) -> str:
        """Format symbol to standard format."""
        pass

    @abstractmethod
    def validate_and_enrich(self, symbol: str) -> ValidationResult:
        """Validate symbol and return enriched data."""
        pass

    @abstractmethod
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price."""
        pass


class PolygonStockHandler(AssetHandler):
    """Stock handler using Polygon.io API."""

    def __init__(self, api_key: str = None):
        """Initialize with Polygon.io API key."""
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Polygon.io API key is required. Set POLYGON_API_KEY environment variable or pass api_key parameter.")

        self.base_url = "https://api.polygon.io"
        self.session = requests.Session()
        self.session.params = {'apikey': self.api_key}

    def validate_symbol(self, symbol: str) -> bool:
        if not symbol or not isinstance(symbol, str):
            return False

        symbol = symbol.strip().upper()
        return symbol.isalpha() and 1 <= len(symbol) <= 5

    def format_symbol(self, symbol: str) -> str:
        return symbol.strip().upper()

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

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

            price_endpoint = f"/v2/aggs/ticker/{formatted_symbol}/prev"
            price_data = self._make_request(price_endpoint)

            current_price = None
            if price_data.get('status') == 'OK' and price_data.get('results'):
                current_price = float(price_data['results'][0]['c'])

            stock_data = {
                'symbol': formatted_symbol,
                'name': ticker_info.get('name', formatted_symbol),
                'current_price': current_price,
                'currency': ticker_info.get('currency_name', 'USD')
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
        """Get current stock price using Polygon.io."""
        try:
            formatted_symbol = self.format_symbol(symbol)

            price_endpoint = f"/v2/aggs/ticker/{formatted_symbol}/prev"
            price_data = self._make_request(price_endpoint)

            if price_data.get('status') == 'OK' and price_data.get('results'):
                return float(price_data['results'][0]['c'])

            return None

        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None


class AssetHandlerFactory:
    """Factory for creating asset handlers."""

    _handlers = {}

    @classmethod
    def initialize(cls, polygon_api_key: str = None):
        """Initialize handlers with API keys."""
        cls._handlers = {
            AssetType.STOCK: PolygonStockHandler(api_key=polygon_api_key)
        }

    @classmethod
    def get_handler(cls, asset_type: AssetType) -> Optional[AssetHandler]:
        """Get handler for asset type."""
        if not cls._handlers:
            try:
                cls.initialize()
            except ValueError as e:
                print(f"Warning: {e}")
                return None

        return cls._handlers.get(asset_type)

    @classmethod
    def validate_asset(cls, asset_type: AssetType, symbol: str) -> ValidationResult:
        """Convenience method to validate any asset."""
        handler = cls.get_handler(asset_type)
        if not handler:
            return ValidationResult(
                is_valid=False,
                error_message=f"No handler available for asset type: {asset_type}. Make sure Polygon.io API key is configured."
            )

        return handler.validate_and_enrich(symbol)
