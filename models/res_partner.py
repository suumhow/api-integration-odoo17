from odoo import models, fields, api
from datetime import date, datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
  _inherit = 'res.partner'

  x_catch_up_id = fields.Char(string='Catch Up ID', readonly=True)
  x_catch_up_url = fields.Html(string='Catch Up Url', readonly=True)

  def _json_serialize(self, value):
      if isinstance(value, (datetime, date)):
          return value.isoformat()
      if isinstance(value, models.BaseModel):
          return value.id
      return value

  def _send_partner_data(self, forceUpdateCU=False):
    #   return
      _logger.info(f"_send_partner_data called for ResPartner ID: {self.id}")
    #   cu_schema_param = self.env["ir.config_parameter"].get_param("cu_schema_params", False)
      url = "https://preprod.hike-up.be/api/odoo/partner/hikeup"

      # Standard fields we want to include
      standard_fields = [
            'id', 'name', 'email', 'phone', 'mobile', 'street', 'city', 'zip', 'country_id',
            'company_type','is_company','website', 'parent_id', 'type', 'user_id', 'vat', 'lang', 'active'
            # Add any other standard fields you want to include
        ]

        # Get all custom fields
      custom_fields = self.env['ir.model.fields'].search([
      ('model', '=', 'res.partner'),
      ('name', 'like', 'x_%')  # Custom fields typically start with 'x_'
      ]).mapped('name')

      # Combine standard and custom fields
      fields_to_read = standard_fields + custom_fields

      data = {'id': self.id}
      for field in fields_to_read:
          
              try:
                  value = self[field]
                  data[field] = self._json_serialize(value)
              except Exception as e:
                  _logger.warning(f"Error serializing field {field}: {str(e)}")
                  data[field] = str(value) if value else None
      _logger.info(f"resetCU: {forceUpdateCU}")
      if forceUpdateCU:
        data['forceUpdateCu'] = True

      try:
          _logger.info(f"Data to send to API: {data}")

          _logger.info(f"Sending data to API for ResPartner ID: {self.id}")
          response = requests.post(url, json=data, timeout=10)
          _logger.info(f"API response status code: {response.status_code}")
          response.raise_for_status()
          response_data = response.json()
          _logger.info(f"API response data: {response_data}")
          _logger.info(f"self data id: {self.x_catch_up_id}")
          _logger.info(f"self data url: {self.x_catch_up_url}")

          if 'id' in response_data:
              if self.x_catch_up_id != response_data['id']:
                  self.with_context(skip_send_partner_data=True).write({'x_catch_up_id': response_data['id']})
          if 'url' in response_data:
              if self.x_catch_up_url != response_data['url']:
                url2 = response_data['url']
                url = f'<a href="{url2}">Catch Up</a>'
                
                self.with_context(skip_send_partner_data=True).write({'x_catch_up_url': url})
         
          
      except Exception as e:
          _logger.error(f"Error in _send_partner_data: {str(e)}")

  @api.model
  def get_all_companies(self):
      companies = self.search([('is_company', '=', True)])
      return self._get_partner_data(companies)

  @api.model
  def get_all_contacts(self):
      contacts = self.search([('is_company', '=', False)])
      return self._get_partner_data(contacts)

  def _get_partner_data(self, partners):
      # Standard fields we want to include
      standard_fields = [
            'id', 'name', 'email', 'phone', 'mobile', 'street', 'city', 'zip', 'country_id',
            'company_type','is_company','website', 'parent_id', 'type', 'user_id', 'vat', 'lang', 'active'
            # Add any other standard fields you want to include
        ]

        # Get all custom fields
      custom_fields = self.env['ir.model.fields'].search([
      ('model', '=', 'res.partner'),
      ('name', 'like', 'x_%')  # Custom fields typically start with 'x_'
      ]).mapped('name')

      # Combine standard and custom fields
      fields_to_read = standard_fields + custom_fields

      data = []
      for partner in partners:
          partner_data = {}
          for field in fields_to_read:
              try:
                  value = partner[field]
                  partner_data[field] = self._json_serialize(value)
              except Exception as e:
                  partner_data[field] = str(e)
          data.append(partner_data)
      
      return data

  @api.model
  def create_company_cu(self, data):
      data['is_company'] = True
      return self.create_partner(data)

  @api.model
  def create_contact(self, data):
      data['is_company'] = False
      return self.create_partner(data)

  @api.model
  def create_partner(self, data):
      new_partner = self.create(data)
      return {'id': new_partner.id, 'name': new_partner.name}

  def update_company(self, data):
      return self.update_partner(data, is_company=True)

  def update_contact(self, data):
      return self.update_partner(data, is_company=False)

  def update_partner(self, data, is_company):
      if not self.exists() or self.is_company != is_company:
          return {'error': 'Partner not found'}, 404
      self.with_context(skip_send_partner_data=True).write(data)
      return {'id': self.id, 'name': self.name}
  @api.model
  def mass_update_partners(self, data):
      _logger.info(f"Mass update partners called with data: {data}")
      
      if not isinstance(data, list):
          return {'error': 'Expected a list of partner updates'}
      
      updated_count = 0
      errors = []

      for partner_data in data:
          partner_id = partner_data.get('id')
          update_values = {k: v for k, v in partner_data.items() if k != 'id'}
          url = update_values.get('x_catch_up_url')
          update_values['x_catch_up_url'] = f'<a href="{url}">Catch Up</a>'
          
          if not partner_id or not update_values:
              errors.append(f"Invalid data for partner: {partner_data}")
              continue
          
          try:
              partner = self.browse(partner_id)
              if partner.exists():
                  partner.with_context(skip_send_partner_data=True).write(update_values)
                  updated_count += 1
                  _logger.info(f"Updated partner ID {partner_id} with values: {update_values}")
              else:
                  errors.append(f"Partner with ID {partner_id} not found")
          except Exception as e:
              error_msg = f"Error updating partner ID {partner_id}: {str(e)}"
              _logger.error(error_msg)
              errors.append(error_msg)

      result = {
          'success': updated_count > 0,
          'message': f'Updated {updated_count} partner records',
          'updated_count': updated_count,
      }
      if errors:
          result['errors'] = errors

      return result

  @api.model
  def create(self, vals):
      if self.env.context.get('skip_send_partner_data') or self.env.context.get('import_file'):
          return super(ResPartner, self).create(vals)
      record = super(ResPartner, self).create(vals)
      _logger.info(f"ResPartner create method called with vals: {vals}")
      record._send_partner_data(True)
      return record

  def write(self, vals):
      
      _logger.info(f"self: {self.env.context.get('skip_send_partner_data')}")
      if self.env.context.get('skip_send_partner_data') or self.env.context.get('import_file'):
          _logger.info(f"Skipping send_partner_data with skip_send_partner_data context")
          return super(ResPartner, self).write(vals)
      
      result = super(ResPartner, self).write(vals)
      _logger.info(f"ResPartner write method called for ID: {self.id} with vals: {vals}")
      _logger.info(f"111111111111111111111111: {vals.get('is_company')}")
      _logger.info(f"222222222222222222222: {self.is_company}")
    #   if self.is_company :
    #       _logger.info(f"Skipping send_partner_data with x_catch_up_id because is_company field changed")
    #       self._send_partner_data(True)
    #   else:
    #       self._send_partner_data()
      self._send_partner_data()
      return result
    