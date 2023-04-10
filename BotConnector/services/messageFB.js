const axios = require('axios');
require('dotenv').config();

const { APP_ID, APP_SERCET, PAGE_ACCESS_TOKEN, USER_ACCESS_TOKEN } = process.env;

module.exports = {
    replyMessage: async (message) => {
        try {
            let result;
            if (message && message.channel && message.type_message) {
                if (message.channel.toLowerCase() === 'facebook') {
                    if (message.type_message.toLowerCase() === 'messenger') {
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
                if (message && message.channel.toLowerCase() === 'whatsapp') {
                    console.log(message);
                    if (
                        message.type_message &&
                        message.type_message.toLowerCase() === 'messenger'
                    ) {
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
    replyComment: async (commentID, message) => {
        try {
            console.log('Comment ID: ', commentID);
            const requestBody = {
                message,
            };
            console.log('Message: ', requestBody);

            const params = new URLSearchParams({
                grant_type: 'fb_exchange_token',
                client_id: APP_ID,
                client_secret: APP_SERCET,
                fb_exchange_token: USER_ACCESS_TOKEN,
            });
            console.log(params.toString());

            // const resultPage = await axios.post(
            //     `https://graph.facebook.com/v14.0/oauth/access_token`,
            //     params.toString()
            // );

            // console.log('Page access token');
            // console.log(resultPage.data);

            const result = await axios.post(
                `${process.env.GRAPH_FACEBOOK_API}/v14.0/${commentID}/comments?access_token=${PAGE_ACCESS_TOKEN}`,
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
