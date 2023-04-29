import sys
sys.dont_write_bytecode = True


import uvicorn
from fastapi import FastAPI

import nltk
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('vader_lexicon')

from rasa.utils.endpoints import EndpointConfig
from fastapi.middleware.cors import CORSMiddleware
from rasa.core.http_interpreter import RasaNLUHttpInterpreter

from router.router import router
from core.config import settings
from service.loadAllModel import load_all_models
from service.createCustomActionFile import create_file_custom_action

def get_application() -> FastAPI:
  application = FastAPI()
  application.add_middleware(
      CORSMiddleware,
      allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  http_interpreter = RasaNLUHttpInterpreter(EndpointConfig(
    url = settings.RASA_BOT_ENDPOINT,
    params = {},
    headers = {
        "Content-Type": "application/json",
    },
    basic_auth=None,
  ))
  
  application.include_router(router, prefix=settings.API_PREFIX)

  # create_file_custom_action()
  # load_all_models()
  
  return application

app = get_application()
if __name__ == '__main__':
    uvicorn.run("main:app", port=8000, reload = True)
