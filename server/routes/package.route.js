const router = require("express").Router();
const packageController = require("../controllers/package.controller");

router.get("/get-pkg", packageController.getPackage);

router.get("/get-pkgs", packageController.getPackages);

router.post("/update-pkg", packageController.updatePackage);

router.post("/update-pkgs", packageController.updatePackages);

router.post("/update-random-pkgs", packageController.updateRandomPackages);

module.exports = router;
