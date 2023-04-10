const axios = require('axios');
const { checkPageWorking } = require('../utils');

const { BOT_RASA_URL } = process.env;

module.exports = {
    sendCommentToBot: async (value) => {
        try {
            const { from, post_id, comment_id, message } = value;
            const botId = post_id.split('_')[0];
            if (await checkPageWorking(botId)) {
                if (from.id !== botId) {
                    const requestBody = {
                        text: message,
                        sender_id: from && from.id,
                        recipient_id: botId,
                        channel: 'facebook',
                        type_message: 'comment',
                        service_url: 'http://localhost:8080',
                        metadata: {
                            post_id: post_id,
                            comment_id: comment_id,
                        },
                    };
                    console.log('Message: ', requestBody);
                    const result = await axios.post(`${BOT_RASA_URL}/webhook/rasa`, requestBody);
                    console.log(result.data);
                    return result.data;
                }
            }
            return;
        } catch (error) {
            console.log(error.message);
            return error.message;
        }
    },
    sendMessageToBot: async (value) => {
        try {
            const { sender, recipient, message } = value;
            if (await checkPageWorking(recipient.id)) {
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
            }
            return;
        } catch (error) {
            console.log(error.message);
            return error.message;
        }
    },
    sendMessageWhapsAppToBot: async (value) => {
        try {
            const { messaging_product, metadata, messages } = value;
            if (await checkPageWorking(metadata.phone_number_id)) {
                if (messages && messages.length) {
                    const requestBody = {
                        text: messages[0].text && messages[0].text.body,
                        sender_id: messages[0].from,
                        // recipient_id: metadata && metadata.display_phone_number,
                        recipient_id: metadata && metadata.phone_number_id,
                        channel: messaging_product || 'whatsapp',
                        type_message: 'messenger',
                        service_url: 'http://localhost:8080',
                    };
                    console.log('Message: ', requestBody);
                    const result = await axios.post(`${BOT_RASA_URL}/webhook/rasa`, requestBody);
                    console.log(result.data);
                    return result.data;
                }
            }
            return;
        } catch (error) {
            console.log(error.message);
            return error.message;
        }
    },
};
