# -*- coding: utf-8 -*-


from external.connectors.aws_secrets_adapter import AWSSecretsAdapter
from external.lib.config import BaseConfig
from external.lib.tenant import Tenant

import external.utils.commons as commons

class Secrets():

    def __init__(self,adapter_impls={}):

        self.__adapter_impls = {
            'aws':AWSSecretsAdapter
            }
        self.__adapter_impls = {**self.__adapter_impls,**adapter_impls} 

    @classmethod
    def get_adapter(cls,tenant):
        
        secrets_config = BaseConfig(tenant.to_config_args(),'secrets')
        platform = secrets_config.get_config('provider')
        secrets_adapter = None
        if platform:
            secrets_adapter = cls.__adapter_impls[platform](secrets_config)
        else:
            commons.log.warning('No secrets config found. Secrets adapter not instantiated!')
        
        return secrets_adapter

    def __call__(self, f):
        
        def run(tenant, **kwargs):
            
            secrets_adapter = self.get_adapter(tenant)
                
            return f(secrets_adapter=secrets_adapter,tenant=tenant,  **kwargs)
                
        return run

    