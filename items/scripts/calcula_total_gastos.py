# -*- coding: utf-8 -*-
import sys, simplejson
from datetime import datetime
from copy import deepcopy

from lkf_addons.addons.expenses.expense_utils import Expenses
# from linkaform_api import utils, network, lkf_models
#from expense_utils import Expenses

from account_settings import *


if __name__ == '__main__':
    print(sys.argv )
    current_record = simplejson.loads(sys.argv[1])
    jwt_complete = simplejson.loads( sys.argv[2] )
    config['JWT_KEY'] = jwt_complete['jwt'].split(' ')[1]
    settings.config.update(config)
    exp_obj = Expenses(settings)
    answers = current_record['answers']
    current_record['answers'] = exp_obj.get_total(answers)
    catalog_obj_id = exp_obj.CATALOG_SOL_VIAJE_OBJ_ID
    folio = answers.get(catalog_obj_id,{}).get(exp_obj.fdict['cat_folio'])
    update_ok = exp_obj.update_solicitud(folio, answers)
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