# Portfolio Tracker

Created a portfolio management system tailored for my personal use to track and manage multiple types of assets including stocks, cryptocurrencies, and Pokemon trading cards. Built with Python and Supabase for data persistence.

## 🚀 Features

- **Multi-Asset Support**: Track stocks, cryptocurrencies, and Pokemon trading cards
- **Real-time Price Updates**: Automated price fetching using Polygon API and TCG CSV
- **User Authentication**: Secure signup and login system
- **Portfolio Management**: Add, update, delete, and view portfolio assets
- **Rate Limiting**: Respects API rate limits for reliable data fetching
- **CLI Interface**: User-friendly command-line interface for easy interaction

## 📋 Prerequisites

- Python 3.7 or higher
- Supabase account and project
- Polygon API key (for stock and crypto prices)
- Internet connection for API calls

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd portfolio-tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # Supabase Configuration
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   
   # Polygon API (for stock and crypto prices)
   POLYGON_API_KEY=your_polygon_api_key
   ```

## 🗄️ Database Setup

The application uses a Supabase database with the following table structure:

```sql
CREATE TABLE portfoliosv2 (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    asset_type TEXT NOT NULL, -- 'stock', 'crypto', 'pokemon'
    symbol TEXT NOT NULL,
    asset_name TEXT,
    quantity DECIMAL NOT NULL,
    current_price DECIMAL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🎯 Usage

### Starting the Application

Run the main application:
```bash
python main.py
```

### Main Menu Options

1. **Signup** - Create a new account
2. **Login** - Access your existing account
3. **Exit** - Close the application

### Portfolio Management Options

After logging in, you can:

1. **Add New Stock** - Add stock investments (e.g., AAPL, GOOGL)
2. **Add New Crypto** - Add cryptocurrency holdings (e.g., BTC, ETH)
3. **Add New Pokemon Product** - Add Pokemon trading cards
4. **View Your Portfolio** - See all your assets with current values
5. **Update Asset in Portfolio** - Modify quantities of existing assets
6. **Delete Asset from Portfolio** - Remove assets from your portfolio
7. **Return to Main Menu** - Go back to main menu

### Price Updates

To update all asset prices in the database:
```bash
python update_asset_prices.py
```

This script:
- Fetches current prices for all assets
- Updates the database with new prices
- Respects API rate limits (13-second delays between Polygon API calls)
- Handles different asset types appropriately

## 📊 Supported Asset Types

### Stocks
- **Symbols**: 1-5 letter stock symbols (e.g., AAPL, GOOGL, MSFT)
- **Price Source**: Polygon API
- **Validation**: Real-time symbol validation

### Cryptocurrencies
- **Symbols**: 2-10 character crypto symbols (e.g., BTC, ETH, ADA)
- **Price Source**: Polygon API
- **Format**: Automatically converts to Polygon format (X:BTCUSD)

### Pokemon Trading Cards
- **Identification**: Group ID and Product ID combination
- **Price Source**: TCG CSV API
- **Examples**: Group ID "604" with Product ID "200001"

## 🔧 API Configuration

### Polygon API
- **Purpose**: Stock and cryptocurrency price data
- **Rate Limit**: 5 requests per minute (free tier)
- **Setup**: Get API key from [Polygon.io](https://polygon.io/)

### TCG CSV API
- **Purpose**: Pokemon trading card price data
- **Rate Limit**: No rate limits
- **Setup**: No API key required

### Supabase
- **Purpose**: Database and authentication
- **Setup**: Create project at [Supabase.com](https://supabase.com/)

## 🙏 Acknowledgments

- [Polygon.io](https://polygon.io/) for financial market data
- [TCG CSV](https://tcgcsv.com/) for Pokemon card data
- [Supabase](https://supabase.com/) for backend services
