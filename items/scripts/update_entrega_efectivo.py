# -*- coding: utf-8 -*-
import sys, simplejson
from linkaform_api import settings, utils, network, lkf_models
from account_settings import *


def get_record_catalog_and_update_current_record( current_record ):
    folio = current_record['folio']
    mango_query = {"selector":
    {"answers":
        {"$and":[
            {'610419b5d28657c73e36fcd3': {'$eq': folio}}
    ]}},
    "limit":1,
    "skip":0}
    catalog_data = lkm.catalog_id('solicitudes_de_gastos')
    catalog_id = catalog_data.get('id')
    catalog_obj_id = catalog_data.get('obj_id')
    res = lkf_api.search_catalog( lkm.catalog_id('solicitudes_de_gastos', 'id'), mango_query, jwt_settings_key='JWT_KEY')
    if not res:
        print('no se encontro el registro res=',res)
        return False
    for r in res:
        cr.update_one({
            'folio': folio,
            'form_id': current_record['form_id'],
            'deleted_at': {'$exists': False}
        },{'$set': {
            f'answers.{catalog_obj_id}': {
                '610419b5d28657c73e36fcd4':  r.get('610419b5d28657c73e36fcd4') ,
                '610419b5d28657c73e36fcd3': folio,
                '610419b5d28657c73e36fcd5': [ r.get('610419b5d28657c73e36fcd5') ],
                '610419b5d28657c73e36fcd6': [ r.get('610419b5d28657c73e36fcd6') ],
                '610419e33a05c520d90814d3': [ r.get('610419e33a05c520d90814d3') ],

            },
        }})

if __name__ == '__main__':
    print(sys.argv)
    current_record = simplejson.loads( sys.argv[1] )
    jwt_complete = simplejson.loads( sys.argv[2] )
    config['JWT_KEY'] = jwt_complete['jwt'].split(' ')[1]
    settings.config.update(config)
    # print('settings', settings.config)
    lkf_api = utils.Cache(settings)
    net = network.Network(settings)
    cr = net.get_collections()
    lkm = lkf_models.LKFModules(settings)

    get_record_catalog_and_update_current_record( current_record )