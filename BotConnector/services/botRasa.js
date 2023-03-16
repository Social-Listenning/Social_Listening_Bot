const axios = require('axios');
const { BOT_RASA_URL } = process.env;

module.exports = {
    sendCommentToBot: async (commentID, message) => {
        try {
            const requestBody = {
                message: typeof message === 'string' ? message : message.text,
                sender: commentID,
            };
            console.log('Message: ', requestBody);
            const result = await axios.post(
                `${BOT_RASA_URL}/webhooks/callback/webhook`,
                requestBody
            );
            console.log(result.data);
            return result.data;
        } catch (error) {
            console.log(error.message);
            return error.message;
        }
    },
    sendMessageToBot: async (senderID, recipientID, message) => {
        try {
            const requestBody = {
                message,
                sender: senderID,
                recipient: recipientID,
            };
            console.log('Message: ', requestBody);
            const result = await axios.post(
                `${BOT_RASA_URL}/webhooks/callback/webhook`,
                requestBody
            );
            console.log(result.data);
            return result.data;
        } catch (error) {
            console.log(error.message);
            return error.message;
        }
    },
};
