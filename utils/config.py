from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

def get_supabase_client():
    return create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

# Create a single instance to be used across the app
supabase = get_supabase_client()
