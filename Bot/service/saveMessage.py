import asyncio
import concurrent.futures
import json
from rasa.shared.constants import DEFAULT_NLU_FALLBACK_INTENT_NAME
from nltk.sentiment import SentimentIntensityAnalyzer

from core.config import settings
from helper.httpMethod import GetMethod

from helper.httpMethod import PostMethod
from model.trainAction import TrainAction
from helper.execAsyncFunction import async_function_executor
from service.intergration.saveSocialMessage import save_social_message

async def handle_message_thread(message: any):
	with concurrent.futures.ThreadPoolExecutor() as executor:
		future = executor.submit(async_function_executor, handle_message, message=message)
		return await asyncio.wrap_future(future)

async def handle_message(message: any):
  backend_auth_header = {
    'Authorization': settings.BACKEND_AUTH_HEADER
  }
  network = await GetMethod(
    domain=settings.BACKEND_ENPOINT, 
    endpoint="/socialNetwork/{0}".format(message.get('recipient_id')),
    header= backend_auth_header
  )
  network_info = network.json()
  network_extend_data = json.loads(network_info.get('extendData'))
  
  sender_response = await GetMethod(
    domain= settings.FACEBOOK_GRAPH_ENDPOINT, 
    endpoint="/{0}?fields=picture,name&access_token={1}".format(message.get('sender_id'), network_extend_data.get('accessToken'))
  )
  sender_info = sender_response.json()
  message["sender"] = {
		"name": sender_info.get('name'),
		"avatar": sender_info.get('picture').get('data').get('url'),
		"id": sender_info.get('id'),
	}

  print(message)
  await save_social_message(message, None)

	# if message.get("recipient_id") in TrainAction.agent_list:
	# 	response = await TrainAction.agent_list.get(message.get("recipient_id")).handle_text(text_message=message.get("text"), sender_id=message.get("sender_id"))          
	# 	if response:
	# 		if len(response) == 0:
	# 			result["text"] = "Sorry, I don't understand"
	# 		else: result["text"] = response[0]["text"]
	# 	else:
	# 		fallback_response = await TrainAction.agent_list.get(message.get("recipient_id")).handle_text(DEFAULT_NLU_FALLBACK_INTENT_NAME, sender_id=message.get("sender_id"))
	# 		print("fallback_response: ", fallback_response)
	# 		if len(fallback_response) == 0:
	# 			result["text"] = "Sorry, I don't understand"
	# 		else: result["text"] = fallback_response[0]["text"]
	# else:
	# 	result["text"] = f"""Model {message.get('recipient_id')} not exist"""

	# response = await PostMethod(domain=message.get("service_url"), endpoint="/rasa/conversations/activities", body=result)
	# return response