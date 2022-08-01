
from functools import reduce
import boto3
import base64
import json
import external.utils.commons as commons

from external.utils.active_record import ActiveRecord
from external.lib.config import BaseConfig
from external.utils.tool_box import singleton


@singleton
class AWSSecretsAdapter():
    
    def __init__(
            self
            ,config_class 
            ):
        
        self.__configs = config_class
        self.__client = boto3.client(service_name='secretsmanager',region_name=config_class.get_config('region'))
        self.__secret = {}
    

    def get_secret(self,vault_name=None,secret_path=None):
        
        secret_id = (vault_name or self.__configs.get_config('vault_name'))
        
        if not self.__secret[secret_id]:
            get_secret_value_response = {}
            commons.log.warning("AWSSecretsAdapter: Calling Secrets Manager!")
            try:
                get_secret_value_response = self.__client.get_secret_value(SecretId=secret_id)
            except Exception as e:
                commons.log.warning(f'[AWSSecretsAdapter]: {str(e)}')
            
            data = '{}'
            
            if 'SecretString' in get_secret_value_response:
                data = get_secret_value_response['SecretString']
            elif 'SecretBinary' in get_secret_value_response:
                data = base64.b64decode(get_secret_value_response['SecretBinary'])
                
            self.__secret[secret_id] = ActiveRecord(**json.loads(data))
        
        return reduce(lambda acc,upd: acc[upd],secret_path,self.__secret)
