const initModels = require("../models/init-models");
const Sequelize = require('sequelize')
const op = Sequelize.Op;

const { Package } = initModels();

const statusAllowed = require("../constants");

const packageController = {
  getPackage: async (req, res) => {
    const { pkg_code } = req.query;

    if (!pkg_code) {
      return res.status(400).json({
        success: false,
        message: "Không có dữ liệu đơn hàng.",
      });
    }

    const package = await Package.findOne({ where: { code: pkg_code } });

    return res.status(200).json({
      success: true,
      message: `Lấy thông tin đơn hàng ${pkg_code} thành công.`,
      data: package,
    });
  },
  getPackages: async (req, res) => {
    let { shop_id, limit } = req.query;

    limit = limit ? limit : 10;

    if (!shop_id) {
      return res.status(400).json({
        success: false,
        message: "Không có dữ liệu về cửa hàng.",
      });
    }

    const packages = await Package.findAll({
      where: { shop_id },
      limit: limit,
    });

    return res.status(200).json({
      success: true,
      message: `Lấy thông tin đơn hàng của shop ${shop_id} thành công.`,
      data: packages,
    });
  },
  updatePackage: async (req, res) => {
    const { pkg_code, pkg_status_id } = req.body;

    if (!pkg_code || !pkg_status_id) {
      return res.status(400).json({
        success: false,
        message: "Không có dữ liệu đơn hàng.",
      });
    }

    if (!statusAllowed.includes(pkg_status_id)) {
      return res.status(400).json({
        success: false,
        message: `Trạng thái đơn hàng ${pkg_status_id} cần cập nhật không hợp lệ!`,
      });
    }

    const updated = await Package.update(
      { status: pkg_status_id },
      { where: { code: pkg_code } }
    );

    if (updated) {
      return res.status(200).json({
        success: true,
        message: `Cập nhật trạng thái đơn hàng thành ${pkg_status_id} của đơn hàng ${pkg_code} thành công.`,
        data: updated,
      });
    } else {
      return res.status(200).json({
        success: true,
        message: `Cập nhật trạng thái đơn hàng của đơn hàng ${pkg_code} thất bại.`,
        data: updated,
      });
    }
  },
  updatePackages: async (req, res) => {
    const { shop_id, pkg_status_id } = req.body;

    if (!pkg_status_id) {
      return res.status(400).json({
        success: false,
        message: "Không có dữ liệu về trạng thái cần cập nhật.",
      });
    }

    if (!statusAllowed.includes(pkg_status_id)) {
      return res.status(400).json({
        success: false,
        message: `Trạng thái đơn hàng ${pkg_status_id} cần cập nhật không hợp lệ!`,
      });
    }

    let updated;
    if (shop_id) {
      updated = await Package.update(
        { status: pkg_status_id },
        { where: { shop_id: shop_id } }
      );
    } else {
      updated = await Package.update(
        { status: pkg_status_id },
        {
          where: {
            code: {
              [op.not]: null,
            },
          },
        }
      );
    }

    if (updated) {
      const has_shop = ` của cửa hàng ${shop_id}`;
      return res.status(200).json({
        success: true,
        message: `Cập nhật trạng thái đơn hàng thành ${pkg_status_id}${
          shop_id ? has_shop : ""
        } thành công.`,
        data: updated,
      });
    } else {
      return res.status(200).json({
        success: true,
        message: `Cập nhật trạng thái đơn hàng của cửa hàng ${shop_id} thất bại.`,
        data: updated,
      });
    }
  },
  updateRandomPackages: async (req, res) => {
    let { limit } = req.query;
    limit = limit || 1000;
    const pkg_codes = await Package.findAll({
      atrributes: ["code", "status"],
      raw: true,
    });

    let cnt = 0;
    try {
      for (let i = 0; i < limit; i++) {
        const random_code =
          pkg_codes[Math.floor(Math.random() * pkg_codes.length)];
        const random_status =
          statusAllowed[Math.floor(Math.random() * statusAllowed.length)];

        const { code, status } = random_code;

        cnt++;

        if (status != random_status) {
          await Package.update({ status: random_status }, { where: { code } });
        }
      }

      return res.status(200).json({
        success: true,
        message: `Đã cập nhật trạng thái đơn hàng của ${cnt} đơn hàng bất kì.`,
        data: cnt,
      });
    } catch (err) {
      return res.status(500).json({ msg: err.message });
    }
  },
};

module.exports = packageController;
