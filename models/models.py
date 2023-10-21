import base64
from odoo import models, fields, api, _
import csv
from io import StringIO
import json

class DataBulkUploadSource(models.Model):
    _name = 'data.bulk.upload.source'
    _description = 'Data Bulk Upload Sources'

    name = fields.Char(string='Source Name', required=True, help="A descriptive name for this data source.")
    model_id = fields.Many2one('ir.model', string='Data Source', help="Select the source of data for this entry")
    field_ids = fields.One2many('data.bulk.upload.source.field', 'bulk_upload_source_id', string='Data Fields')
    upload_id = fields.Many2one('data.bulk.upload', string='Related Upload', ondelete='cascade')

class DataBulkUploadSourceField(models.Model):
    _name = 'data.bulk.upload.source.field'
    _description = 'Data Bulk Upload Source Fields'

    name = fields.Char(string='Field Description')
    field_id = fields.Many2one('ir.model.fields', string='Field Name', domain="[('model_id', '=', parent.model_id)]")
    bulk_upload_source_id = fields.Many2one('data.bulk.upload.source', string='Data Source')

class DataBulkUpload(models.Model):
    _name = 'data.bulk.upload'
    _description = 'Data Bulk Upload'

    name = fields.Char(string='Upload Name', required=True)
    source_ids = fields.Many2many('data.bulk.upload.source', 'data_bulk_upload_source_rel', 'upload_id', 'bulk_upload_source_id', string='Data Sources')
    upload_data = fields.Text(string='Upload Data (JSON)', help="The data to be visualized in JSON format")
    js_code = fields.Text(string='JS Code for Upload', help="JS code to render the upload")

    csv_data_file = fields.Binary(string='CSV Data File')
    csv_filename = fields.Char(string='CSV Filename')

    thumbnail = fields.Binary()
    sequence = fields.Integer()
    group_ids = fields.Many2many('res.groups', default=lambda self: self.env.ref('base.group_user'))

    @api.depends('source_ids')
    def _compute_upload_data(self):
        for record in self:
            data_list = []
            for source in record.source_ids:
                model = source.model_id.model
                Model = self.env[model]
                for field in source.field_ids:
                    field_name = field.field_id.name
                    data_list.append({
                        'name': f"{source.name}_{field_name}",
                        'values': Model.search([]).mapped(field_name)
                    })

            record.upload_data = json.dumps(data_list)

    def button_execute_js(self):
        js_code = self.js_code
        return {
            'type': 'ir.actions.client',
            'tag': 'execute_js',
            'params': {
                'js_code': js_code,
        },
    }

    def export_bulk_upload_csv(self):
        self.ensure_one()
        
        # output = StringIO()
        # writer = csv.writer(output, quoting=csv.QUOTE_ALL)

        # header = []
        # fields_mapping = {}
        # index_fields = {}
        # row_counter = 0

        # for data_source in self.data_source_ids:
        #     model_name = data_source.model_id.model
        #     for ds_field in data_source.field_ids:
        #         field_name = ds_field.field_id.name
        #         combined_name = f"{model_name}_{field_name}"
        #         if ds_field.field_id.ttype in ['many2one', 'many2many', 'one2many']:
        #             header.extend([combined_name + '_id', combined_name + '_name'])
        #         else:
        #             header.append(combined_name)
        #         fields_mapping[combined_name] = ds_field.field_id
        #         if ds_field.name.lower() == 'index':
        #             index_fields[model_name] = field_name

        # writer.writerow(header)

        # primary_model = self.data_source_ids[0].model_id.model
        # primary_records = self.env[primary_model].search([])

        # for primary_record in primary_records:
        #     row = []

        #     for combined_name, field in fields_mapping.items():
        #         model_name = field.model_id.model
        #         field_name = field.name
        #         field_type = field.ttype

        #         if model_name in index_fields:
        #             index_value = getattr(primary_record, index_fields[primary_model])
        #             records = self.env[model_name].search([(index_fields[model_name], '=', index_value.id if isinstance(index_value, models.BaseModel) else index_value)], limit=1)
        #             record = records[0] if records else None
        #         else:
        #             records = self.env[model_name].search([])
        #             record = records[row_counter] if len(records) > row_counter else None

        #         if record:
        #             if field_type == 'many2one':
        #                 related_record = record[field_name]
        #                 if related_record:
        #                     row.extend([related_record.id, related_record.name])
        #                 else:
        #                     row.extend(['', ''])
        #             elif field_type in ['many2many', 'one2many']:
        #                 ids = [related.id for related in record[field_name][:5]]
        #                 names = [related.name for related in record[field_name][:5]]
        #                 row.extend(['| '.join(map(str, ids)), '| '.join(names)])
        #             else:
        #                 row.append(record[field_name])
        #         else:
        #             if field_type in ['many2one', 'many2many', 'one2many']:
        #                 row.extend(['', ''])
        #             else:
        #                 row.append('')

        #     writer.writerow(row)
        #     row_counter += 1

        # output.seek(0)
        # file_data = output.getvalue().encode()
        # # Please note that the attachment filename has also been updated
        # attachment_vals = {
        #     'name': 'data_bulk_upload_export.csv',
        #     'datas': base64.b64encode(file_data),
        #     'res_model': 'data.bulk.upload',
        #     'res_id': self.id,
        #     'type': 'binary',
        # }

        # attachment = self.env['ir.attachment'].create(attachment_vals)
        # self.csv_data_file = base64.b64encode(file_data)
        # self.csv_filename = 'data_bulk_upload_export.csv'
        # return {
        #     'type': 'ir.actions.act_url',
        #     'url': f'/web/content/{attachment.id}?download=true',
        #     'target': 'self',
        # }



    # field_id = fields.Many2one('ir.model.fields', string='Data Field', domain="[('model_id', '=', model_id)]", help="Select the field (column) of data you want to visualize")