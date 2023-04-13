from typing import Optional, List
from fastapi import Form, FastAPI, File, UploadFile, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from rasa.model_training import train
from rasa.core.agent import Agent
from rasa.utils.endpoints import EndpointConfig
from rasa.shared.constants import DEFAULT_NLU_FALLBACK_INTENT_NAME
from rasa.core.http_interpreter import RasaNLUHttpInterpreter
from textblob import TextBlob
from spacytextblob.spacytextblob import SpacyTextBlob
from dotenv import load_dotenv
from datetime import datetime

import spacy
import httpx
import yaml
import shutil
import os
import concurrent.futures
import asyncio
import glob

load_dotenv()
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

text_import_library = f"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from textblob import TextBlob
"""


# SOCIAL_PAGE_URL=os.getenv('SOCIAL_PAGE_URL')
# RASA_ACTION_URL=os.getenv('RASA_ACTION_URL')
social_page_url="http://localhost:3000/"
action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
http_interpreter = RasaNLUHttpInterpreter(EndpointConfig(
    url="http://localhost:5005/",
    params={},
    headers={
        "Content-Type": "application/json",
    },
    basic_auth=None,
))

agent_list = {}
utter_action_list = []

class FileTrain:
    def __init__(self, fixed_model_name="default_model", domain=None, config=None, training_files=[]):
        self.fixed_model_name = fixed_model_name
        self.domain = domain
        self.config = config
        self.training_files = training_files
      
# def create_sentiment_action(): 
#     return f"""
# class ActionSentiment(Action):
#     def name(self) -> Text:
#         return "action_sentiment"
#     def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         message = tracker.latest_message.get("text")
#         blob = TextBlob(message)
#         sentiment = blob.sentiment.polarity
#         print("blob.sentiment.polarity: ", sentiment)
#         return [SlotSet("textblob_sentiment", {{"polarity": blob.sentiment.polarity, "subjectivity": blob.sentiment.subjectivity, "sentiment": sentiment}})]
# """
      
def create_sample_action(class_name, action_name, utter_key): 
    return f"""
class {class_name}(Action):
    def name(self) -> Text:
        return "{action_name}"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("-------------------------------- Utter Action --------------------------------")
        entities = tracker.latest_message.get("entities")
        print("entities: ", entities)    

        confidence_of_entities = {{}}        
        for entity in entities:
            entity_name = entity.get('entity')  
            entity_value = entity.get('value')         
            confidence_entity = entity.get('confidence_entity')
            print('confidence_entity: ', confidence_entity)
            if tracker.slots.get(entity_name) is None:
                tracker.slots[entity_name] = entity_value
                confidence_of_entities[entity_name] = confidence_entity
            else:
                if confidence_of_entities.get(entity_name) is not None and confidence_entity > confidence_of_entities.get(entity_name):
                    tracker.slots[entity_name] = entity_value
                    confidence_of_entities[entity_name] = confidence_entity
            print("Slot of entity: ", tracker.slots[entity_name])

        dispatcher.utter_message(response="{utter_key}", **dict(tracker.slots.items()))        
        return []
"""

async def create_file_train(pathFile: str):
    data_file = None
    folder_actions_location = os.path.join("actions")
    file_actions_location = os.path.join(folder_actions_location, "actions.py")
    if not os.path.exists(folder_actions_location):
        os.makedirs(folder_actions_location)
    if not os.path.exists(file_actions_location):
        with open(file_actions_location, 'w') as buffer: 
            buffer.write(text_import_library)

    if os.path.exists(pathFile):
        with open(pathFile, "r", encoding='utf-8') as file:
            if file.name.endswith('domain.yml') or file.name.endswith("domain.yaml"):
                data_file = yaml.safe_load(file)
                if data_file is not None:
                    with open(file_actions_location, 'a') as buffer:
                        for key in data_file["responses"].keys():
                            key_name = key.replace('_', ' ').title().replace(' ', '')
                            class_name = "Action" + key_name
                            action_name = "action_" + key 
                            data_file["actions"].append(action_name)
                            if action_name not in utter_action_list:
                                utter_action_list.append(action_name)
                                buffer.write(create_sample_action(class_name, action_name, key))
                # data_file["slots"] = {}
                # data_file["slots"]["textblob_sentiment"] = {}
                # data_file["slots"]["textblob_sentiment"]["type"] = "any"
                # data_file["slots"]["textblob_sentiment"]["mappings"] = [{"type": "custom"}]

            if file.name.endswith("stories.yml") or file.name.endswith("stories.yaml"):
                data_file = yaml.safe_load(file)
                if data_file is not None:
                    for story in data_file['stories']:
                        for step in story['steps']:
                            for key, value in step.items():
                                if (key == 'action' and "utter_" in value[0:6]):
                                    step[key] = 'action_' + value

            if file.name.endswith('rules.yml') or file.name.endswith("rules.yaml"):
                data_file = yaml.safe_load(file)
                if data_file is not None:
                    for rule in data_file['rules']:
                        for step in rule['steps']:
                            for key, value in step.items():
                                if (key == 'action' and "utter_" in value[0:6]):
                                    step[key] = 'action_' + value

    if data_file is not None: 
        with open(pathFile, 'w') as file:
            yaml.dump(data_file, file)

