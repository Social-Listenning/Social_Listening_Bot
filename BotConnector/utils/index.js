const axios = require('axios');
const { WEB_PAGE_URL, API_KEY } = process.env;


module.exports = {
    checkPageWorking: async (pageID) => {
        try {
            const result = await axios.get(`${WEB_PAGE_URL}/socialTab/${pageID}/working`, {
                headers: { Authorization: API_KEY },
            });
            return result.data.result;
        } catch (e) {
            console.log(e.message);
            return e.message;
        }
    },
    getAccessToken: async (pageID) => {
        try {
            const result = await axios.get(`${WEB_PAGE_URL}/socialTab/${pageID}/accessToken`, {
                headers: { Authorization: API_KEY },
            })
            return result.data.result;
        }
        catch (error) {
            console.log(error.message);
            return error.message;
        }
    }
};
