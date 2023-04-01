from typing import Optional, List
from fastapi import Form, FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from rasa.model_training import train
from rasa.core.agent import Agent
from rasa.utils.endpoints import EndpointConfig
from rasa.shared.constants import DEFAULT_CORE_SUBDIRECTORY_NAME, DEFAULT_NLU_FALLBACK_INTENT_NAME
from rasa.core.http_interpreter import RasaNLUHttpInterpreter
from rasa.core.channels import UserMessage

from rasa.core.lock_store import InMemoryLockStore
from rasa.core.nlg import NaturalLanguageGenerator
from rasa.core.tracker_store import InMemoryTrackerStore
from rasa.core.processor import MessageProcessor

import yaml
import shutil
import os
import concurrent.futures
import asyncio
import glob

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
http_interpreter = RasaNLUHttpInterpreter(EndpointConfig(
    url="http://localhost:5005/",
    params={},
    headers={
        "Content-Type": "application/json",
    },
    basic_auth=None,
))
agentList = {}

class FileTrain:
    def __init__(self, fixed_model_name="default_model", domain=None, config=None, training_files=[]):
        self.fixed_model_name = fixed_model_name
        self.domain = domain
        self.config = config
        self.training_files = training_files
    
def create_sample_action(class_name, action_name, utter_key, channel, type_chat): 
    action_temp = f"""
class {class_name}(Action):
    def name(self) -> Text:
        return "{action_name}"
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        print(entities)        
        
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

        dispatcher.utter_template("{utter_key}", tracker, metadata={{"channel": "{channel}", "typeChat": "{type_chat}"}}, **dict(tracker.slots.items()))        
        return []
"""
    return action_temp

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
            model_id =  os.path.splitext(os.path.splitext(os.path.basename(filename))[0])[0]
            agentList[model_id] = Agent.load(model_path, action_endpoint=action_endpoint)

def train_model(model_name, domain, config, training_files, model_path):
    return train(domain=domain, config=config, training_files=training_files, output=model_path, fixed_model_name=model_name)
    
async def create_handle_action(botId: str, pathFile: str):
    data_file = None
    text_import_library = f"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
"""
    with open(pathFile, "r", encoding='utf-8') as file:
        if file.name.endswith('domain.yml') or file.name.endswith("domain.yaml"):
            data_file = yaml.safe_load(file)
            if data_file is not None:
                filename = "actions.py"
                folder_location = os.path.join("uploads", botId, "actions")
                if not os.path.exists(folder_location):
                    os.makedirs(folder_location)
                file_location = os.path.join(folder_location, filename)
                with open(file_location, 'w') as buffer: 
                    buffer.write(text_import_library)   
                    for key in data_file['responses'].keys():
                        key_name = key.replace("_", " ").title().replace(" ", "")
                        class_name = 'Action' + key_name
                        action_name = 'action_' + key 
                        data_file["actions"].append(action_name)
                        buffer.write(create_sample_action(class_name, action_name, key, "facebook", "comment"))
        if file.name.endswith('stories.yml') or file.name.endswith("stories.yaml"):
            data_file = yaml.safe_load(file)
            if data_file is not None:
                for story in data_file['stories']:
                    for step in story['steps']:
                        for key, value in step.items():
                            if (key == 'action' and "utter_" in value[0:6]):
                                step[key] = 'action_' + value
        if file.name.endswith('rules.yml') or file.name.endswith("rules.yaml"):
            print(file.name)
            data_file = yaml.safe_load(file)
            if data_file is not None:
                for rule in data_file['rules']:
                    for step in rule['steps']:
                        for key, value in step.items():
                            if (key == 'action' and "utter_" in value[0:6]):
                                step[key] = 'action_' + value 
    if data_file is None:  
        return 
    with open(pathFile, 'w') as file:
        yaml.dump(data_file, file)
    # file.truncate()
    return 

@app.post('/train')
async def create_upload_file(bot_id: str = Form(), files: List[Optional[UploadFile]] = File(...)):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        fileTrain = FileTrain(bot_id, '', '', [])    
        for file in files:
            if file.filename.endswith('.yml') or file.filename.endswith(".yaml"):
                try:            
                    folder_location = os.path.join("uploads", bot_id)
                    if not os.path.exists(folder_location):
                        os.makedirs(folder_location)
                    file_location = os.path.join(folder_location, file.filename)
                    with open(file_location, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                        fileName=os.path.splitext(os.path.basename(file.filename))[0]
                        if hasattr(fileTrain, fileName):
                            setattr(fileTrain, fileName, file_location)
                        else:
                            fileTrain.training_files.append(file_location)
                    await create_handle_action(bot_id, file_location)
                except yaml.YAMLError as exc:
                    raise HTTPException(status_code=400, detail="Invalid YAML file") from exc
        future = executor.submit(train_model, fileTrain.fixed_model_name, fileTrain.domain, fileTrain.config, fileTrain.training_files, "models/")
        result = await asyncio.wrap_future(future)
        model_path = os.path.join("models", bot_id + ".tar.gz")
        agentList[bot_id] = Agent.load(model_path, action_endpoint=action_endpoint)
        return result
        return "Successful training"

@app.post('/webhooks/rasa')
async def receive_message(request: Request):
    message = await request.json()
    if message.get('receive_id') in agentList:
        response = await agentList.get(message.get('receive_id')).handle_text(text_message=message.get('message'), sender_id=message.get('sender_id'))
        print('--------------------------------')
        print("response:")
        print(response)
        print('--------------------------------')           
        if response:
            if len(response) == 0:
                return {"response": "Sorry, I don't understand"}
            return {"response": response[0]["text"]}
        else:
            fallback_response = await agentList.get(message.get('receive_id')).handle_text(DEFAULT_NLU_FALLBACK_INTENT_NAME, sender_id=message.get('sender_id'))
            print("fallback_response: ", fallback_response)
            if len(fallback_response) == 0:
                return {"response": "Sorry, I don't understand"}
            return {"response": fallback_response[0]["text"]}
    return {"response": f"""Model {message.get('receive_id')} not exist"""}

load_all_model()
print(agentList)