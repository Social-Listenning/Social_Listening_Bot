import httpx
from urllib.parse import urljoin

async def PostMethod(domain, endpoint, body, headers={}):
  url = urljoin(domain, endpoint) 
  async with httpx.AsyncClient() as client:
    response = await client.post(url=url, headers=headers, json=body)
  return response