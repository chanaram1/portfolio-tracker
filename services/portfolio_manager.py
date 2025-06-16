from utils.config import supabase
from typing import Dict, Any


class PortfolioManager:
    def add_stock(self, user_id: str, asset_data: Dict[str, Any]):
        try:
            insert_data = {
                "user_id": user_id,
                "symbol": asset_data.get("symbol", ""),
                "asset_name": asset_data.get("name", ""),
                "quantity": float(asset_data.get("quantity", 0)),
                "current_price": float(asset_data.get("current_price")) if asset_data.get("current_price") else None,
            }
            return supabase.table('portfolios').insert(insert_data).execute()
        except Exception as e:
            print(f"Error adding asset: {str(e)}")
            return None

    def view_portfolio(self, user_id: str):
        try:
            return supabase.table('portfolios')\
                .select("*")\
                .eq("user_id", user_id)\
                .execute()
        except Exception as e:
            print(f"Error viewing portfolio: {str(e)}")
            return None
        
    def update_stock(self, user_id: str, symbol:str, quantity:float):
        try:
            return supabase.table('portfolios')\
                .update({"quantity":quantity})\
                .eq("user_id", user_id)\
                .eq("symbol", symbol)\
                .execute()
        except Exception as e:
            print(f"Error viewing portfolio: {str(e)}")
            return None
        
    def delete_stock(self, user_id: str, symbol: str):
        try:
            return supabase.table('portfolios')\
                .delete()\
                .eq("user_id", user_id)\
                .eq("symbol", symbol)\
                .execute()
        except Exception as e:
            print(f"Error viewing portfolio: {str(e)}")
            return None
