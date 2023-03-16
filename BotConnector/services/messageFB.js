const axios = require('axios');
require('dotenv').config();

const { APP_ID, APP_SERCET, PAGE_ACCESS_TOKEN, USER_ACCESS_TOKEN } = process.env;

module.exports = {
    replyMessenger: async (recipientID, message) => {
        try {
            let requestBody = {
                recipient: {
                    id: recipientID,
                },
                message: { text: message },
            };
            console.log(PAGE_ACCESS_TOKEN);
            const result = await axios.post(
                `${process.env.GRAPH_FACEBOOK_API}/v14.0/me/messages?access_token=${PAGE_ACCESS_TOKEN}`,
                requestBody
            );
            console.log(result.data);
            return result.data;
        } catch (error) {
            console.log(error.message);
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
