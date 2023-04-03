require('dotenv').config();
const express = require('express');
const { webhookFBController } = require('../controllers/index');

const webhookFBRouter = express.Router();

webhookFBRouter.get('/facebook', webhookFBController.subscribeWebhook);
webhookFBRouter.post('/facebook', webhookFBController.sendToBot);

module.exports = webhookFBRouter;
