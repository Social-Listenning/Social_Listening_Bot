const webhookFBRouter = require('./webhookFB');
const botRasaRouter = require('./botRasa');

const route = (app) => {
    app.use('/webhook', webhookFBRouter);
    app.use('/rasa', botRasaRouter);
};

module.exports = route;
