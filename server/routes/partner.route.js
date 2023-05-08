const router = require("express").Router();
const partnerController = require("../controllers/partner.controller");

router.post("/alpha", partnerController.webhookAlpha);

router.post("/beta", partnerController.webhookBeta);

router.post("/gamma", partnerController.webhookGamma);

module.exports = router;
