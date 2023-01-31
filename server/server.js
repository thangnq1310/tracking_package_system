const express = require('express')
const app = express()
const logger = require('morgan');
const port = 8080

app.use(logger('dev'))
app.use(express.json())

const delay = ms => new Promise(resolve => setTimeout(resolve, ms))
app.post('/alpha', async (req, res) => {
    console.log(req.body)

    await delay(2000)

    return res.json({
        'success': true,
        'message': 'Alpha receive message successfully!'
    })
})

app.post('/beta', async (req, res) => {
    console.log(req.body)

    await delay(25000)

    return res.json({
        'success': true,
        'message': 'Beta receive message successfully!'
    })
})

app.post('/gamma', async (req, res) => {
    console.log(req.body)

    await delay(10000)

    return res.json({
        'success': true,
        'message': 'Gamma receive message successfully!'
    })
})

app.listen(port, () => {
  console.log(`Server is listening on port ${port}`)
})