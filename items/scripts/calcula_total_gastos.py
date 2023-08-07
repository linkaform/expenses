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
    answers = current_record['answers']
    jwt_complete = simplejson.loads( sys.argv[2] )
    config['JWT_KEY'] = jwt_complete['jwt'].split(' ')[1]
    settings.config.update(config)
    exp_obj = Expenses(settings)
    # CATALOG_SOL_VIAJE_OBJ_ID = exp_obj.CATALOG_SOL_VIAJE_OBJ_ID
    # folio_solicitud = answers.get(exp_obj.CATALOG_SOL_VIAJE_OBJ_ID,{}).get('610419b5d28657c73e36fcd3')
    # exp_obj.set_solicitud_catalog(folio_solicitud)

    answers = current_record['answers']
    current_record['answers'] = exp_obj.get_total(answers)

    update_ok = exp_obj.update_solicitud(current_record)

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