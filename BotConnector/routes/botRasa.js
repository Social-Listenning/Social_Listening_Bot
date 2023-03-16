require('dotenv').config();
const express = require('express');
const { messageFBController } = require('../controllers/index');

const botRasaRouter = express.Router();

botRasaRouter.post('/bot', messageFBController.callSendMsg);

module.exports = botRasaRouter;
