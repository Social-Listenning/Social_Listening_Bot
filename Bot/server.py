from typing import Optional, List
from fastapi import Form, FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rasa.model_training import train
import yaml
import shutil
import os
import concurrent.futures
import asyncio
import re

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.post('/create-file')
async def create_handle_action_file(botId: str = Form(), file: Optional[UploadFile] = File(...)):
    data_file = None
    text_import_library = f"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from operator import itemgetter
"""
    if file.filename.endswith('domain.yml') or file.filename.endswith("domain.yaml"):
        file_content = await file.read()
        data_file = yaml.safe_load(file_content)
        if data_file is not None:
            filename = "actions.py"
            folder_location = os.path.join("uploads", botId, "actions")
            print(folder_location)
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
    if file.filename.endswith('stories.yml') or file.filename.endswith("stories.yaml"):
        file_content = await file.read()
        data_file = yaml.safe_load(file_content)
        return data_file
        if data_file is not None:
            for story in data_file['stories']:
                for step in story['steps']:
                    for key, value in step.items():
                        if (key == 'action' and "utter_" in value[0:6]):
                            step[key] = 'action_' + value 
    if file.filename.endswith('rules.yml') or file.filename.endswith("rules.yaml"):
        file_content = await file.read()
        data_file = yaml.safe_load(file_content)
        if data_file is not None:
            for rule in data_file['rules']:
                for step in rule['steps']:
                    for key, value in step.items():
                        if (key == 'action' and "utter_" in value[0:6]):
                            step[key] = 'action_' + value
    if data_file is None:  
        return data_file
    # file.seek(0)
    # yaml.dump(data_file, file)
    # print(data_file)
    # file.truncate()
    return data_file

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


def train_model(model_name, domain, config, training_files, model_path):
    return train(domain=domain, config=config, training_files=training_files, output=model_path, fixed_model_name=model_name)

@app.post('/train')
async def create_upload_file(botId: str = Form(), files: List[Optional[UploadFile]] = File(...)):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        model_path = "models/"
        fileTrain = FileTrain(botId, '', '', [])    
        for file in files:
            if file.filename.endswith('.yml') or file.filename.endswith(".yaml"):
                try:            
                    folder_location = os.path.join("uploads", botId)
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
                    await create_handle_action(botId, file_location)
                except yaml.YAMLError as exc:
                    raise HTTPException(status_code=400, detail="Invalid YAML file") from exc
        future = executor.submit(train_model, fileTrain.fixed_model_name, fileTrain.domain, fileTrain.config, fileTrain.training_files, model_path)
        result = await asyncio.wrap_future(future)
        return "Successful training"

