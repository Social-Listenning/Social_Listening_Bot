from typing import Optional, List
from fastapi import Form, FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from rasa.model_training import train
import yaml
import shutil
import os
import concurrent.futures
import asyncio

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