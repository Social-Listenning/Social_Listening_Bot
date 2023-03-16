require('dotenv').config();
const express = require('express');
const { webhookFBController } = require('../controllers/index');
const { messageFBService, botRasaService } = require('../services/index');

const webhookFBRouter = express.Router();
const VERIFY_TOKEN = process.env.VERIFY_TOKEN;

webhookFBRouter.get('/', webhookFBController.subscribeWebhook);

webhookFBRouter.post('/', (req, res) => {
    let body = req.body;
    console.log(body);
    // console.log(body.entry[0].changes);
    if (body.object === 'page') {
        // Iterate over each entry - there may be multiple if batched
        body.entry.forEach(async function (entry) {
            // Gets the body of the webhook event
            let value =
                (entry.changes && entry.changes[0].value) ||
                (entry.messaging && entry.messaging[0]);

            console.log(value);
            if (value && value.comment_id && value.message) {
                // messageFBService.replyCmt(value.comment_id, value.message);
                await botRasaService.replyCmt(value.comment_id, value.message);
            } else if (value && value.sender.id && value.recipient.id && value.message) {
                await botRasaService.replyMessenger(
                    value.sender.id,
                    value.recipient.id,
                    value.message.text
                );
            }
        });
        // Return a '200 OK' response to all events
        return res.status(200).send('EVENT_RECEIVED');
    }
    if (body.object === 'instagram') {
        console.log(body.entry[0].changes);
        return res.sendStatus(200);
    } else {
        // Return a '404 Not Found' if event is not from a page subscription
        return res.sendStatus(404);
    }
});

module.exports = webhookFBRouter;
