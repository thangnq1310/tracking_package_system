const { Sequelize } = require("sequelize");

DB_HOST = process.env.DB_HOST;
DB_USER = process.env.DB_USER;
DB_PASSWORD = process.env.DB_PASSWORD;
DB_NAME = process.env.DB_NAME;

const sequelize = new Sequelize(DB_NAME, DB_USER, DB_PASSWORD, {
  host: DB_HOST,
  dialect: "mysql",
  logging: false,
});

module.exports = sequelize;
