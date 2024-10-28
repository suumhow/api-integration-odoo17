# controllers/partnerController.py

from odoo import http
from odoo.http import request
import json
import traceback
import logging
import random
from ..utils import require_api_key
# from faker import Faker


_logger = logging.getLogger(__name__)

class PartnerController(http.Controller):

  @http.route('/api/getAllCompanies', type='http', auth='public', methods=['GET'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def get_partners(self):
      try:
          data = request.env['res.partner'].sudo().get_all_companies()
          return http.Response(json.dumps(data), content_type='application/json')
      except Exception as e:
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)

  @http.route('/api/getAllContacts', type='http', auth='public', methods=['GET'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def get_contacts(self):
      try:
          data = request.env['res.partner'].sudo().get_all_contacts()
          return http.Response(json.dumps(data), content_type='application/json')
      except Exception as e:
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)

  @http.route('/api/createCompany', type='json', auth='public', methods=['POST'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def create_company_cu(self):
      try:
          data = json.loads(request.httprequest.data)
          result = request.env['res.partner'].sudo().create_company_cu(data)
          return http.Response(json.dumps(result), content_type='application/json', status=201)
      except Exception as e:
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)
      


  @http.route('/api/createContact', type='json', auth='public', methods=['POST'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def create_contact(self):
      try:
          data = json.loads(request.httprequest.data)
          result = request.env['res.partner'].sudo().create_contact(data)
          return http.Response(json.dumps(result), content_type='application/json', status=201)
      except Exception as e:
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)

  @http.route('/api/updatePartner/<int:partner_id>', type='json', auth='public', methods=['PUT'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def update_partner(self, partner_id):
      try:
          data = json.loads(request.httprequest.data)
          partner = request.env['res.partner'].sudo().browse(partner_id)
          result = partner.update_company(data) if partner.is_company else partner.update_contact(data)
          return http.Response(json.dumps(result), content_type='application/json')
      except Exception as e:
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)

  @http.route('/api/deletePartner/<int:partner_id>', type='http', auth='public', methods=['DELETE'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def delete_partner(self, partner_id):
      try:
          partner = request.env['res.partner'].sudo().browse(partner_id)
          if not partner.exists():
              return http.Response(json.dumps({'error': 'Partner not found'}), content_type='application/json', status=404)
          partner.unlink()
          return http.Response(json.dumps({'message': 'Partner deleted successfully'}), content_type='application/json')
      except Exception as e:
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)
      


  @http.route('/api/mass_update_partners', type='json', auth='public', methods=['POST'])
  @require_api_key  # This decorator will check for the API key
  def mass_update_partners(self, **post):
      _logger.info("mass_update_partners controller method called")
      try:
          data = json.loads(request.httprequest.data).get('data')
       
          _logger.info(f"Received data: {data}")
          
          if not isinstance(data, list):
              _logger.warning("Invalid data format: expected a list")
              return {'error': 'Expected a list of partner updates'}

          _logger.info("Calling res.partner.mass_update_partners")
          result = request.env['res.partner'].sudo().mass_update_partners(data)
          _logger.info(f"Result from mass_update_partners: {result}")
          
          return result
      except Exception as e:
          _logger.exception("Exception in mass_update_partners controller")
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return {'error': error_message}
      
  @http.route('/api/get_mappable_fields', type='http', auth='public', methods=['GET'], csrf=False)
  def get_mappable_fields(self):
    #   get the custom fields of type char and text not in blacklist fields
        blacklist = ['x_catch_up_id', 'x_catch_up_url'] # fields to exclude
        custom_fields = request.env['ir.model.fields'].sudo().search([
            ('model', '=', 'res.partner'),
            ('name', 'like', 'x_%'),  # Custom fields typically start with 'x_'
            ('state', '=', 'manual'),
            # ('ttype', 'in', ['char', 'text','b'])
        ])
        data = []
        for field in custom_fields:
            if field.name not in blacklist:
                data.append({'name': field.name, 'type': field.ttype, 'label': field.field_description, 'required': field.required, 'readonly': field.readonly, 'help': field.help})
            
        return http.Response(json.dumps(data), content_type='application/json')
 
    
        
        
        
      
  @http.route('/api/add_partners', type='http', auth='public', methods=['GET'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def add_partners(self):
      try:
    

          # Create 10 companies
          companies = []
          for i in range(10):
              company = request.env['res.partner'].sudo().create({
                  'name': 'company_batch_4' + str(i),  
                  'is_company': True,
                  'email': 'email_' + str(i) + '@example4.com',
                  'phone': '555' + str(i).zfill(7),
                  'street': 'la belle rue',
                  'city': 'Paris',
                  'zip': '75001',
              })
              companies.append(company.id)
          _logger.info("100 companies have been created.")

          # Create 10 contacts, each linked to a random company
          for i in range(10):
              request.env['res.partner'].sudo().create({
                  'name': 'contact_batch_4' + str(i),  
                  'is_company': False,
                  'email': 'email_' + str(i) + '@example4.com',
                  'phone': '555' + str(i).zfill(7),
                  'street': 'la belle rue',
                  'city': 'Paris',
                  'zip': '75001',
                  'parent_id': random.choice(companies),
              })
          _logger.info("100 contacts have been created and linked to companies.")

        #   reset the field 'x_catch_up_id' for each partners that have it set
          partners = request.env['res.partner'].sudo().search([])
          _logger.info(f"Resetting field 'x_catch_up_id' for {len(partners)} partners records.")
          for partner in partners:
              partner.x_catch_up_id = False
              partner.user_id = False
              partner.x_catch_up_url = False
              
          opportunities = request.env['crm.lead'].sudo().search([])
          for opportunity in opportunities:
              opportunity.x_catch_up_id = False
              opportunity.x_catch_up_url = False

          
          
          _logger.info("Field 'x_catch_up_id' has been reset for all partners records.")

          return http.Response("Data reset and creation completed successfully.", content_type='text/plain')

      except Exception as e:
          _logger.error(f"An error occurred: {str(e)}")
          return http.Response(f"An error occurred: {str(e)}", content_type='text/plain', status=500)
      