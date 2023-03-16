require('dotenv').config();
const express = require('express');
const { messageFBController } = require('../controllers/index');

const messageFB_router = express.Router();
const PAGE_ACCESS_TOKEN = process.env.PAGE_ACCESS_TOKEN;

messageFB_router.post(
    '/v3/conversations/:id/activities/:id',
    messageFBController.callSendMsg
);

messageFB_router.post(
    '/v3/conversations/:id/activities',
    messageFBController.callSendMsg
);

// messageFB_router.post(
//     "/v3/conversations/8201881179852218/activities",
//     messageFB_controller.callSendAPI
// );

module.exports = messageFB_router;
