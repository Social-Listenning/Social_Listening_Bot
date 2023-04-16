const axios = require('axios');
const { WEB_PAGE_URL } = process.env;

module.exports = {
    checkPageWorking: async (pageID) => {
        try {
            const result = await axios.get(`${WEB_PAGE_URL}/socialTab/${pageID}/working`, {
                headers: { Authorization: '5p3cti4L-t0k3n' },
            });
            return result.data.result;
        } catch (e) {
            console.log(e.message);
            return e.message;
        }
    },
};
