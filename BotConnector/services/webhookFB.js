require('dotenv').config();
const axios = require('axios');

module.exports = {
    callBot: async function (requestBody) {
        return await axios
            .post('http://localhost:3978/api/messages', requestBody, {
                headers: {
                    'Content-Type': 'application/json',
                    // Authorization: `Bearer ${process.env.AUTHORIZATION_ACCESS_TOKEN}`, //the token is a variable which holds the token
                    // Authorization: `Basic ${sender_psid}`, //the token is a variable which holds the token
                },
            })
            .then(function (response) {
                console.log('message sent!');
            })
            .catch(async function (error) {
                console.log("Don't send!");

                // await authenticateController.authenticateBotConnectorRequest();
                // _this.callBotConnector(webhook_event);
                // console.error("Unable to send message:" + error);
            });
    },
};
