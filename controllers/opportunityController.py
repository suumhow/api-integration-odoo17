from odoo import http, models, fields
from odoo.http import request
import json
import requests
import logging
from datetime import datetime, date
from ..utils import require_api_key



_logger = logging.getLogger(__name__)


class OpportunityController(http.Controller):
  
  def _json_serialize(self, value):
      if isinstance(value, (datetime, date)):
          return value.isoformat()
      if isinstance(value, models.BaseModel):
          return value.id
      return value
  
  

  @http.route('/api/getAllOpportunities', type='http', auth='public', methods=['GET'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def get_opportunities(self):
      try:
          data = request.env['crm.lead'].sudo().get_all_opportunities()
          return http.Response(json.dumps(data), content_type='application/json')
      except Exception as e:
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)
      

  @http.route('/api/opportunities', type='json', auth='public', methods=['POST'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def create_opportunity(self):
      try:
          data = json.loads(request.httprequest.data)
          result = request.env['crm.lead'].sudo().createOpportunity(data)
          return http.Response(json.dumps(result), content_type='application/json', status=201)
      except Exception as e:
        error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        return http.Response(json.dumps({'error': error_message}), content_type='application/json', status=500)
    

  

  @http.route('/api/opportunity_stages', type='http', auth='public', methods=['GET'], csrf=False)
  @require_api_key  # This decorator will check for the API key
  def get_opportunity_stages(self):
      stages = request.env['crm.stage'].sudo().search([])
      fields = request.env['crm.stage'].sudo().fields_get()
      blacklist = [
        ]
      data = []
      for stage in stages:
            stage_data = {}
            for field in fields:
                if field not in blacklist:
                    try:
                        value = stage[field]
                        stage_data[field] = self._json_serialize(value)
                    except Exception as e:
                        stage_data[field] = str(e)
            data.append(stage_data)
      

      
      return http.Response(json.dumps(data), content_type='application/json')
  
  @http.route('/api/mass_update_opportunities', type='json', auth='public', methods=['POST'])
  @require_api_key  # This decorator will check for the API key
  def mass_update_opportunities(self, **post):
      _logger.info("mass_update_opportunities controller method called")
      try:
          data = json.loads(request.httprequest.data).get('data')
       
          _logger.info(f"Received data: {data}")
          
          if not isinstance(data, list):
              _logger.warning("Invalid data format: expected a list")
              return {'error': 'Expected a list of opportunity updates'}

          _logger.info("Calling crm.lead.mass_update_opportunities")
          result = request.env['crm.lead'].sudo().mass_update_opportunities(data)
          _logger.info(f"Result from mass_update_opportunities: {result}")
          
          return result
      except Exception as e:
          _logger.exception("Exception in mass_update_opportunities controller")
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return {'error': error_message}
      
  @http.route('/api/create_opportunity_from_cu', type='json', auth='public', methods=['POST'])
  @require_api_key  # This decorator will check for the API key
  def create_opportunity_from_cu(self, **post):
      _logger.info("create_opportunity_from_cu controller method called")
      try:
          data = json.loads(request.httprequest.data).get('data')
       
          _logger.info(f"Received data 444444444444444444444444444444444444444: {data}")
          
          

          
          
          if data['companyData'] and 'partner_id' not in data['companyData']:
            # create company
            company = request.env['res.partner'].sudo().create_company_cu(data['companyData'])
            _logger.info(f"Created company with ID: {company['id']}")
            data['opportunityData']['partner_id'] = company['id']
            
        #   if data['companyData'] and 'parent_id' in data['companyData']:
           
        #     data['opportunityData']['partner_id'] = company['id']
            
          if data['contactData'] and 'partner_id' not in data['contactData']:
            # create contact
            data['contactData']['parent_id'] = company['id']
            contact = request.env['res.partner'].sudo().create_contact(data['contactData'])
            _logger.info(f"Created contact with ID: {contact['id']}")
            data['opportunityData']['partner_id'] = contact['id']
            
            
          _logger.info("Calling crm.lead.create_opportunity_from_cu")  
          result = request.env['crm.lead'].sudo().create_opportunity_from_cu(data['opportunityData'])
          _logger.info(f"Result from create_opportunity_from_cu: {result}")
          
          return result
      except Exception as e:
          _logger.exception("Exception in create_opportunity_from_cu controller")
          error_message = f"An error occurred: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
          return {'error': error_message}