# utils.py
from odoo.http import request, Response
import json

def require_api_key(func):
  def wrapper(*args, **kwargs):
      api_key = request.httprequest.headers.get('X-API-KEY')
      if not api_key or not validate_api_key(api_key):
          return Response(
              json.dumps({'error': 'Unauthorized'}),
              status=401,
              mimetype='application/json'
          )
      return func(*args, **kwargs)
  return wrapper

def validate_api_key(api_key):
  expected_api_key = request.env['ir.config_parameter'].sudo().get_param('api_key')
  return api_key == expected_api_key