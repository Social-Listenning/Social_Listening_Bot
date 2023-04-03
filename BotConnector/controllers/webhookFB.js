const { botRasaService } = require('../services/index');
const { VERIFY_TOKEN } = process.env;

module.exports = {
    subscribeWebhook: (req, res) => {
        // Parse the query params
        let mode = req.query['hub.mode'];
        let token = req.query['hub.verify_token'];
        let challenge = req.query['hub.challenge'];
        // Check if a token and mode is in the query string of the request
        if (mode && token) {
            // Check the mode and token sent is correct
            if (mode === 'subscribe' && token === VERIFY_TOKEN) {
                // Respond with the challenge token from the request
                console.log('Subscribe webhook successfully');
                return res.status(200).send(challenge);
            } else {
                // Respond with '403 Forbidden' if verify tokens do not match
                return res.sendStatus(403);
            }
        }
    },

    sendToBot: async (req, res) => {
        try {
            let body = req.body;
            console.log(body);
            if (body.object === 'page') {
                // Iterate over each entry - there may be multiple if batched
                body.entry.forEach(async (entry) => {
                    // Gets the body of the webhook event
                    const value =
                        (entry.changes && entry.changes[0].value) ||
                        (entry.messaging && entry.messaging[0]);
                    console.log('value', value);
                    if (value && value.comment_id && value.message) {
                        // messageFBService.replyCmt(value.comment_id, value.message);
                        // await botRasaService.sendCommentToBot(value.comment_id, value.message);
                    } else if (value && value.sender && value.recipient && value.message) {
                        await botRasaService.sendMessageToBot(value);
                    } else {
                        return res.sendStatus(404);
                    }
                });
                // Return a '200 OK' response to all events
                return res.status(200).send('EVENT_RECEIVED');
            }
            if (body.object === 'instagram') {
                console.log(body.entry[0].changes);
                return res.sendStatus(404);
            } else {
                // Return a '404 Not Found' if event is not from a page subscription
                return res.sendStatus(404);
            }
        } catch (error) {
            return res.status(500).send(error.message);
        }
    },
};
