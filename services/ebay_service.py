import requests
import os
import json
import base64
from dotenv import load_dotenv
from django.core.cache import cache

# Load environment variables from .env file
load_dotenv()

class EbayService:
    def __init__(self):
        self.app_id = os.getenv('EBAY_APP_ID')
        self.dev_id = os.getenv('EBAY_DEV_ID')
        self.cert_id = os.getenv('EBAY_CERT_ID')
        
        # Handle boolean conversion for sandbox mode
        sandbox_env = os.getenv('EBAY_SANDBOX', 'True').lower()
        self.sandbox = sandbox_env in ('true', '1', 'yes', 'on')
        
        # API endpoints
        if self.sandbox:
            self.base_url = "https://api.sandbox.ebay.com"
        else:
            self.base_url = "https://api.ebay.com"
            
        self.browse_url = f"{self.base_url}/buy/browse/v1"
        
    def get_oauth_token(self):
        """Get OAuth token for API calls"""
        cache_key = 'ebay_oauth_token'
        token = cache.get(cache_key)
        
        if not token:
            url = f"{self.base_url}/identity/v1/oauth2/token"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': f'Basic {self._get_basic_auth()}'
            }
            
            data = {
                'grant_type': 'client_credentials',
                'scope': 'https://api.ebay.com/oauth/api_scope'
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data['access_token']
                expires_in = token_data['expires_in']
                
                # Cache token for slightly less than expiry time
                cache.set(cache_key, token, expires_in - 60)
            else:
                raise Exception(f"Failed to get OAuth token: {response.text}")
                
        return token
    
    def _get_basic_auth(self):
        """Generate basic auth header"""
        credentials = f"{self.app_id}:{self.cert_id}"
        return base64.b64encode(credentials.encode()).decode()
    
    def search_items(self, query, limit=50, category_id=None, filters=None):
        """Search for items using Browse API"""
        token = self.get_oauth_token()
        
        url = f"{self.browse_url}/item_summary/search"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        params = {
            'q': query,
            'limit': limit
        }
        
        if category_id:
            params['category_ids'] = category_id
            
        if filters:
            params.update(filters)
            
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Search failed: {response.text}")
    
    def get_item_details(self, item_id):
        """Get detailed information about a specific item"""
        token = self.get_oauth_token()
        
        url = f"{self.browse_url}/item/{item_id}"
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get item details: {response.text}")