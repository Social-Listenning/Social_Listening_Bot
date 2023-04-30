from fastapi import APIRouter

from controller import trainModel, saveMessage, saveBotMessage, calculateSentiment, replyFBMessage

router = APIRouter()

router.include_router(trainModel.router, prefix = "/train")
router.include_router(saveMessage.router, prefix = "/webhook/rasa")
router.include_router(saveBotMessage.router, prefix = "/save-message-bot")
router.include_router(calculateSentiment.router, prefix = "/sentiment")
router.include_router(replyFBMessage.router, prefix = "/reply-message")
