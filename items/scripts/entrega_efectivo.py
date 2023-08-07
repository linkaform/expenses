# -*- coding: utf-8 -*-
import sys, simplejson
from datetime import datetime
from copy import deepcopy

# from linkaform_api import utils, network, lkf_models
from account_settings import *

from expense_utils import Expenses



if __name__ == '__main__':
    print(sys.argv )
    current_record = simplejson.loads(sys.argv[1])
    jwt_complete = simplejson.loads( sys.argv[2] )
    config['JWT_KEY'] = jwt_complete['jwt'].split(' ')[1]
    settings.config.update(config)
    # lkf_api = utils.Cache(settings)
    # jwt_parent = lkf_api.get_jwt( api_key=settings.config['APIKEY'], user=settings.config['USERNAME'] )
    # config['USER_JWT_PARENT'] = jwt_parent
    # settings.config.update(config)
    # # lkf_api = utils.Cache(settings)
    # net = network.Network(settings)
    expense_obj = Expenses(settings)
    print('1 expense_obj', expense_obj)
    info_catalog = current_record['answers'].get(expense_obj.CATALOG_SOL_VIAJE_OBJ_ID, {})
    folio = info_catalog.get('610419b5d28657c73e36fcd3', '')
    destino = info_catalog.get('610419b5d28657c73e36fcd4', '')
    print('folio=', folio)
    print('destino=', destino)
    expense_obj.set_solicitud_catalog(folio, destino)
    print('expense_obj', expense_obj.SOL_DATA)
    cash = current_record.get('answers').get('544d5ad901a4de205f391111')
    update_ok = expense_obj.update_expense_catalog_values(current_record, total_gasto=0, anticipo_efectivo=cash)

    if update_ok:
            sys.stdout.write(simplejson.dumps({
                'status': 101,
                'replace_ans': current_record['answers']
            }))
    else:
        msg_error_app = {
            "610419b5d28657c73e36fcd3":{"msg": ["Error al actualizar la solicitud"], "label": "Numero de Solicitud", "error":[]},
        }
        raise Exception(simplejson.dumps(msg_error_app))