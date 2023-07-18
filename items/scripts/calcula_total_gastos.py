# -*- coding: utf-8 -*-
import sys, simplejson
from datetime import datetime
from copy import deepcopy

from linkaform_api import utils, network, lkf_models
from account_settings import *

from expense_utils import Expenses


def update_catalog(current_record):
    total_gasto = current_record['answers'].get('544d5ad901a4de205f391111', 0)
    print('total_gasto = ',total_gasto)
    total_gasto_aprobado = current_record['answers'].get('627bf0d5c651931d3c7eedd3')
    if total_gasto_aprobado == 0 or total_gasto_aprobado:
        total_gasto = total_gasto_aprobado
    print('total_gasto2 = ',total_gasto)
    print('total_gasto_aprobado = ',total_gasto_aprobado)
    return expense_obj.update_expense_catralog_values(current_record, total_gasto )


def get_total(current_record):
    subtotal = current_record['answers'].get('62914e2d855e9abc32eabc17', 0)
    impuesto = current_record['answers'].get('62914e2d855e9abc32eabc18', 0)
    propina = current_record['answers'].get('62914e2d855e9abc32eabc19', 0)
    expense_curreny = current_record['answers'].get(expense_obj.CATALOG_MONEDA_OBJ_ID , {}).get('62aa1fa92c20405af671d123')
    print('2 expense_obj', expense_obj)
    info_catalog = current_record['answers'].get(expense_obj.CATALOG_SOL_VIAJE_OBJ_ID, {})
    folio = info_catalog.get('610419b5d28657c73e36fcd3', '')
    destino = info_catalog.get('610419b5d28657c73e36fcd4', '')
    expense_obj.set_solicitud_catalog(folio, destino)
    print('solicitud', expense_obj.SOL_DATA)
    if not expense_obj.SOL_DATA:
        msg_error_app = {
            "6499b3586f2edb3da9155e3b":{"msg": [f"No se encontro en numero de solicitud {folio}, con destino: {destino} "], "label": "Numero de Solicitud", "error":[]},
        }
        raise Exception(simplejson.dumps(msg_error_app))
    currency = expense_obj.SOL_DATA.get('62aa1fa92c20405af671d123')
    print('currency=', currency)
    total_gasto = subtotal + impuesto + propina
    data = {
        "from":expense_curreny, 
        "date":current_record['answers'].get('583d8e10b43fdd6a4887f55b'),
        "to":currency,
        "amount":total_gasto,
        "script_id":104621
        }
    amount_dict = lkf_api_prod.run_script(data)
    print('amount_dict', amount_dict)
    amount = amount_dict.get('json',{}).get('response',{}).get('amount')
    print('amount', amount)
    if not amount:
        if amount_dict.get('error'):
            raise Exception(simplejson.dumps(amount.get('error')))
        amount = total_gasto
    list_viaje_monto_restante = current_record['answers'].get(expense_obj.CATALOG_SOL_VIAJE_OBJ_ID, {}).get('629fb33a8758b5808890b22f', ['0'])
    viaje_monto_restante = float( list_viaje_monto_restante[0] )
    # if total_gasto > viaje_monto_restante:
    #     msg_error_app = {
    #         "544d5ad901a4de205f3934ed":{"msg": [f"El Total del gasto ${total_gasto} no debe ser mayor al monto restante, {viaje_monto_restante}"], "label": "Subtotal", "error":[]},
    #     }
    #     raise Exception(simplejson.dumps(msg_error_app))
    return total_gasto, amount

if __name__ == '__main__':
    print(sys.argv )
    current_record = simplejson.loads(sys.argv[1])
    jwt_complete = simplejson.loads( sys.argv[2] )
    config['JWT_KEY'] = jwt_complete['jwt'].split(' ')[1]

    settings.config.update(config)
    lkf_api = utils.Cache(settings)
    jwt_parent = lkf_api.get_jwt( api_key=settings.config['APIKEY'], user=settings.config['USERNAME'] )
    config['USER_JWT_PARENT'] = jwt_parent
    settings.config.update(config)
    lkf_api = utils.Cache(settings)
    net = network.Network(settings)
    cr = net.get_collections()
    expense_obj = Expenses(cr, lkf_api, settings)

    config['PROTOCOL'] = 'https'
    config['HOST'] ='app.linkaform.com'
    settings.config.update(config)
    lkf_api_prod = utils.Cache(settings)

    total_gasto, amount = get_total(current_record)
    current_record['answers']['544d5ad901a4de205f3934ed'] = total_gasto
    current_record['answers']['544d5ad901a4de205f391111'] = amount
    update_ok = update_catalog(current_record)

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