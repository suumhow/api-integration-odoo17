from odoo import http, fields, api
from odoo.http import request
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
  _inherit = 'res.partner'

  x_catch_up_id = fields.Char(string='Catch Up ID', readonly=True)
  x_catch_up_url = fields.Char(string='Catch Up Url', readonly=True)

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

  def send_to_catch_up(self):
      _logger.info(f"send_to_catch_up called for ResPartner ID: {self.id}")
      url = "https://preprod.hike-up.be/api/odoo/contact/hikeup"

      partners = self.env['res.partner'].sudo().search([('is_company', '=', True)])

      data = {
          'id': self.id,
          'x_catch_up_id': self.x_catch_up_id,
          'name': self.name,
          'email': self.email,
          'phone': self.phone,
          'mobile': self.mobile,
          'function': self.function,
          'company_id': self.company_id.id if self.company_id else None,
          'company_name': self.company_id.name if self.company_id else None,
          'create_date': str(self.create_date) if self.create_date else None,
          'write_date': str(self.write_date) if self.write_date else None,
      }
      try:
          _logger.info(f"Sending data to API for ResPartner ID: {self.id}")
          response = requests.post(url, json=data, timeout=10)
          _logger.info(f"API response status code: {response.status_code}")
          response.raise_for_status()
          response_data = response.json()
          _logger.info(f"API response data: {response_data}")
          if 'id' in response_data:
              self.x_catch_up_id = response_data['id']
              _logger.info(f"Updated x_catch_up_id to {response_data['id']} for ResPartner ID: {self.id}")
          _logger.info(f"Successfully sent data for ID {self.id}")
      except requests.exceptions.RequestException as e:
          _logger.error(f"Failed to send data for ID {self.id}: {e}")
      except json.JSONDecodeError:
          _logger.error(f"Failed to parse response from API for ID {self.id}")
      except Exception as e:
          _logger.error(f"Unexpected error in send_to_catch_up for ID {self.id}: {str(e)}")




#       _logger.info(f"_send_opportunity_data called for CrmLead ID: {self.id}")
#       url = "https://preprod.hike-up.be/api/odoo/opportunity/hikeup"
#       data = self._prepare_opportunity_data()
#       try:
#           _logger.info(f"Sending data to API for CrmLead ID: {self.id}")
#           response = requests.post(url, json=data, timeout=10)
#           _logger.info(f"API response status code: {response.status_code}")
#           response.raise_for_status()
#           response_data = response.json()
#           _logger.info(f"API response data: {response_data}")
#           if 'id' in response_data:
#               self.x_catch_up_id = response_data['id']
#               _logger.info(f"Updated x_catch_up_id to {response_data['id']} for CrmLead ID: {self.id}")
#           _logger.info(f"Successfully sent opportunity data for ID {self.id}")
#       except requests.exceptions.RequestException as e:
#           _logger.error(f"Failed to send opportunity data for ID {self.id}: {e}")
#       except json.JSONDecodeError:
#           _logger.error(f"Failed to parse response from API for opportunity ID {self.id}")
#       except Exception as e:
#           _logger.error(f"Unexpected error in _send_opportunity_data for ID {self.id}: {str(e)}")

  @api.model
  def create(self, vals):
      record = super(ResPartner, self).create(vals)
      _logger.info(f"CrmLead create method called with vals: {vals}")
      try:
          _logger.info(f"Created CrmLead record with ID: {record.id}")
          record._send_opportunity_data()
          return record
      except Exception as e:
          _logger.error(f"Error in CrmLead create method: {str(e)}")
          raise

  def write(self, vals):
      _logger.info(f"CrmLead write method called for ID: {self.id} with vals: {vals}")
      try:
          result = super(CrmLead, self).write(vals)
          _logger.info(f"Updated CrmLead record with ID: {self.id}")
          self._send_opportunity_data()
          return result
      except Exception as e:
          _logger.error(f"Error in CrmLead write method: {str(e)}")
          raise

  def unlink(self):
      _logger.info(f"CrmLead unlink method called for IDs: {self.ids}")
      for record in self:
          if record.x_catch_up_id:
              url = f"https://preprod.hike-up.be/api/odoo/opportunity/hikeup/{record.x_catch_up_id}"
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