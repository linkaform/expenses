# -*- coding: utf-8 -*-
import sys, simplejson

from lkf_addons.addons.expenses.expense_utils import Expenses
#from expense_utils import Expenses

from account_settings import *



class LocalExpenses(Expenses):


    def update_autorization_records(self, answers):
        answers['test'] = 'update....'
        result = super().update_autorization_records(answers)
        return result
        # result = expense_obj.update_autorization_records(answers)


if __name__ == '__main__':
    print(sys.argv)
    print('\n\n\n')
    current_record = simplejson.loads(sys.argv[1])
    jwt_complete = simplejson.loads( sys.argv[2] )
    config['JWT_KEY'] = jwt_complete['jwt'].split(' ')[1]
    settings.config.update(config)
    # jwt_complete = simplejson.loads(sys.argv[2])
    # config['JWT_KEY'] = jwt_complete["jwt"].split(' ')[1]
    # settings.config.update(config)
    # net = network.Network(settings)
    # cr = net.get_collections()
    # lkf_api = utils.Cache(settings)
    answers = current_record['answers']
    # expense_obj = Expenses(settings)
    local_exp  = LocalExpenses(settings)
    current_record['answers'] = local_exp.update_autorization_records(answers)
    print('answers to update=', current_record['answers'])
    sys.stdout.write(simplejson.dumps({
        'status': 101,
        'replace_ans': current_record['answers']
    }))