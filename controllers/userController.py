from odoo import http
from odoo.http import request
import json
import traceback
import logging
from ..utils import require_api_key
 

_logger = logging.getLogger(__name__)


class UserController(http.Controller):
  


  @http.route('/api/getAllUsers', type='http', auth='public', methods=['GET'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def get_all_users(self):
      try:
          data = request.env['res.users'].sudo().get_all_users()
          return http.Response(json.dumps(data), content_type='application/json')
      except Exception as e:
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)

  @http.route('/api/createUser', type='json', auth='public', methods=['POST'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def create_user(self):
      data = json.loads(request.httprequest.data)
      new_user = request.env['res.users'].sudo().create(data)
      return {'id': new_user.id, 'name': new_user.name}

  @http.route('/api/updateUser/<int:user_id>', type='json', auth='public', methods=['PUT'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def update_user(self, user_id):
      data = json.loads(request.httprequest.data)
      user = request.env['res.users'].sudo().browse(user_id)
      if not user.exists():
          return {'error': 'User not found'}, 404
      user.write(data)
      return {'id': user.id, 'name': user.name}