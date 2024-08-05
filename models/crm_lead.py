
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
  _inherit = 'crm.lead'

  x_catch_up_id = fields.Char(string='Catch Up ID', readonly=True)
  x_catch_up_url = fields.Char(string='Catch Up Url', readonly=True)



  def _prepare_opportunity_data(self):
      _logger.info(f"Preparing opportunity data for CrmLead ID: {self.id}")
      data = {
          'id': self.id,
          'x_catch_up_id': self.x_catch_up_id,
          'name': self.name,
          'partner_id': self.partner_id.id if self.partner_id else None,
          'partner_name': self.partner_id.name if self.partner_id else None,
          'email': self.email_from,
          'phone': self.phone,
          'stage_id': self.stage_id.id,
          'stage_name': self.stage_id.name,
          'expected_revenue': self.expected_revenue,
          'probability': self.probability,
          'date_deadline': str(self.date_deadline) if self.date_deadline else None,
          'description': self.description,
          'user_id': self.user_id.id if self.user_id else None,
          'user_name': self.user_id.name if self.user_id else None,
          'team_id': self.team_id.id if self.team_id else None,
          'team_name': self.team_id.name if self.team_id else None,
          'company_id': self.company_id.id if self.company_id else None,
          'company_name': self.company_id.name if self.company_id else None,
          'priority': self.priority,
          'tag_ids': [tag.id for tag in self.tag_ids],
          'tag_names': [tag.name for tag in self.tag_ids],
          'create_date': str(self.create_date) if self.create_date else None,
          'write_date': str(self.write_date) if self.write_date else None,
      }
      _logger.info(f"Prepared opportunity data: {data}")
      return data

  def _send_opportunity_data(self):
      _logger.info(f"_send_opportunity_data called for CrmLead ID: {self.id}")
      url = "https://preprod.hike-up.be/api/odoo/opportunity/hikeup"
      data = self._prepare_opportunity_data()
      try:
          _logger.info(f"Sending data to API for CrmLead ID: {self.id}")
          response = requests.post(url, json=data, timeout=10)
          _logger.info(f"API response status code: {response.status_code}")
          response.raise_for_status()
          response_data = response.json()
          _logger.info(f"API response data: {response_data}")
          if 'id' in response_data:
              self.x_catch_up_id = response_data['id']
              _logger.info(f"Updated x_catch_up_id to {response_data['id']} for CrmLead ID: {self.id}")
          _logger.info(f"Successfully sent opportunity data for ID {self.id}")
      except requests.exceptions.RequestException as e:
          _logger.error(f"Failed to send opportunity data for ID {self.id}: {e}")
      except json.JSONDecodeError:
          _logger.error(f"Failed to parse response from API for opportunity ID {self.id}")
      except Exception as e:
          _logger.error(f"Unexpected error in _send_opportunity_data for ID {self.id}: {str(e)}")

  @api.model
  def create(self, vals):
      _logger.info(f"CrmLead create method called with vals: {vals}")
      try:
          record = super(CrmLead, self).create(vals)
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