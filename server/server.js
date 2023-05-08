const express = require("express");
const app = express();
require("dotenv").config();

const db = require("./db");
// Connect to DB
db.sync();

// Use middleware
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

const partner = require("./routes/partner.route.js");
const package = require("./routes/package.route.js");

// Use routes
app.use("/partner", partner);
app.use("/api/package", package);

const port = process.env.PORT || 8088;
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
