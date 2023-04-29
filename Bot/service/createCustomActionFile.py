import os
import yaml

from helper.enum import IMPORT_LIBRARY_TEXT
from model.trainAction import TrainAction
from service.createFileTrainModel import create_sample_action

def create_file_custom_action():
  folder_actions_location = os.path.join("actions")
  if not os.path.exists(folder_actions_location):
    os.makedirs(folder_actions_location)
    
  file_actions_location = os.path.join(folder_actions_location, "actions.py")
  with open(file_actions_location, 'w') as buffer: 
      buffer.write(IMPORT_LIBRARY_TEXT)  

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
                if action_name not in TrainAction.listAction:
                  TrainAction.listAction.append(action_name)
                  buffer.write(create_sample_action(class_name, action_name, key))  