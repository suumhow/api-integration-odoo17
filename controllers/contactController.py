from odoo import http
from odoo.http import request
import json
from datetime import date, datetime

class ContactController(http.Controller):

  def _json_serialize(self, value):
      if isinstance(value, (date, datetime)):
          return value.isoformat()
      if hasattr(value, 'id'):
          return value.id
      return str(value)

  @http.route('/api/contacts', type='http', auth='public', methods=['GET'], csrf=False)
  def get_contacts(self):
      contacts = request.env['res.partner'].sudo().search([('is_company', '=', False)])
      fields = request.env['res.partner'].sudo().fields_get()
      
      blacklist = [
              'image_1920',
              'image_1024',
              'image_512',
            'image_256',
            'image_128',
            'avatar_1920',
            'avatar_1024',
            'avatar_512',
            'avatar_256',
            'avatar_128',

          ]
      data = []
      for contact in contacts:
          contact_data = {}
          for field in fields:
              if field not in blacklist:
                  try:
                      value = contact[field]
                      contact_data[field] = self._json_serialize(value)
                  except Exception as e:
                      contact_data[field] = str(e)
          data.append(contact_data)
      return http.Response(json.dumps(data), content_type='application/json')

  @http.route('/api/contacts', type='json', auth='public', methods=['POST'], csrf=False)
  def create_contact(self):
      data = json.loads(request.httprequest.data)
      new_contact = request.env['res.partner'].sudo().create(data)
      return {'id': new_contact.id, 'name': new_contact.name}

  @http.route('/api/contacts/<int:contact_id>', type='json', auth='public', methods=['PUT'], csrf=False)
  def update_contact(self, contact_id):
      data = json.loads(request.httprequest.data)
      contact = request.env['res.partner'].sudo().browse(contact_id)
      if not contact.exists():
          return {'error': 'Contact not found'}, 404
      contact.write(data)
      return {'id': contact.id, 'name': contact.name}