# -*- coding: utf-8 -*-
import sys, simplejson
from linkaform_api import settings, utils, network, lkf_models
from account_settings import *



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

