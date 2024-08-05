from odoo import http, fields as odoo_fields, api
from odoo.http import request
import json
from datetime import date, datetime
import traceback    
import logging

_logger = logging.getLogger(__name__)

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
        
          
          companies = request.env['res.partner'].sudo().search([('is_company', '=', True)])
          partner_model = request.env['ir.model'].sudo().search([('name', '=', 'res.partner')])

          partner_fields = request.env['ir.model.fields'].sudo().search([('model_id', '=', partner_model.id)])
          _logger.info(f"partner_fields: {partner_fields}")
          
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