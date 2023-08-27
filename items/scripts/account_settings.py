# coding: utf-8
#!/usr/bin/python
from linkaform_api import settings
# import lkfpwd

#---------PROD
#settings.mongo_hosts = 'db2.linkaform.com:27017,db3.linkaform.com:27017,db4.linkaform.com:27017'
settings.mongo_port = 27017
settings.mongo_hosts = '192.168.0.25:27017'
#---------PREPROD
#settings.mongo_hosts = 'dbs2.lkf.cloud:27918'
#settings.mongo_port = 27918
settings.MONGODB_URI = 'mongodb://%s/'%(settings.mongo_hosts)

account_id = 12068

config = {
    'USERNAME' : 'ydelgado@bacao.com.co',
    'API_KEY':"07c7413b41c8b8a49dd518d3caf4f3cc59740090",
    #'APIKEY':"07c7413b41c8b8a49dd518d3caf4f3cc59740090",
    #'PROTOCOL' : 'https', #http or https
    # 'HOST' : '172.19.0.1:8000',
    #'HOST' : 'preprod.linkaform.com',
    #'PROTOCOL' : 'https', #http or https
    #'HOST' : 'app.linkaform.com',
    'PROTOCOL' : 'http', #http or https
    'HOST' : '192.168.0.25:8000',
    'MONGODB_PORT':settings.mongo_port,
    'MONGODB_HOST': settings.mongo_hosts,
    'MONGODB_USER': 'account_{}'.format(account_id),
    'PORT' : settings.mongo_port,
    'USER_ID' : account_id,
    'ACCOUNT_ID' : account_id,
    'KEYS_POSITION' : {},
    'IS_USING_APIKEY' : False,
    'USE_JWT' : True,
    'JWT_KEY':'',
}
settings.config.update(config)

