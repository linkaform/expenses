# -*- coding: utf-8 -*-
import sys, simplejson
from datetime import datetime
from account_settings import *

from expense_utils import Expenses



if __name__ == '__main__':
    print(sys.argv)
    current_record = simplejson.loads(sys.argv[1])
    jwt_complete = simplejson.loads( sys.argv[2] )
    config['JWT_KEY'] = jwt_complete['jwt'].split(' ')[1]
    settings.config.update(config)
    expense_obj = Expenses(settings)
    if not expense_obj.update_solicitud_from_catalog( current_record ):
        msg_error_app = {
            "64bebf27737569e96980d251":{"msg": ["Error al actualizar la solicitud"], "label": "Numero de Solicitud", "error":[]},
        }
        raise Exception(simplejson.dumps(msg_error_app))