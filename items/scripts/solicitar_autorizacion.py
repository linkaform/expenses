# -*- coding: utf-8 -*-
import sys, simplejson
from datetime import datetime
from copy import deepcopy

from linkaform_api import utils, network, lkf_models
from account_settings import *

from expense_utils import Expenses


if __name__ == '__main__':
    # print(sys.argv )
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
    expense_obj.autorizacion_viaticos(current_record.get('folio'))

