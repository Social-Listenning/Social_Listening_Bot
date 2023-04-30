import asyncio
import concurrent.futures
import datetime

from core.config import settings
from helper.httpMethod import PostMethod
from helper.execAsyncFunction import async_function_executor

async def reply_facebook_message_thread(message: any):
	with concurrent.futures.ThreadPoolExecutor() as executor:
		future = executor.submit(async_function_executor, reply_facebook_message, message=message)
		return await asyncio.wrap_future(future)

async def reply_facebook_message(message: any):
  response = await PostMethod(
    domain = 'https://graph.facebook.com',
    endpoint = "/{0}/comments?access_token={1}".format(message.get('fb_message_id'), message.get('token')),
    body = {
      "message": message.get("messageReply")
    },
  )
  fb_response = response.json()
  
  now = datetime.datetime.now()
  iso_time = now.isoformat()

  comment_info = {
    "networkId": message.get("pageId"),
    "message": message.get("messageReply"),
    "sender": message.get("pageId"),
    "createdAt": iso_time,
    "type": 'Bot',
    "parent": {
        "postId": message.get("postId"),
        "message": None,
        "permalinkUrl": None,
        "createdAt": None
    },
    "sentiment": None,
    "postId": message.get("postId"),
    "commentId": fb_response.get("id"),
    "parentId": message.get("fb_message_id")
  }
  
  backend_auth_header = {
    'Authorization': settings.BACKEND_AUTH_HEADER
  }
  response_save_comment = await PostMethod(
    domain = settings.BACKEND_ENPOINT, 
    endpoint = "/social-message/save", 
    body = comment_info, 
    headers = backend_auth_header
  )
  print("Response save comment: ", response_save_comment)
