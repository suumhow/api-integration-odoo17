from odoo import models, fields, api
from datetime import date, datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
  _inherit = 'crm.lead'

  x_catch_up_id = fields.Char(string='Catch Up ID', readonly=True)
  x_catch_up_url = fields.Html(string='Catch Up Url', readonly=True)

  def _json_serialize(self, value):
      if isinstance(value, (datetime, date)):
          return value.isoformat()
      if isinstance(value, models.BaseModel):
          return value.id
      return value
  
  def get_all_opportunities(self):
      opportunities = self.env['crm.lead'].search([('type', '=', 'opportunity')])    #   et all the active opportunities
    
      # Standard fields we want to include
      standard_fields = [
            'id', 'display_name', 'expected_revenue', 'partner_id', "priority",
    "probability",
    "prorated_revenue",
    "recurring_plan",
    "recurring_revenue",
    "date_deadline",
    "recurring_revenue_monthly","stage_id","user_id","active"
    
            # Add any other standard fields you want to include
        ]
 
      

        # Get all custom fields
      custom_fields = self.env['ir.model.fields'].search([
      ('model', '=', 'crm.lead'),
      ('name', 'like', 'x_%')  # Custom fields typically start with 'x_'
      ]).mapped('name')

      # Combine standard and custom fields
      fields_to_read = standard_fields + custom_fields
     

      data = []
      for opp in opportunities:
          opp_data = {}
          for field in fields_to_read:
              try:
                  value = opp[field]
                  opp_data[field] = self._json_serialize(value)
              except Exception as e:
                  opp_data[field] = str(e)
          data.append(opp_data)
      
      return data



  def _send_opportunity_data(self, resetCU=False):
    #   return
    
      if self.type != 'opportunity':
          return
      _logger.info(f"_send_opportunity_data called for CrmLead ID: {self.id}")
      cu_schema_param = self.env["ir.config_parameter"].get_param("cu_schema_params", False)
      url = "https://app.catch-up.be/api/odoo/opportunity/" + cu_schema_param

       # Standard fields we want to include
      standard_fields = [
            'id', 'display_name', 'expected_revenue', 'partner_id', "priority",
    "probability",
    "prorated_revenue",
    "recurring_plan",
    "recurring_revenue","date_deadline",
    "recurring_revenue_monthly","stage_id","user_id","active","type","lost_reason_id"
    
            # Add any other standard fields you want to include
        ]

        # Get all custom fields
      custom_fields = self.env['ir.model.fields'].search([
      ('model', '=', 'crm.lead'),
      ('name', 'like', 'x_%')  # Custom fields typically start with 'x_'
      ]).mapped('name')

      # Combine standard and custom fields
      fields_to_read = standard_fields + custom_fields

      data = {'id': self.id}
      for field in fields_to_read:
          
              try:
                  value = self[field]
                  data[field] = self._json_serialize(value)
                  if field == 'lost_reason_id':
                    # get the lost reason name from the id 
                    lost_reason = self.env['crm.lost.reason'].search([('id', '=', self._json_serialize(value))])
                    data['lost_reason_name'] = lost_reason.name
              except Exception as e:
                  _logger.warning(f"Error serializing field {field}: {str(e)}")
                  data[field] = str(value) if value else None
      _logger.info(f"resetCU: {resetCU}")
      if resetCU:
        data['x_catch_up_id'] = False
        data['x_catch_up_url'] = False   
        
    #   check if partner_id is a company, if company on passe le flag partner_company à true sinon à false

      try:
          _logger.info(f"Data to send to API: {data}")

          _logger.info(f"Sending data to API for CrmLead ID: {self.id}")
          response = requests.post(url, json=data, timeout=10)
          _logger.info(f"API response status code: {response.status_code}")
          response.raise_for_status()
          response_data = response.json()
          _logger.info(f"API response data: {response_data}")
          _logger.info(f"self data id: {self.x_catch_up_id}")
          _logger.info(f"self data url: {self.x_catch_up_url}")

          if 'id' in response_data:
              if self.x_catch_up_id != response_data['id']:
                  self.with_context(skip_send_opportuniy_data=True).write({'x_catch_up_id': response_data['id']})
          if 'url' in response_data:
              if self.x_catch_up_url != response_data['url']:
                url2 = response_data['url']
                url = f'<a href="{url2}">Catch Up</a>'
                
                self.with_context(skip_send_opportunity_data=True).write({'x_catch_up_url': url})
         
          
      except Exception as e:
          _logger.error(f"Error in _send_opportunity_data: {str(e)}")
          
  @api.model
  def create_opportunity_from_cu(self, data):
      _logger.info(f"create_opportunity_from_cu called with data: {data}")
      
      
    #    Create a new opportunity record with the provided data and return the ID of the new record
      try:
        opportunity = self.with_context(skip_send_opportunity_data=True).create(data)
        _logger.info(f"Created opportunity with ID: {opportunity.id}")
        return {'id': opportunity.id}
      except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        _logger.error(error_message)
        return {'error': error_message}
    
      
        


  @api.model
  def mass_update_opportunities(self, data):
      _logger.info(f"Mass update opportunities called with data: {data}")
      
      if not isinstance(data, list):
          return {'error': 'Expected a list of opportunities updates'}
      
      updated_count = 0
      errors = []

      for opportunity_data in data:
          opportunity_id = opportunity_data.get('id')
          update_values = {k: v for k, v in opportunity_data.items() if k != 'id'}
          
          if not opportunity_id or not update_values:
              errors.append(f"Invalid data for opportunity: {opportunity_data}")
              continue
          
          try:
              opportunity = self.browse(opportunity_id)
              if opportunity.exists():
                  opportunity.with_context(skip_send_opportunity_data=True).write(update_values)
                  updated_count += 1
                  _logger.info(f"Updated opportunity ID {opportunity_id} with values: {update_values}")
              else:
                  errors.append(f"Opportunity with ID {opportunity_id} not found")
          except Exception as e:
              error_msg = f"Error updating opportunity ID {opportunity_id}: {str(e)}"
              _logger.error(error_msg)
              errors.append(error_msg)

      result = {
          'success': updated_count > 0,
          'message': f'Updated {updated_count} opportunity records',
          'updated_count': updated_count,
      }
      if errors:
          result['errors'] = errors

      return result
  @api.model
  def create(self, vals):
      if self.env.context.get('skip_send_opportunity_data') or self.env.context.get('import_file'):
          return super(CrmLead, self).create(vals)
      record = super(CrmLead, self).create(vals)
      _logger.info(f"CrmLead create method called with vals: {vals}")
      record._send_opportunity_data()
      return record

  def write(self, vals):
      _logger.info(f"self: {self.env.context.get('skip_send_opportunity_data')}")
      if self.env.context.get('skip_send_opportunity_data') or self.env.context.get('import_file'):
          _logger.info(f"Skipping send_opportunity_data with skip_send_opportunity_data context")
          return super(CrmLead, self).write(vals)
      
      result = super(CrmLead, self).write(vals)
      _logger.info(f"CrmLead write method called for ID: {self.id} with vals: {vals}")
      

      self._send_opportunity_data()
      return result

  def unlink(self):
      cu_schema_param = self.env["ir.config_parameter"].get_param("cu_schema_params", False)
      _logger.info(f"CrmLead unlink method called for IDs: {self.ids}")
      for record in self:
          if record.x_catch_up_id:
              url = f"https://app.catch-up.be/api/odoo/opportunity/{cu_schema_param}/{record.x_catch_up_id}"
              try:
                  _logger.info(f"Sending delete request for CrmLead ID: {record.id}")
                  response = requests.delete(url, timeout=10)
                  _logger.info(f"Delete request response status code: {response.status_code}")
                  response.raise_for_status()
                  _logger.info(f"Successfully sent delete request for opportunity ID {record.id}")
              except requests.exceptions.RequestException as e:
                  _logger.error(f"Failed to send delete request for opportunity ID {record.id}: {e}")
              except Exception as e:
                  _logger.error(f"Unexpected error in unlink method for ID {record.id}: {str(e)}")
      return super(CrmLead, self).unlink()
  
