const express = require('express')
const app = express()
const logger = require('morgan');
const port = 8088

app.use(logger('dev'))
app.use(express.json())

const delay = ms => new Promise(resolve => setTimeout(resolve, ms))
app.post('/alpha', async (req, res) => {
    await delay(1000)

    let pkg = req.body;
    if (pkg && pkg.package_status_id >= 5) {
        return res.status(500).json({
            'success': false,
            'message': 'Alpha receive message failed!'
        })
    }

    return res.json({
        'success': true,
        'message': 'Alpha receive message successfully!'
    })
})

app.post('/beta', async (req, res) => {
    await delay(1000)

    let pkg = req.body;
    if (pkg && pkg.package_status_id >= 5) {
        return res.status(500).json({
            'success': false,
            'message': 'Beta receive message failed!'
        })
    }

    return res.json({
        'success': true,
        'message': 'Beta receive message successfully!'
    })
})

app.post('/gamma', async (req, res) => {
    await delay(1000)

    let pkg = req.body;
    if (pkg && pkg.package_status_id >= 5) {
        return res.status(500).json({
            'success': false,
            'message': 'Gamma receive message failed!'
        })
    }

    return res.json({
        'success': true,
        'message': 'Gamma receive message successfully!'
    })
})

app.listen(port, () => {
  console.log(`Server is listening on port ${port}`)
})