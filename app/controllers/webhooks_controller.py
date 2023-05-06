from flask import Blueprint, request, jsonify

from services.package_service import PackageService

webhooks_routes = Blueprint('webhooks_routes', __name__)


@webhooks_routes.route('/ping', methods=['GET'])
def ping():
    return 'pong'


@webhooks_routes.route('/get-pkg', methods=['POST'])
def get_package():
    req_data = request.get_json() if request.get_json() else {}
    pkg_code = req_data['pkg_code'] if 'pkg_code' in req_data.keys() else None

    if not pkg_code:
        return jsonify({
            'success': False,
            'message': 'Không có dữ liệu đơn hàng.'
        })

    package_service = PackageService()
    return package_service.get_package(pkg_code)


@webhooks_routes.route('/get-pkgs', methods=['POST'])
def get_packages():
    req_data = request.get_json() if request.get_json() else {}
    shop_id = req_data['shop_id'] if 'shop_id' in req_data.keys() else None
    limit = req_data['limit'] if 'limit' in req_data.keys() else 10

    if not shop_id:
        return jsonify({
            'success': False,
            'message': 'Không có dữ liệu về cửa hàng.'
        })

    package_service = PackageService()
    return package_service.get_packages(shop_id, limit)


@webhooks_routes.route('/update-package', methods=['POST'])
def update_package():
    req_data = request.get_json() if request.get_json() else {}
    pkg_code = req_data['pkg_code'] if 'pkg_code' in req_data.keys() else None
    pkg_status_id = req_data['pkg_status_id'] if 'pkg_status_id' in req_data.keys() else None

    if not pkg_code or not pkg_status_id:
        return jsonify({
            'success': False,
            'message': 'Không có dữ liệu đơn hàng.'
        })

    package_service = PackageService()
    return package_service.update_package(pkg_code, pkg_status_id)


@webhooks_routes.route('/update-packages', methods=['POST'])
def update_packages():
    req_data = request.get_json() if request.get_json() else {}
    shop_id = req_data['shop_id'] if 'shop_id' in req_data.keys() else None
    pkg_status_id = req_data['pkg_status_id'] if 'pkg_status_id' in req_data.keys() else None

    if not shop_id or not pkg_status_id:
        return jsonify({
            'success': False,
            'message': 'Không có dữ liệu về cửa hàng.'
        })

    package_service = PackageService()
    return package_service.update_packages(shop_id, pkg_status_id)


@webhooks_routes.route('/update-random-packages', methods=['POST'])
def update_random_packages():
    package_service = PackageService()
    return package_service.update_random_packages()