def create_file_custom_action():
    folder_actions_location = os.path.join("actions")
    if not os.path.exists(folder_actions_location):
        os.makedirs(folder_actions_location)
    file_actions_location = os.path.join(folder_actions_location, "actions.py")
    with open(file_actions_location, 'w') as buffer: 
        buffer.write(text_import_library)  

    uploads_path = "./uploads"
    if not os.path.exists(uploads_path):
        os.makedirs(uploads_path)
    folders_path = [f.path for f in os.scandir(uploads_path) if f.is_dir()]
    for folder_path in folders_path:
        file_domain_location = os.path.join(folder_path, "domain.yml")
        if os.path.exists(file_domain_location):
            with open(file_domain_location, "r", encoding='utf-8') as file:
                data_file = yaml.safe_load(file)
                if data_file is not None:
                    with open(file_actions_location, 'a') as buffer: 
                        if "responses" in data_file:
                            for key in data_file.get("responses").keys():
                                key_name = key.replace('_', ' ').title().replace(' ', '')
                                class_name = "Action" + key_name
                                action_name = "action_" + key 
                                data_file["actions"].append(action_name)
                                if action_name not in utter_action_list:
                                    utter_action_list.append(action_name)
                                    buffer.write(create_sample_action(class_name, action_name, key))        

def load_all_model():
    # Define the path to the models directory
    models_dir = 'models/'
    # Get a list of all the .tar.gz files in the models directory
    model_files = glob.glob(models_dir + '*.tar.gz')
    # Iterate through the list of model files
    for model_file in model_files:
        filename = os.path.basename(model_file)
        model_path = os.path.join("models", filename)
        if os.path.exists(model_path):
            model_id = os.path.splitext(os.path.splitext(os.path.basename(filename))[0])[0]
            agent_list[model_id] = Agent.load(model_path, action_endpoint=action_endpoint)

def train_model(model_name, domain, config, training_files, model_path):
    return train(domain=domain, config=config, training_files=training_files, output=model_path, fixed_model_name=model_name)

def agent_load_model(bot_id, model_path):
    agent_list[bot_id] = Agent.load(model_path, action_endpoint=action_endpoint)
    return
  
async def agent_handle_text(message):
    return await agent_list.get(message.get("recipient_id")).handle_text(text_message=message.get("text"), sender_id=message.get("sender_id"))

