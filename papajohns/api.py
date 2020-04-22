import aiohttp
import ssl
import certifi
import json
import asyncio

class Api:
    def __init__(self):
        self.addresses = None
        self.sslcontext = ssl.create_default_context(cafile=certifi.where())
        self.sess = aiohttp.ClientSession(headers={'pj-client-app': 'IPHONE'})

    def _url(self, parts):
        return 'https://api.papajohns.co.uk/api/' + '/'.join(str(s).strip('/') for s in parts)

    async def fetch(self, parts, params=None):
        url = self._url(parts)
        async with self.sess.get(url, params=params, ssl=self.sslcontext) as resp:
            return await self.check_response(await resp.json())

    async def get_addresses(self, postcode):
        resp = await self.fetch(['v2', 'addresses'], params={'postalCode': postcode})
        return resp['data']

    async def get_delivery_stores(self, full_address):
        stores_results = await self.fetch(['v2', 'stores'], params={'searchType': 'ALL', 'locationType': 'HOME',
                                                                    'street': full_address['address1'],
                                                                    'city': full_address['city'],
                                                                    'postalCode': full_address['postalCode']})
        return stores_results['data']['deliveryStores']

    async def get_store_deals(self, store_id):
        r = await self.fetch(['v2', 'stores', store_id, 'deals', 'grouped'], params={'hideSteps': 'true'})
        return r['data']['deals']

    async def check_response(self, resp):
        if resp['data']:
            return resp
        else:
            raise RuntimeError(resp)

    def __del__(self):
        asyncio.create_task(self.sess.close())
