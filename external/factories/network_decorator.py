
import os
import json 

from external.lib.config import BaseConfig
from external.lib.tenant import Tenant

import external.utils.commons as commons

class Network():

    def __call__(self, f):
        
        def run(event, context):
            
            response = {
                "headers":{
                    "content-type": "application/json",
                    },
                "statusCode": 500
            }

            path_params = event.get('pathParameters',{})

            tenant = Tenant(path_params.get('provider'))
            network_config = BaseConfig(*tenant.to_config_args(),'network')
            
            try:
                body = f(tenant=tenant,event=event,context=context)

                response['body'] = body
                response['statusCode'] = 200

            except Exception as e:
                e = list(e.args)
                commons.log.exception(e[0])

                raise
            finally:
                commons.log.info("response: {}".format(response))
                if 'body' in response.keys(): 
                    response['body'] = json.dumps(response['body'],ensure_ascii=False,default=str)
                    return response
        
        return run