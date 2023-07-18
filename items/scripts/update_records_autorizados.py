# -*- coding: utf-8 -*-
import sys, simplejson
from linkaform_api import settings, network, utils
from account_settings import *

def get_record_from_db(form_id, folio):
    query = {
        'form_id': form_id,
        'folio': folio,
        'deleted_at': {'$exists': False}
    }
    select_columns = {'folio':1,'user_id':1,'form_id':1,'answers':1}
    record_found = cr.find(query, select_columns)
    return record_found.next()

def update_set_records(current_record):
    dict_records_to_update = {}
    for viatico in current_record['answers'].get('62950fd07b46d19bfd08d8fd', []):
        type_record = viatico.get('6295133afadaf9e529d5a096', '')
        folio_origen = viatico.get('6296df808717058b58bfe656', '')
        if not dict_records_to_update.get(type_record):
            dict_records_to_update[type_record] = {}
        if not dict_records_to_update[type_record].get(folio_origen):
            dict_records_to_update[type_record][folio_origen] = {}
        tipo_gasto = viatico.get('6295294c70d902f9e1499645', '')
        if not dict_records_to_update[type_record][folio_origen].get(tipo_gasto):
            dict_records_to_update[type_record][folio_origen][tipo_gasto] = {
                'status': viatico.get('62952ab5ec3852e91f08d93b', ''),
                'monto_autorizado': viatico.get('62952ab5ec3852e91f08d93c', 0),
                'motivo_no_autorizado': viatico.get('62952ab5ec3852e91f08d93d', ''),
                'comentarios': viatico.get('62952ab5ec3852e91f08d93e', '')
            }
    print(dict_records_to_update)
    for type_rec in dict_records_to_update:
        for folio in dict_records_to_update[type_rec]:
            dict_info_update = dict_records_to_update[type_rec][folio]
            form_id = FORM_SOLICITUD_VIATICOS_ID if type_rec == 'gastos_sin_anticipo' else FORM_SOLICITUD_VIATICOS_ID
            record = get_record_from_db(form_id, folio)
            if type_rec == 'delivery':
                for gasto in record['answers'].get('6271bdf1bfe8e14d78b94879', []):
                    delivery_tipo_gasto = gasto.get('544d5ad901a4de205f3934ec', '')
                    info_set = dict_info_update.get(delivery_tipo_gasto, {})
                    if info_set:
                        gasto['627405bbac760a3458563a3e'] = info_set.get('status', '')
                        gasto['627405bbac760a3458563a3f'] = info_set.get('motivo_no_autorizado', '')
                        gasto['627405bbac760a3458563a41'] = info_set.get('comentarios', '')
                        if info_set.get('monto_autorizado'):
                            gasto['627befc7d4f0a9bc6a72b7bb'] = info_set.get('monto_autorizado')
            else:
                viaje_tipo_gasto = record['answers'].get('544d5ad901a4de205f3934ec', '')
                info_set = dict_info_update.get(viaje_tipo_gasto, {})
                if info_set:
                    record['answers']['544d5b4e01a4de205e2b2169'] = info_set.get('status', '')
                    record['answers']['6271bd58d96e7e7ab68d2c4b'] = info_set.get('motivo_no_autorizado', '')
                    record['answers']['544d5b4e01a4de205e2b216a'] = info_set.get('comentarios')
                    if info_set.get('monto_autorizado'):
                        record['answers']['627bf0d5c651931d3c7eedd3'] = info_set.get('monto_autorizado')
            res_update = lkf_api.patch_record(record, jwt_settings_key='JWT_KEY')
            print('folio= {} form_id= {} res_update= {}'.format(folio, form_id, res_update))

if __name__ == '__main__':
    current_record = simplejson.loads(sys.argv[1])
    jwt_complete = simplejson.loads(sys.argv[2])
    config['JWT_KEY'] = jwt_complete["jwt"].split(' ')[1]
    settings.config.update(config)
    net = network.Network(settings)
    cr = net.get_collections()
    lkf_api = utils.Cache(settings)
    lkm = lkf_models.LKFModules(settings)
    FORM_SOLICITUD_VIATICOS_ID = lkm.form_id('registros_de_gastos_de_viaje')['id']
    update_set_records(current_record)