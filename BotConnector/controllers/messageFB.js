const authenticateController = require('../controllers/authenticate');
const { messageFBService } = require('../services/index');

module.exports = {
    // Sends response messages via the Send API
    callSendMsg: async function (req, res, next) {
        // Construct the message body
        // Send the HTTP request to the Messenger Platform
        // if (req.body.text && req.body.type === 'message') {
        if (req.body.text) {
            console.log(req.body);
            await messageFBService.replyMessenger(req.body.recipient_id, req.body.text);
            return res.end();
        } else {
            return res.sendStatus(403);
        }
    },
};
