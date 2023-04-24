import json

from models.base import session
from models.model import *

from flask import jsonify


class PackageService:
    def __init__(self, request_data=None):
        self.request_data = request_data

    def get_package(self, pkg_code):
        package = session.query(Packages).filter(Packages.code == pkg_code).first()

        return jsonify({
            'success': True,
            'message': f'Lấy thông tin đơn hàng {pkg_code} thành công.',
            'data': self.format_package(package)
        })

    def get_packages(self, shop_id, limit):
        packages = session.query(Packages).filter(Packages.shop_id == shop_id).limit(limit).all()

        pkgs = []
        for package in packages:
            pkgs.append(self.format_package(package))

        return jsonify({
            'success': True,
            'message': f'Lấy thông tin đơn hàng của shop {shop_id} thành công.',
            'data': pkgs
        })

    def update_package(self, pkg_code, pkg_status_id):
        updated = session.query(Packages).filter(Packages.code == pkg_code).update({'status': pkg_status_id})
        session.commit()
        session.flush()

        if updated:
            return jsonify({
                'success': True,
                'message': f'Cập nhật trạng thái đơn hàng thành {pkg_status_id} của đơn hàng {pkg_code} thành công.',
                'data': updated
            })
        else:
            return jsonify({
                'success': True,
                'message': f'Cập nhật trạng thái đơn hàng của đơn hàng {pkg_code} thất bại.',
                'data': updated
            })

    def update_packages(self, shop_id, pkg_status_id):
        updated = session.query(Packages).filter(Packages.shop_id == shop_id)\
            .update({'status': pkg_status_id})
        session.commit()
        session.flush()

        if updated:
            return jsonify({
                'success': True,
                'message': f'Cập nhật trạng thái đơn hàng thành {pkg_status_id} của cửa hàng {shop_id} thành công.',
                'data': updated
            })
        else:
            return jsonify({
                'success': True,
                'message': f'Cập nhật trạng thái đơn hàng của cửa hàng {shop_id} thất bại.',
                'data': updated
            })

    def format_package(self, pkg):
        if not isinstance(pkg, Packages):
            return None
        return {
            'id': pkg.id,
            'code': pkg.code,
            'shop_id': pkg.shop_id,
            'current_station_id': pkg.current_station_id,
            'customer_id': pkg.customer_id,
            'cod_id': pkg.cod_id,
            'status': pkg.status,
            'picked_at': pkg.picked_at,
            'delivered_at': pkg.delivered_at,
            'done_at': pkg.done_at,
            'audited_at': pkg.audited_at
        }
