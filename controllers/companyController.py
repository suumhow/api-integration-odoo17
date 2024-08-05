from odoo import http, fields as odoo_fields, api
from odoo.http import request
import json
from datetime import date, datetime
import traceback

class CompanyController(http.Controller):
  def _json_serialize(self, value):
      if isinstance(value, (datetime, date)):
          return value.isoformat()
      if isinstance(value, odoo_fields.BaseModel):
          return value.id
      return value

  @http.route('/api/companies', type='http', auth='public', methods=['GET'], csrf=False)
  def get_companies(self):
      try:
          # Force reload of ir.model.fields
          request.env['ir.model.fields'].clear_caches()
          request.env['res.partner'].clear_caches()
          
          # Reload the model
          request.env.cr.execute("SELECT * FROM ir_model_fields WHERE model = 'res.partner' AND name IN ('x_catch_up_id', 'x_catch_up_url')")
          new_fields = request.env.cr.fetchall()
          if new_fields:
              request.env['res.partner']._add_field('x_catch_up_id', odoo_fields.Char(string='CU ID'))
              request.env['res.partner']._add_field('x_catch_up_url', odoo_fields.Char(string='CU URL'))
              request.env['res.partner']._setup_complete()

          companies = request.env['res.partner'].sudo().search([('is_company', '=', True)])
          partner_fields = request.env['res.partner'].sudo().fields_get()
          
          blacklist = [
              'image_1920', 'image_1024', 'image_512', 'image_256', 'image_128',
              'avatar_1920', 'avatar_1024', 'avatar_512', 'avatar_256', 'avatar_128',
          ]
          
          data = []
          for company in companies:
              company_data = {}
              for field in partner_fields:
                  if field not in blacklist:
                      try:
                          value = company[field]
                          company_data[field] = self._json_serialize(value)
                      except Exception as e:
                          company_data[field] = str(e)
              
              # Explicitly check for new fields
              for new_field in ['x_catch_up_id', 'x_catch_up_url']:
                  if new_field in company:
                      company_data[new_field] = self._json_serialize(company[new_field])
                  else:
                      company_data[new_field] = "Field not found in model"
              
              data.append(company_data)
          
          return http.Response(json.dumps(data), content_type='application/json')
      except Exception as e:
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)
  
  @http.route('/api/companies', type='json', auth='public', methods=['POST'], csrf=False)
  def create_company(self):
      data = json.loads(request.httprequest.data)
      data['is_company'] = True
      new_company = request.env['res.partner'].sudo().create(data)
      return {'id': new_company.id, 'name': new_company.name}

  @http.route('/api/companies/<int:company_id>', type='json', auth='public', methods=['PUT'], csrf=False)
  def update_company(self, company_id):
      data = json.loads(request.httprequest.data)
      company = request.env['res.partner'].sudo().browse(company_id)
      if not company.exists() or not company.is_company:
          return {'error': 'Company not found'}, 404
      company.write(data)
      return {'id': company.id, 'name': company.name}