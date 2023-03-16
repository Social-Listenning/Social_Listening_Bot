require('dotenv').config();
const express = require('express');
const { webhookFBController } = require('../controllers/index');

const webhookFBRouter = express.Router();

webhookFBRouter.get('/', webhookFBController.subscribeWebhook);
webhookFBRouter.post('/', webhookFBController.sendToBot);

module.exports = webhookFBRouter;
