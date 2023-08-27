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
    expense_obj = Expenses(settings)
    info_catalog = current_record['answers'].get(expense_obj.CATALOG_SOL_VIAJE_OBJ_ID, {})
    folio = info_catalog.get(expense_obj.fdict['cat_folio'], '')
    print('folio=', folio)
    update_ok = expense_obj.update_solicitud(folio, current_record['answers'])

    if not update_ok:
        msg_error_app = {
            "610419b5d28657c73e36fcd3":{"msg": ["Error al actualizar la solicitud"], "label": "Numero de Solicitud", "error":[]},
        }
        raise Exception(simplejson.dumps(msg_error_app))