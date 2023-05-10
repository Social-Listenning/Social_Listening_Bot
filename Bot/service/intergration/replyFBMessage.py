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
  print(message)
  dialogflow_data =message.get("replyInfo").get("dialogFlow")
  agent_id = list(dialogflow_data.keys())[0]
  list_response_intent = dialogflow_data.get(agent_id)
  
  intent_detect = await PostMethod(
    domain = settings.DIALOGFLOW_ENDPOINT,
    endpoint = "/detect-intent/projects/kltn-381914/locations/us-central1/agents/{0}/sessions/{1}".format(agent_id, message.get('messageId')),
    body = {
      "text": message.get("message"),
      "language_code": "en"
    }
  )
  intent_data = intent_detect.json()
  intent_id = intent_data.get("intent").split('/')[-1]
  response_intent = find_data(list_response_intent, intent_id)
  print(response_intent)
  
  if response_intent is not None:
    response = await PostMethod(
      domain = 'https://graph.facebook.com',
      endpoint = "/{0}/comments?access_token={1}".format(message.get('fb_message_id'), message.get('token')),
      body = {
        "message": response_intent.get("respond")
      },
    )
    fb_response = response.json()
    
    now = datetime.datetime.now()
    iso_time = now.isoformat()

    comment_info = {
      "networkId": message.get("pageId"),
      "message": response_intent.get("respond"),
      "sender": {
        "id": message.get("pageId"),
        "name": message.get("pageName"),
        "avatar": message.get("avatarUrl")
      },
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

def find_data(list, find_data):
  if not find_data:
    for data in list:
      if data.get("hasFallback") == True:
        return data
    
  for data in list:
    print(data.get("intentId"), find_data)
    if find_data == data.get("intentId"):
        return data


  return None