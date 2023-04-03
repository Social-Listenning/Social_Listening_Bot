require('dotenv').config();
const express = require('express');
const { messageFBController } = require('../controllers/index');

const botRasaRouter = express.Router();

botRasaRouter.post('/bot', messageFBController.callSendMsg);
botRasaRouter.post('/conversations/activities', messageFBController.callSendMsg);
botRasaRouter.post('/training-result', messageFBController.trainingResult);

module.exports = botRasaRouter;
