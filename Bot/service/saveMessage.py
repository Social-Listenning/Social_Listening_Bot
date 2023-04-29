import asyncio
import concurrent.futures
from rasa.shared.constants import DEFAULT_NLU_FALLBACK_INTENT_NAME
from nltk.sentiment import SentimentIntensityAnalyzer

from helper.httpMethod import PostMethod
from model.trainAction import TrainAction
from helper.execAsyncFunction import async_function_executor
from service.intergration.saveSocialMessage import save_social_message

async def handle_message_thread(message: any):
	with concurrent.futures.ThreadPoolExecutor() as executor:
		future = executor.submit(async_function_executor, handle_message, message=message)
		return await asyncio.wrap_future(future)

async def handle_message(message: any):
	result = {
		"sender_id": message.get("recipient_id"),
		"recipient_id": message.get("sender_id"),
		"text": "",
		"channel": message.get("channel"),
		"type_message": message.get("type_message"), 
		"metadata": message.get("metadata")
	}
		
	# sia = SentimentIntensityAnalyzer()
	# score = sia.polarity_scores(message.get("text"))
	# sentiment = (score.get("compound") + 1) /2
	# print("Sentiment of user: ", sentiment)
	sentiment = None

	await save_social_message(message, sentiment)

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