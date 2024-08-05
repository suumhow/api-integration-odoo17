{
  'name': 'API Integration',
  'version': '1.22',
  'category': 'Tools',
  'summary': 'Custom API endpoints for data retrieval',
  'description': """
      This module provides custom API endpoints for retrieving and pushing data from Odoo, also add triggers to send data to an external api.
  """,
  'author': 'Thomas de lamarzelle',
  'website': 'https://www.app.catch-up.be/',
  'depends': ['base', 'contacts', 'crm'],
  'data': [
      'security/ir.model.access.csv',
  ],
  'depends': ['base', 'contacts', 'crm'],
  'installable': True,
  'application': True,
  'auto_install': False,
}
