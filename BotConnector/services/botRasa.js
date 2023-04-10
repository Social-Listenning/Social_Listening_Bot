const axios = require('axios');
require('dotenv').config();

const { PAGE_ACCESS_TOKEN, TELEGRAM_TOKEN } = process.env;

module.exports = {
    replyMessage: async (message) => {
        try {
            let result;
            if (message && message.channel && message.type_message) {
                if (message.channel.toLowerCase() === 'facebook') {
                    if (message.type_message.toLowerCase() === 'message') {
                        const requestBody = {
                            recipient: {
                                id: message.recipient_id,
                            },
                            message: { text: message.text },
                        };
                        result = await axios.post(
                            `${process.env.GRAPH_FACEBOOK_API}/v14.0/me/messages?access_token=${PAGE_ACCESS_TOKEN}`,
                            requestBody
                        );
                    }
                    if (message.type_message.toLowerCase() === 'comment' && message.metadata) {
                        const requestBody = {
                            message: message.text,
                        };
                        result = await axios.post(
                            `${process.env.GRAPH_FACEBOOK_API}/v14.0/${message.metadata.comment_id}/comments?access_token=${PAGE_ACCESS_TOKEN}`,
                            requestBody
                        );
                    }
                }
                if (message.channel.toLowerCase() === 'whatsapp') {
                    console.log(message);
                    if (message.type_message && message.type_message.toLowerCase() === 'message') {
                        const requestBody = {
                            to: message.recipient_id,
                            text: { body: message.text },
                            messaging_product: 'whatsapp',
                            type: 'text',
                        };

                        result = await axios.post(
                            `${process.env.GRAPH_FACEBOOK_API}/v16.0/${message.sender_id}/messages`,
                            requestBody,
                            {
                                headers: {
                                    'Content-Type': 'application/json',
                                    Authorization: `Bearer ${PAGE_ACCESS_TOKEN}`,
                                },
                            }
                        );
                    }
                }
                if (message.channel.toLowerCase() === 'telegram') {
                    console.log(message);

                    if (message.type_message && message.type_message.toLowerCase() === 'message') {
                        const requestBody = {
                            chat_id: message.from,
                            text: 'Hello, World!',
                        };
                        result = await axios.post(
                            `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`,
                            requestBody
                        );
                    }
                }
            }
            console.log(PAGE_ACCESS_TOKEN);
            console.log('Comment id successfully:', result.data);
            return result;
        } catch (error) {
            console.log(error.message);
            console.log(error);
            return error.message;
        }
    },
};
