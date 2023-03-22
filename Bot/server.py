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
        for entity in entities:
            entity_name = entity['entity']
            entity_value = entity['value']
            tracker.set_slot(entity_name, entity_value)
            # SlotSet(entity_name, entity_value)

        slot_values = tracker.slots.get_all()
        dispatcher.utter_template("{utter_key}", tracker, metadata={{"channel": "{channel}", "typeChat": "{type_chat}"}}, **slot_values)
        return []
"""
    return action_temp

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
                except yaml.YAMLError as exc:
                    raise HTTPException(status_code=400, detail="File YAML không hợp lệ") from exc
        future = executor.submit(train_model, fileTrain.fixed_model_name, fileTrain.domain, fileTrain.config, fileTrain.training_files, model_path)
        result = await asyncio.wrap_future(future)
        return "Successful training"

@app.post('/create-file')
async def create_action(files: List[Optional[UploadFile]] = File(...)):
    text_import_library = f"""
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
"""
    for file in files:
        if file.filename.endswith('domain.yml') or file.filename.endswith("domain.yaml"):
            file_content = await file.read()
            domain = yaml.safe_load(file_content)
            if domain is not None:
                filename = "actions.py"
                folder_location = os.path.join("test/action")
                if not os.path.exists(folder_location):
                    os.makedirs(folder_location)
                file_location = os.path.join(folder_location, filename)
                with open(file_location, 'w') as buffer: 
                    buffer.write(text_import_library)   
                    for key in domain['responses'].keys():
                        key_name = key.replace("_", " ").title().replace(" ", "")
                        class_name = 'Action' + key_name
                        action_name = 'action_' + key 
                        domain["actions"].append(action_name)
                        buffer.write(create_sample_action(class_name, action_name, key, "facebook", "comment"))
        if file.filename.endswith('stories.yml') or file.filename.endswith("stories.yaml"):
            file_content = await file.read()
            stories = yaml.safe_load(file_content)
            if stories is not None:
                for story in stories['stories']:
                    for step in story['steps']:
                        for key, value in step.items():
                            if (key == 'action'):
                                step[key] = 'action_' + value 
        if file.filename.endswith('rules.yml') or file.filename.endswith("rules.yaml"):
            file_content = await file.read()
            rules = yaml.safe_load(file_content)
            if rules is not None:
                for rule in rules['rules']:
                    for step in rule['steps']:
                        for key, value in step.items():
                            if (key == 'action'):
                                step[key] = 'action_' + value             
    return 