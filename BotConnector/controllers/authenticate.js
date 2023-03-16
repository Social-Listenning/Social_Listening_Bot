require('dotenv').config();
const express = require('express');
const axios = require('axios');
const OAuth2Server = require('oauth2-server'),
    Request = OAuth2Server.Request,
    Response = OAuth2Server.Response;

const app = express();

app.oauth = new OAuth2Server({
    model: require('../connector/model'),
    accessTokenLifetime: 60 * 60,
    allowBearerTokensInQueryString: true,
});

module.exports = {
    // Sends response messages via the Send API
    // obtainBotConnectorToken: async () => {
    //     // Construct the message body
    //     // Send the HTTP request to the Messenger Platform
    //     console.log(process.env.AUTHORIZATION_ACCESS_TOKEN);
    //     return await axios
    //         .post(
    //             "http://localhost:3978/authenticate",
    //             {
    //                 grant_type: "client_credentials",
    //             },
    //             {
    //                 headers: {
    //                     "Content-Type": "application/json",
    //                     Authorization: `Bearer ${process.env.AUTHORIZATION_ACCESS_TOKEN}`,
    //                 },
    //             }
    //         )
    //         .then(function (response) {
    //             return true;
    //         })
    //         .catch(function (error) {
    //             // console.error(error.config.headers);
    //             return false;
    //         });
    // },
    authenticateBotConnectorRequest: async () => {
        // Construct the message body
        // Send the HTTP request to the Messenger Platform
        return await axios
            .post(
                'http://localhost:3978/authenticate/oauth/token',
                {
                    grant_type: 'password',
                    username: '123',
                    password: '123',
                },
                {
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: 'Basic YXBwbGljYXRpb246c2VjcmV0', //the token is a variable which holds the token
                        // Authorization: `Basic ${sender_psid}`, //the token is a variable which holds the token
                    },
                }
            )
            .then(function (response) {
                process.env.AUTHORIZATION_ACCESS_TOKEN = response.data.accessToken;
                process.env.AUTHORIZATION_REFRESH_TOKEN = response.data.refreshToken;
                return true;
            })
            .catch(function (error) {
                console.error(error.message);
                return false;
            });
    },
    obtainBotToken: async (req, res, next) => {
        req.headers['content-type'] = 'application/x-www-form-urlencoded';

        var request = new Request(req);
        var response = new Response(res);

        return await app.oauth
            .authenticate(request, response)
            .then(function (response) {
                return true;
            })
            .catch(function (error) {
                // console.error(error.config.headers);
                return false;
            });
    },
    authenticateBotRequest: async (req, res) => {
        req.headers['content-type'] = 'application/x-www-form-urlencoded';

        var request = new Request(req);
        var response = new Response(res);

        return await app.oauth
            .token(request, response)
            .then(function (token) {
                res.json(token);
            })
            .catch(function (err) {
                res.status(err.code || 500).json(err);
            });
    },
};
