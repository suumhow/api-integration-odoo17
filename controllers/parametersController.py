from odoo import http, fields, api
from odoo.http import request
import json
import psycopg2

class ParametersController(http.Controller):

  @http.route('/api/configureOdoo', type='http', auth='public', methods=['GET'], csrf=False)
  def configure_odoo(self):
    try:
        # Add fields to res.partner model
        self._add_fields_to_model('res.partner', [
            ('x_catch_up_id', 'CU ID', 'varchar'),
            ('x_catch_up_url', 'CU URL', 'varchar')
        ])

        # Add fields to crm.lead model
        self._add_fields_to_model('crm.lead', [
            ('x_catch_up_id', 'CU ID', 'varchar'),
            ('x_catch_up_url', 'CU URL', 'varchar')
        ])

        # Add field to crm.stage model
        self._add_fields_to_model('crm.stage', [
            ('x_catch_up_id', 'CU ID', 'varchar')
        ])

        # Add field to res.users model
        self._add_fields_to_model('res.users', [
            ('x_catch_up_id', 'CU ID', 'varchar')
        ])

        # Refresh the registry
        self._refresh_registry()

        return http.Response(json.dumps({'status': 'success', 'message': 'Fields added successfully'}), content_type='application/json')
    except Exception as e:
        return http.Response(json.dumps({'status': 'error', 'message': str(e)}), content_type='application/json', status=500)

  def _add_fields_to_model(self, model_name, fields_to_add):
    cr = request.env.cr
    
    # Get the model_id
    cr.execute("SELECT id FROM ir_model WHERE model = %s", (model_name,))
    model_id = cr.fetchone()
    if not model_id:
        raise ValueError(f"Model {model_name} not found in ir_model")
    model_id = model_id[0]

    for field_name, field_description, field_type in fields_to_add:
        try:
            # Check if field already exists in ir.model.fields
            cr.execute("""
                SELECT id FROM ir_model_fields 
                WHERE name = %s AND model = %s
            """, (field_name, model_name))
            if not cr.fetchone():
                # Add field to ir.model.fields
                cr.execute("""
                    INSERT INTO ir_model_fields (name, field_description, model_id, model, ttype, state)
                    VALUES (%s, %s, %s, %s, %s, 'manual')
                """, (field_name, json.dumps({'en_US': field_description}), model_id, model_name, field_type))

            # Check if column exists in the model's table
            table_name = model_name.replace('.', '_')
            cr.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s AND column_name = %s
            """, (table_name, field_name))
            if not cr.fetchone():
                # Add column to the model's table
                cr.execute(f"""
                    ALTER TABLE {table_name} ADD COLUMN {field_name} {field_type}
                """)

            # Add field to the view
            self._add_field_to_view(model_name, field_name, field_description)

            cr.commit()
        except Exception as e:
            cr.rollback()
            raise e

  def _add_field_to_view(self, model_name, field_name, field_description):
    View = request.env['ir.ui.view'].sudo()
    arch_db = f'<field name="{field_name}" string="{field_description}"/>'

    # Find the form view for the model
    view = View.search([('model', '=', model_name), ('type', '=', 'form')], limit=1)
    if view:
        # If view exists, add the new field to it
        new_arch = view.arch_db.replace('</form>', f'{arch_db}</form>')
        view.write({'arch_db': new_arch})
    else:
        # If view doesn't exist, create a new one
        View.create({
            'name': f'{model_name.replace(".", "_")}_form',
            'model': model_name,
            'arch_db': f'<form><sheet>{arch_db}</sheet></form>',
            'type': 'form',
        })

    # Add field to tree view as well
    tree_view = View.search([('model', '=', model_name), ('type', '=', 'tree')], limit=1)
    if tree_view:
        new_arch = tree_view.arch_db.replace('</tree>', f'{arch_db}</tree>')
        tree_view.write({'arch_db': new_arch})
    else:
        View.create({
            'name': f'{model_name.replace(".", "_")}_tree',
            'model': model_name,
            'arch_db': f'<tree>{arch_db}</tree>',
            'type': 'tree',
        })

  def _refresh_registry(self):
      # This method will attempt to refresh the registry
      # It may vary depending on your Odoo version
      try:
          request.env['ir.model'].clear_caches()
          request.env['ir.model.fields'].clear_caches()
      except AttributeError:
          pass  # If clear_caches is not available, we'll skip it

      # Force reload of registry
      request.env.cr.commit()
      request.env.reset()
      request.env = request.env(context=request.env.context)