require('dotenv').config();
const express = require('express');
const { botRasaController, messageFBController } = require('../controllers/index');

const botRasaRouter = express.Router();

botRasaRouter.post(
    '/bot',
    // botRasaController.callSendMsg
    messageFBController.callSendMsg
);

module.exports = botRasaRouter;
