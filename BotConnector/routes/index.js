const webhookFBRouter = require('./webhookFB');
const messageFBRouter = require('./messageFB');
const authenticateRouter = require('./authenticate');
const botRasaRouter = require('./botRasa');

const route = (app) => {
    app.use('/webhook', webhookFBRouter);
    app.use('/messageFB', messageFBRouter);
    app.use('/authenticate', authenticateRouter);
    app.use('/rasa', botRasaRouter);
};

module.exports = route;
