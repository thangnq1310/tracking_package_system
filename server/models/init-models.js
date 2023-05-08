var DataTypes = require("sequelize").DataTypes;
var _addresses = require("./addresses.model");
var _cods = require("./cods.model");
var _customers = require("./customers.model");
var _packages = require("./packages.model");
var _shops = require("./shops.model");
var _stations = require("./stations.model");
const sequelize = require('../db')


function initModels() {
  var addresses = _addresses(sequelize, DataTypes);
  var cods = _cods(sequelize, DataTypes);
  var customers = _customers(sequelize, DataTypes);
  var packages = _packages(sequelize, DataTypes);
  var shops = _shops(sequelize, DataTypes);
  var stations = _stations(sequelize, DataTypes);

  customers.belongsTo(addresses, { as: "address", foreignKey: "address_id"});
  addresses.hasMany(customers, { as: "customers", foreignKey: "address_id"});
  stations.belongsTo(addresses, { as: "address", foreignKey: "address_id"});
  addresses.hasMany(stations, { as: "stations", foreignKey: "address_id"});
  packages.belongsTo(cods, { as: "cod", foreignKey: "cod_id"});
  cods.hasMany(packages, { as: "packages", foreignKey: "cod_id"});
  packages.belongsTo(customers, { as: "customer", foreignKey: "customer_id"});
  customers.hasMany(packages, { as: "packages", foreignKey: "customer_id"});
  packages.belongsTo(shops, { as: "shop", foreignKey: "shop_id"});
  shops.hasMany(packages, { as: "packages", foreignKey: "shop_id"});
  cods.belongsTo(stations, { as: "station", foreignKey: "station_id"});
  stations.hasMany(cods, { as: "cods", foreignKey: "station_id"});
  packages.belongsTo(stations, { as: "current_station", foreignKey: "current_station_id"});
  stations.hasMany(packages, { as: "packages", foreignKey: "current_station_id"});

  return {
    Address: addresses,
    Cod: cods,
    Customer: customers,
    Package: packages,
    Shop: shops,
    Station: stations,
  };
}
module.exports = initModels;
module.exports.initModels = initModels;
module.exports.default = initModels;
