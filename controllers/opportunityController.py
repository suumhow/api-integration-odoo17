from odoo import http
from odoo.http import request
import json
import requests

class OpportunityController(http.Controller):

  @http.route('/api/opportunities', type='http', auth='public', methods=['GET'], csrf=False)
  def get_opportunities(self):
      opportunities = request.env['crm.lead'].sudo().search([])
      data = [{
          'id': opp.id,
          'name': opp.name,
          'partner_id': opp.partner_id.id,
          'email': opp.email_from,
          'phone': opp.phone,
          'stage_id': opp.stage_id.id,
          'stage_name': opp.stage_id.name,
          'expected_revenue': opp.expected_revenue,
          'probability': opp.probability,
          'date_deadline': str(opp.date_deadline) if opp.date_deadline else None,
      } for opp in opportunities]
      return http.Response(json.dumps(data), content_type='application/json')

  @http.route('/api/opportunities', type='json', auth='public', methods=['POST'], csrf=False)
  def create_opportunity(self):
      data = json.loads(request.httprequest.data)
      new_opp = request.env['crm.lead'].sudo().create(data)
      self._send_opportunity_data(new_opp)
      return {'id': new_opp.id, 'name': new_opp.name}

  @http.route('/api/opportunities/<int:opp_id>', type='json', auth='public', methods=['PUT'], csrf=False)
  def update_opportunity(self, opp_id):
      data = json.loads(request.httprequest.data)
      opp = request.env['crm.lead'].sudo().browse(opp_id)
      if not opp.exists():
          return {'error': 'Opportunity not found'}, 404
      opp.write(data)
      self._send_opportunity_data(opp)
      return {'id': opp.id, 'name': opp.name}

  def _send_opportunity_data(self, opportunity):
      url = "https://preprod.hike-up.be/api/opportunity"
      data = {
          'id': opportunity.id,
          'name': opportunity.name,
          'partner_id': opportunity.partner_id.id,
          'email': opportunity.email_from,
          'phone': opportunity.phone,
          'stage_id': opportunity.stage_id.id,
          'stage_name': opportunity.stage_id.name,
          'expected_revenue': opportunity.expected_revenue,
          'probability': opportunity.probability,
          'date_deadline': str(opportunity.date_deadline) if opportunity.date_deadline else None,
      }
      try:
          response = requests.post(url, json=data, timeout=10)
          response.raise_for_status()
      except requests.exceptions.RequestException as e:
          # Log the error or handle it as needed
          _logger.error(f"Failed to send opportunity data: {e}")