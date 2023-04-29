import glob
import os

from model.trainAction import TrainAction
from rasa.core.agent import Agent

from core.config import settings

def load_all_models():
  models_dir = 'models/'
  model_files = glob.glob(models_dir + '*.tar.gz')
  
  for model_file in model_files:
    filename = os.path.basename(model_file)
    model_path = os.path.join("models", filename)
    if os.path.exists(model_path):
      model_id = os.path.splitext(os.path.splitext(os.path.basename(filename))[0])[0]
      TrainAction.agent_list[model_id] = Agent.load(model_path, action_endpoint = settings.ACTION_ENDPOINT)