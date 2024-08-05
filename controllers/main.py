from odoo import http
from odoo.http import request
import json
import requests
from datetime import date, datetime


class APIController(http.Controller):
    pass

#   def _json_serialize(self, value):
#       if isinstance(value, (date, datetime)):
#           return value.isoformat()
#       if hasattr(value, 'id'):
#           return value.id
#       return str(value)

#   @http.route('/api/contacts', type='http', auth='public', methods=['GET'], csrf=False)
#   def get_all_contacts(self):
#       contacts = request.env['res.partner'].sudo().search([('is_company', '=', False)])
#       fields = request.env['res.partner'].sudo().fields_get()
#       blacklist = [
#           'image_1920',
#           'image_1024',
#           'image_512',
#         'image_256',
#         'image_128',
#         'avatar_1920',
#         'avatar_1024',
#         'avatar_512',
#         'avatar_256',
#         'avatar_128',

#       ]
#       data = []
#       for contact in contacts:
#           contact_data = {}
#           for field in fields:
#               if field not in blacklist:
#                 try:
#                     value = contact[field]
#                     contact_data[field] = self._json_serialize(value)
#                 except Exception as e:
#                     contact_data[field] = str(e)
#           data.append(contact_data)
#       return http.Response(json.dumps(data), content_type='application/json')

#   @http.route('/api/contacts/<int:contact_id>', type='http', auth='public', methods=['GET'], csrf=False)
#   def get_contact_by_id(self, contact_id):
#       contact = request.env['res.partner'].sudo().browse(contact_id)
#       if not contact.exists() or contact.is_company:
#           return http.Response(json.dumps({'error': 'Contact not found'}), status=404, content_type='application/json')
#       data = {
#           'id': contact.id,
#           'name': contact.name,
#           'email': contact.email,
#           'phone': contact.phone,
#       }
#       return http.Response(json.dumps(data), content_type='application/json')

#   @http.route('/api/companies', type='http', auth='public', methods=['GET'], csrf=False)
#   def get_all_companies(self):
#       companies = request.env['res.partner'].sudo().search([('is_company', '=', True)])
#       data = [{
#           'id': company.id,
#           'name': company.name,
#           'email': company.email,
#           'phone': company.phone,
#       } for company in companies]
#       return http.Response(json.dumps(data), content_type='application/json')

#   @http.route('/api/companies/<int:company_id>', type='http', auth='public', methods=['GET'], csrf=False)
#   def get_company_by_id(self, company_id):
#       company = request.env['res.partner'].sudo().browse(company_id)
#       if not company.exists() or not company.is_company:
#           return http.Response(json.dumps({'error': 'Company not found'}), status=404, content_type='application/json')
#       data = {
#           'id': company.id,
#           'name': company.name,
#           'email': company.email,
#           'phone': company.phone,
#       }
#       return http.Response(json.dumps(data), content_type='application/json')

#   @http.route('/api/opportunity_stages', type='http', auth='public', methods=['GET'], csrf=False)
#   def get_all_opportunity_stages(self):
#       stages = request.env['crm.stage'].sudo().search([])
#       data = [{
#           'id': stage.id,
#           'name': stage.name,
#       } for stage in stages]
#       return http.Response(json.dumps(data), content_type='application/json')

#   @http.route('/api/opportunities', type='http', auth='public', methods=['GET'], csrf=False)
#   def get_all_opportunities(self):
#       opportunities = request.env['crm.lead'].sudo().search([])
#       data = [{
#           'id': opp.id,
#           'name': opp.name,
#           'partner_id': opp.partner_id.id,
#           'stage_id': opp.stage_id.id,
#           'expected_revenue': opp.expected_revenue,
#       } for opp in opportunities]
#       return http.Response(json.dumps(data), content_type='application/json')

#   @http.route('/api/users', type='http', auth='public', methods=['GET'], csrf=False)
#   def get_all_users(self):
#       users = request.env['res.users'].sudo().search([])
#       data = [{
#           'id': user.id,
#           'name': user.name,
#           'login': user.login,
#           'email': user.email,
#       } for user in users]
#       return http.Response(json.dumps(data), content_type='application/json')

#   @http.route('/api/users/<int:user_id>', type='http', auth='public', methods=['GET'], csrf=False)
#   def get_user_by_id(self, user_id):
#       user = request.env['res.users'].sudo().browse(user_id)
#       if not user.exists():
#           return http.Response(json.dumps({'error': 'User not found'}), status=404, content_type='application/json')
#       data = {
#           'id': user.id,
#           'name': user.name,
#           'login': user.login,
#           'email': user.email,
#       }
#       return http.Response(json.dumps(data), content_type='application/json')

#   @http.route('/api/fields/<string:model>', type='http', auth='public', methods=['GET'], csrf=False)
#   def get_fields_definition(self, model):
#       allowed_models = ['res.partner', 'crm.lead', 'crm.stage', 'res.users']
#       if model not in allowed_models:
#           return http.Response(json.dumps({'error': 'Invalid model'}), status=400, content_type='application/json')
      
#       fields = request.env[model].sudo().fields_get()
#       return http.Response(json.dumps(fields), content_type='application/json')