async def handle_train_model(bot_id: str, service_url: str, files: List[Optional[UploadFile]]):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        folder_location = os.path.join("uploads", bot_id)
        if not os.path.exists(folder_location):
            os.makedirs(folder_location)
        fileTrain = FileTrain(bot_id, '', '', [])    
        for file in files:
            if file.filename.endswith('.yml') or file.filename.endswith(".yaml"):
                try:            
                    file_location = os.path.join(folder_location, file.filename)
                    with open(file_location, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                        fileName=os.path.splitext(os.path.basename(file.filename))[0]
                        if hasattr(fileTrain, fileName):
                            setattr(fileTrain, fileName, file_location)
                        else:
                            fileTrain.training_files.append(file_location)
                    await create_file_train(file_location)
                except yaml.YAMLError as exc:
                    raise HTTPException(status_code=400, detail="Invalid YAML file") from exc
        future_train = executor.submit(train_model, fileTrain.fixed_model_name, fileTrain.domain, fileTrain.config, fileTrain.training_files, "models/")
        result_train = await asyncio.wrap_future(future_train)
        model_path = os.path.join("models", bot_id + ".tar.gz")
        future_load = executor.submit(agent_load_model, bot_id, model_path)
        await asyncio.wrap_future(future_load)
        async with httpx.AsyncClient() as client:
            print(service_url)
            if service_url.endswith("/"):
                url = service_url + "rasa/training-result"
            else:
                url = service_url + "/rasa/training-result"
            response = await client.post(url=url, json=result_train)
            print(response.status_code)
        return result_train

async def handle_message(message: any):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = {
            "sender_id": message.get("recipient_id"),
            "recipient_id": message.get("sender_id"),
            "text": "",
            "channel": message.get("channel"),
            "type_message": message.get("type_message"), 
            "metadata": message.get("metadata")
        }
        
        doc = nlp(message.get('text'))
        # sentiment = doc.sentiment
        sentiment = doc._.blob.polarity
        print("Sentiment of user: ", sentiment)  

        result_sentiment = {
            "networkId": message.get("recipient_id"),
            "message": message.get("text"),
            "sender": message.get("sender_id"),
            "createdAt": message.get("metadata").get("comment_created_time"),
            "type": message.get("type_message"),
            "parent": {
                "postId": message.get("metadata").get("post_id"),
                "message": message.get("metadata").get("post_message"),
                "permalinkUrl": message.get("metadata").get("permalink_url"),
                "createdAt": message.get("metadata").get("post_created_time")
            },
            "sentiment": sentiment,
            "postId": message.get("metadata").get("post_id"),
            "commentId": message.get("metadata").get("comment_id"),
            "parentId": message.get("metadata").get("parent_id")
        }

        async with httpx.AsyncClient() as client:
            headers = {'Authorization': '5p3cti4L-t0k3n'}
            # print("Headers", headers) 
            # print("Body", result_sentiment) 
            if social_page_url.endswith("/"):
                url = social_page_url + "social-message/save"
            else:
                url = social_page_url + "/social-message/save"
            # response_save_sentiment = await client.post(url=url, headers=headers, json=result_sentiment)
            # print("Response save sentiment", response_save_sentiment)

        if message.get("recipient_id") in agent_list:
            future = executor.submit(agent_handle_text, message)
            response = await asyncio.wrap_future(future)
            # print("--------------------------------")
            # print("response:", response)
            # print("--------------------------------")           
            if response:
                if len(response) == 0:
                    result["text"] = "Sorry, I don't understand"
                else: result["text"] = response[0]["text"]
            else:
                fallback_response = await agent_list.get(message.get("recipient_id")).handle_text(DEFAULT_NLU_FALLBACK_INTENT_NAME, sender_id=message.get("sender_id"))
                print("fallback_response: ", fallback_response)
                if len(fallback_response) == 0:
                    result["text"] = "Sorry, I don't understand"
                else: result["text"] = fallback_response[0]["text"]
        else:
            result["text"] = f"""Model {message.get('recipient_id')} not exist"""

        
        doc = nlp(result["text"])
        sentiment = doc._.blob.polarity
        print("Sentiment of bot: ", sentiment) 

        result_sentiment = {
            "networkId": message.get("recipient_id"),
            "message": result["text"],
            "sender": message.get("recipient_id"),
            "createdAt": datetime.now().isoformat(),
            "type": "Bot",
            "parent": {
                "postId": message.get("metadata").get("post_id"),
                "message": message.get("metadata").get("post_message"),
                "permalinkUrl": message.get("metadata").get("permalink_url"),
                "createdAt": message.get("metadata").get("post_created_time")
            },
            "sentiment": sentiment,
            "postId": message.get("metadata").get("post_id"),
            "commentId": message.get("metadata").get("comment_id"), # Id bot cmt reply có éo đâu :)
            "parentId": message.get("metadata").get("comment_id") # Id này là Id bot reply được rồi
            # Này phải để page trên fb reply gửi về lại mới có comment_id mới được
        }

        async with httpx.AsyncClient() as client:
            headers = {'Authorization': '5p3cti4L-t0k3n'}
            # print("Headers", headers) 
            # print("Body", result_sentiment) 
            if social_page_url.endswith("/"):
                url = social_page_url + "social-message/save"
            else:
                url = social_page_url + "/social-message/save"
            # response_save_sentiment = await client.post(url=url, headers=headers, json=result_sentiment)
            # print("Response save sentiment", response_save_sentiment)

        async with httpx.AsyncClient() as client:
            # print(message.get("service_url"))
            if message.get("service_url").endswith("/"):
                url = message.get("service_url") + "rasa/conversations/activities"
            else:
                url = message.get("service_url") + "/rasa/conversations/activities"
            response = await client.post(url=url, json=result)
            # print(response.status_code)
        return result

@app.post('/train')
async def handling_model(background_tasks: BackgroundTasks, bot_id: str = Form(), service_url: str = Form(), files: List[Optional[UploadFile]] = File(...)):
    background_tasks.add_task(handle_train_model, bot_id, service_url, files)
    return {"message": "Send webhook successfully"}

@app.post('/webhook/rasa')
async def handling_message(background_tasks: BackgroundTasks, request: Request):
    message = await request.json()
    background_tasks.add_task(handle_message, message)
    return {"message": "Send webhook successfully"}

create_file_custom_action()
print("utter_action_list", utter_action_list)
load_all_model()
print(agent_list)

nlp = spacy.load("en_core_web_trf")

@spacy.Language.component("sentiment_analysis")
def analyze_sentiment(doc):
    sentiments = []
    for sentence in doc.sents:
        blob = TextBlob(sentence.text)
        # print(blob.sentiment)
        # print(blob.sentiment_assessments)
        sentiments.append(blob.sentiment.polarity)
    doc.sentiment = sum(sentiments) / len(sentiments)
    return doc

nlp.add_pipe("sentiment_analysis", name="sentiment_analysis", last=True)
nlp.add_pipe("spacytextblob")

@app.post('/sentiment')
async def handling_sentiment(request: Request):
    message = await request.json()
    doc = nlp(message.get('text'))
    print(doc.sentiment)
    print(doc._.blob.polarity)
    print(doc._.blob.subjectivity)
    return doc.sentiment