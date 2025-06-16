from utils.config import supabase


class AuthService:
    @staticmethod
    def signup(email: str, password: str):
        try:
            return supabase.auth.sign_up({
                "email": email,
                "password": password
            })
        except Exception as e:
            raise Exception(f"Signup failed: {str(e)}")

    @staticmethod
    def login(email: str, password: str):
        try:
            return supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
