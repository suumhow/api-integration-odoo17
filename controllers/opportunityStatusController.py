from odoo import http
from odoo.http import request
import json
from datetime import date, datetime

class OpportunityStatusController(http.Controller):
  
  def _json_serialize(self, value):
      if isinstance(value, (date, datetime)):
          return value.isoformat()
      if hasattr(value, 'id'):
          return value.id
      return str(value)

  @http.route('/api/opportunity_stages', type='http', auth='public', methods=['GET'], csrf=False)
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

  # Typically, stages are predefined and not created/updated via API
