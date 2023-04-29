import os
import yaml
import shutil
import asyncio
import concurrent.futures
from rasa.core.agent import Agent
from typing import List, Optional
from rasa.model_training import train
from fastapi import HTTPException, UploadFile
from rasa.utils.endpoints import EndpointConfig

from core.config import settings
from model.fileTrain import FileTrain
from helper.httpMethod import PostMethod
from model.trainAction import TrainAction
from service.createFileTrainModel import create_file_train
from helper.execAsyncFunction import async_function_executor


async def handle_train_model_thread(bot_id: str, service_url: str, files: List[Optional[UploadFile]]):
		with concurrent.futures.ThreadPoolExecutor() as executor:
				future = executor.submit(async_function_executor, handle_train_model,
																	bot_id=bot_id, service_url=service_url, files=files)
				return await asyncio.wrap_future(future)


async def handle_train_model(bot_id: str, service_url: str, files: List[Optional[UploadFile]]):
		folder_location = os.path.join("uploads", bot_id)
		if not os.path.exists(folder_location):
				os.makedirs(folder_location)

		file_train = FileTrain(bot_id, '', '', [])
		action_endpoint = EndpointConfig(url=settings.ACTION_ENDPOINT)

		for file in files:
				if file.filename.endswith('.yml') or file.filename.endswith(".yaml"):
						try:
								file_location = os.path.join(folder_location, file.filename)

								with open(file_location, "wb") as buffer:
										shutil.copyfileobj(file.file, buffer)
										fileName = os.path.splitext(
												os.path.basename(file.filename))[0]

										if hasattr(file_train, fileName):
												setattr(file_train, fileName, file_location)
										else:
												file_train.training_files.append(file_location)

								create_file_train(file_location)
						except yaml.YAMLError as exc:
								raise HTTPException(status_code=400, detail="Invalid YAML file") from exc
		
		result_train = train(domain=file_train.domain, config=file_train.config,
													training_files=file_train.training_files, output="models/",
													fixed_model_name=file_train.fixed_model_name)
		model_path = os.path.join("models", bot_id + ".tar.gz")
		TrainAction.agent_list[bot_id] = Agent.load(
				model_path, action_endpoint=action_endpoint)
		response = await PostMethod(domain=service_url, endpoint="/rasa/training-result", body=result_train)
		return response
