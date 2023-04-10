const { botRasaService } = require('../services/index');

module.exports = {
    // Sends response messages via the Send API
    callSendMsg: async (req, res) => {
        console.log(req.body);
        // Construct the message body
        // Send the HTTP request to the Messenger Platform
        if (req.body.text) {
            await botRasaService.replyMessage(req.body);
            return res.end();
        } else {
            return res.sendStatus(403);
        }
    },
    trainingResult: async (req, res) => {
        console.log(req.body);
        return res.end();
    },
};
