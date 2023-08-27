# -*- coding: utf-8 -*-
import sys, simplejson
from datetime import datetime
from copy import deepcopy

from lkf_addons.addons.expenses.expense_utils import Expenses
#from linkaform_api import utils, network, lkf_models
#from expense_utils import Expenses

from account_settings import *



if __name__ == '__main__':
    print(sys.argv )
    current_record = simplejson.loads(sys.argv[1])
    args = simplejson.loads( sys.argv[2] )
    jwt_complete = args.pop('jwt')
    config['JWT_KEY'] = jwt_complete.split(' ')[1]
    settings.config.update(config)
    expense_obj = Expenses(settings)
    answers = current_record['answers']
    new_ans = expense_obj.update_expense_values(answers)
    expense_obj.sync_solicitud()

    sys.stdout.write(simplejson.dumps({
                'status': 101,
                'merge':{
                    'answers': new_ans,
                    'replace': True
                    }
                # 'replace_ans': current_record['answers']
            }))

