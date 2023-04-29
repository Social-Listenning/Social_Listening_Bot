import os
import yaml

from helper.enum import IMPORT_LIBRARY_TEXT, CREATE_SAMPLE_ACTION
from model.trainAction import TrainAction

def create_file_train(pathFile: str):
	data_file = None
	folder_actions_location = os.path.join("actions")
	file_actions_location = os.path.join(folder_actions_location, "actions.py")

	if not os.path.exists(folder_actions_location):
		os.makedirs(folder_actions_location)
	if not os.path.exists(file_actions_location):
		with open(file_actions_location, 'w') as buffer: 
			buffer.write(IMPORT_LIBRARY_TEXT)

	if os.path.exists(pathFile):
		with open(pathFile, "r", encoding='utf-8') as file:
    
			if file.name.endswith(('domain.yml',"domain.yaml")):
				data_file = yaml.safe_load(file)
				if data_file is not None:
					with open(file_actions_location, 'a') as buffer:
						for key in data_file["responses"].keys():
							key_name = key.replace('_', ' ').title().replace(' ', '')
							class_name = "Action" + key_name
							action_name = "action_" + key 
							data_file["actions"].append(action_name)

							if action_name not in TrainAction.listAction:
								TrainAction.listAction.append(action_name)
								buffer.write(create_sample_action(class_name, action_name, key))

			if file.name.endswith(("stories.yml","stories.yaml")):
				data_file = yaml.safe_load(file)
				if data_file is not None:
					for story in data_file['stories']:
						for step in story['steps']:
							for key, value in step.items():
								if (key == 'action' and "utter_" in value[0:6]):
									step[key] = 'action_' + value

			if file.name.endswith(('rules.yml', 'rules.yaml')):
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

def create_sample_action(class_name, action_name, utter_key): 
    return CREATE_SAMPLE_ACTION.format(class_name = class_name, action_name = action_name, utter_key = utter_key)