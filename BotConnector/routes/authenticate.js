require('dotenv').config();
const express = require('express');
const { authenticateController } = require('../controllers/index');

const authenticate_router = express.Router();

authenticate_router.post(
    '/oauth/token'
    // authenticateController.authenticateBotRequest
);

authenticate_router.post(
    '/',
    // authenticateController.obtainBotToken,
    function (req, res) {
        res.send('Congratulations, you are in a secret area!');
    }
);

module.exports = authenticate_router;
