const axios = require('axios');
const { BOT_RASA_URL } = process.env;

module.exports = {
    sendCommentToBot: async (value) => {
        try {
            const { commentID, message } = value;
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
    sendMessageToBot: async (value) => {
        try {
            const { sender, recipient, message } = value;
            const requestBody = {
                text: message && message.text,
                sender_id: sender && sender.id,
                recipient_id: recipient && recipient.id,
                channel: 'facebook',
                type_message: 'messenger',
                service_url: 'http://localhost:8080',
            };
            console.log('Message: ', requestBody);
            const result = await axios.post(`${BOT_RASA_URL}/webhook/rasa`, requestBody);
            console.log(result.data);
            return result.data;
        } catch (error) {
            console.log(error.message);
            return error.message;
        }
    },
};
