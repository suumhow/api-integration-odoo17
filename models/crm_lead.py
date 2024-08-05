from odoo import models, api
import requests
import json

class CrmLead(models.Model):
  _inherit = 'crm.lead'

  def _prepare_opportunity_data(self):
      return {
          'id': self.id,
          'name': self.name,
          'partner_id': self.partner_id.id,
          'email': self.email_from,
          'phone': self.phone,
          'stage_id': self.stage_id.id,
          'stage_name': self.stage_id.name,
          'expected_revenue': self.expected_revenue,
          'probability': self.probability,
          'date_deadline': str(self.date_deadline) if self.date_deadline else None,
          # Add more fields as needed
      }

  def _send_opportunity_data(self):
      url = "https://preprod.hike-up.be/api/opportunity"
      data = self._prepare_opportunity_data()
      try:
          response = requests.post(url, json=data, timeout=10)
          response.raise_for_status()
      except requests.exceptions.RequestException as e:
          # Log the error or handle it as needed
          _logger.error(f"Failed to send opportunity data: {e}")

  @api.model
  def create(self, vals):
      record = super(CrmLead, self).create(vals)
      record._send_opportunity_data()
      return record

  def write(self, vals):
      result = super(CrmLead, self).write(vals)
      self._send_opportunity_data()
      return result