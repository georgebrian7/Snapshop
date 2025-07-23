import os
import base64
import requests
from django.core.cache import cache
from decouple import config


import json






class EbayService:
    def __init__(self):
        self.app_id = config('EBAY_APP_ID')
        self.dev_id = config('EBAY_DEV_ID')
        self.cert_id = config('EBAY_CERT_ID')
        self.base_url = config('EBAY_BASE_URL', default='https://api.ebay.com')

        self.browse_url = f"{self.base_url}/buy/browse/v1"

    def get_oauth_token(self):
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
                'scope': config('EBAY_OAUTH_SCOPE', default='https://api.ebay.com/oauth/api_scope')
            }

            resp = requests.post(url, headers=headers, data=data)
            resp.raise_for_status()

            token_data = resp.json()
            token = token_data['access_token']
            expires = token_data['expires_in']
            cache.set(cache_key, token, expires - 60)

        return token

    def _get_basic_auth(self):
        creds = f"{self.app_id}:{self.cert_id}"
        return base64.b64encode(creds.encode()).decode()

    def search_items(self, query, limit=50, category_id=None, filters=None):
        token = self.get_oauth_token()
        url = f"{self.browse_url}/item_summary/search"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        params = {'q': query, 'limit': limit}
        if category_id:
            params['category_ids'] = category_id
        if filters:
            params.update(filters)

        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_item_details(self, item_id):
        token = self.get_oauth_token()
        url = f"{self.browse_url}/item/{item_id}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
