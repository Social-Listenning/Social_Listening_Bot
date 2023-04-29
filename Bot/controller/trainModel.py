from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile
from service.trainModel import handle_train_model_thread

router = APIRouter()

@router.post("")
async def handling_model(
  background_tasks: BackgroundTasks, bot_id: str = Form(), service_url: str = Form(),
  files: List[Optional[UploadFile]] = File(...)):
    background_tasks.add_task(handle_train_model_thread, bot_id, service_url, files)
    return {"message": "Send webhook successfully"}