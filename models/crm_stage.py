from odoo import models, fields, api
from datetime import date, datetime
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class CrmStage(models.Model):
  _inherit = 'crm.stage'

  x_catch_up_id = fields.Char(string='Catch Up ID', readonly=True)