from odoo import http
from odoo.http import request
import json

class UserController(http.Controller):

  @http.route('/api/users', type='http', auth='public', methods=['GET'], csrf=False)
  def get_users(self):
      users = request.env['res.users'].sudo().search([])
      data = [{
          'id': user.id,
          'name': user.name,
          'login': user.login,
          'email': user.email,
      } for user in users]
      return http.Response(json.dumps(data), content_type='application/json')

  @http.route('/api/users', type='json', auth='public', methods=['POST'], csrf=False)
  def create_user(self):
      data = json.loads(request.httprequest.data)
      new_user = request.env['res.users'].sudo().create(data)
      return {'id': new_user.id, 'name': new_user.name}

  @http.route('/api/users/<int:user_id>', type='json', auth='public', methods=['PUT'], csrf=False)
  def update_user(self, user_id):
      data = json.loads(request.httprequest.data)
      user = request.env['res.users'].sudo().browse(user_id)
      if not user.exists():
          return {'error': 'User not found'}, 404
      user.write(data)
      return {'id': user.id, 'name': user.name}