from odoo import models, fields, api
from datetime import date, datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
  _inherit = 'res.users'

  x_catch_up_id = fields.Char(string='Catch Up ID', readonly=True)

  def _json_serialize(self, value):
      if isinstance(value, (datetime, date)):
          return value.isoformat()
      if isinstance(value, models.BaseModel):
          return value.id
      return value

  def _send_user_data(self):
      _logger.info(f"_send_partner_data called for ResUsers ID: {self.id}")
      cu_schema_param = self.env["ir.config_parameter"].get_param("cu_schema_params", False)
      url = "https://preprod.hike-up.be/api/odoo/user/" + cu_schema_param

      # Get all fields of the model
      all_fields = self.fields_get().keys()

      # Fields to exclude
      exclude_fields = [
          'image_1920', 'image_1024', 'image_512', 'image_256', 'image_128',
          'avatar_1920', 'avatar_1024', 'avatar_512', 'avatar_256', 'avatar_128',
          'parent_id', 'child_ids', 'user_ids', 'message_ids', 'message_follower_ids',
          'activity_ids', 'message_partner_ids', 'email_normalized', 'signup_token',
          'signup_type', 'signup_expiration', 'signup_valid', 'calendar_last_notif_ack'
      ]

      data = {'id': self.id}
      for field in all_fields:
          if field not in exclude_fields:
              try:
                  value = self[field]
                  data[field] = self._json_serialize(value)
              except Exception as e:
                  _logger.warning(f"Error serializing field {field}: {str(e)}")
                  data[field] = str(value) if value else None

      try:
          _logger.info(f"Sending data to API for ResUsers ID: {self.id}")
          response = requests.post(url, json=data, timeout=10)
          _logger.info(f"API response status code: {response.status_code}")
          response.raise_for_status()
          response_data = response.json()
          _logger.info(f"API response data: {response_data}")
          if 'id' in response_data:
              self.x_catch_up_id = response_data['id']
      except Exception as e:
          _logger.error(f"Error in _send_user_data: {str(e)}")

  @api.model
  def get_all_users(self):
        users = self.search([])
        return self._get_user_data(users)


  def _get_user_data(self, partners):
      blacklist = [
          'image_1920', 'image_1024', 'image_512', 'image_256', 'image_128',
          'avatar_1920', 'avatar_1024', 'avatar_512', 'avatar_256', 'avatar_128',
          'parent_id', 'child_ids', 'user_ids', 'message_ids', 'message_follower_ids',
          'activity_ids', 'message_partner_ids', 'email_normalized', 'signup_token',
          'signup_type', 'signup_expiration', 'signup_valid', 'calendar_last_notif_ack'
      ]
      
      fields_to_read = [field.name for field in self.env['ir.model.fields'].search([
          ('model', '=', 'res.users'),
          ('name', 'not in', blacklist)
      ])]

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
  def create_user(self, data):
      new_user = self.create(data)
      return {'id': new_user.id, 'name': new_user.name}



  def update_user(self, data):
      if not self.exists() :
          return {'error': 'Partner not found'}, 404
      self.write(data)
      return {'id': self.id, 'name': self.name}

  @api.model
  def create(self, vals):
      record = super(ResUsers, self).create(vals)
      _logger.info(f"ResUsers create method called with vals: {vals}")
      record._send_user_data()
      return record

  def write(self, vals):
      _logger.info(f"ResUsers write method called for ID: {self.id} with vals: {vals}")
      result = super(ResUsers, self).write(vals)
      self._send_user_data()
      return result