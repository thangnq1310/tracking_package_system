const statusAllowed = require('../constants')

const delay = ms => new Promise(resolve => setTimeout(resolve, ms))

const partnerController = {
    webhookAlpha: async (req, res) => {
        await delay(200)

        let pkg = req.body;
        if (!statusAllowed.includes(pkg.package_status_id)) {
            return res.status(500).json({
                'success': false,
                'message': 'Alpha receive message failed!'
            })
        }

        return res.json({
            'success': true,
            'message': 'Alpha receive message successfully!'
        })
    },
    webhookBeta: async (req, res) => {
        await delay(400)

        let pkg = req.body;
        if (!statusAllowed.includes(pkg.package_status_id)) {
            return res.status(500).json({
                'success': false,
                'message': 'Beta receive message failed!'
            })
        }

        return res.json({
            'success': true,
            'message': 'Beta receive message successfully!'
        })
    },
    webhookGamma: async (req, res) => {
        await delay(600)

        let pkg = req.body;
        if (!statusAllowed.includes(pkg.package_status_id)) {
            return res.status(500).json({
                'success': false,
                'message': 'Gamma receive message failed!'
            })
        }

        return res.json({
            'success': true,
            'message': 'Gamma receive message successfully!'
        })
    }
}

module.exports = partnerController;