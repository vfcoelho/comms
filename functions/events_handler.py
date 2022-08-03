import json

from external.connectors.aws_secrets_adapter import AWSSecretsAdapter
from external.factories.network_decorator import Network
from external.factories.provider_auth import ProviderAuth
from external.lib.config import BaseConfig
from external.lib.tenant import Tenant
from external.utils.active_record import ActiveRecord

import external.utils.commons as commons

@Network()
@ProviderAuth()
def authorizer(provider_authorizer, event, context): #this should be in an infrastructure repository
    
    EFFECT = ActiveRecord(ALLOW='Allow',DENY='Deny')
    effect = EFFECT.DENY
    principal = None
    id_key = None

    path_params = event.get('pathParameters', {})

    platform = path_params['producer']

    request_stage = event["requestContext"]["stage"]

    authorization_type = event['type']

    if authorization_type == 'REQUEST':
        #discord signature verification
        from nacl.signing import VerifyKey
        from nacl.exceptions import BadSignatureError

        # this belongs in a factory
        tenant = Tenant('discord','VI')
        configs = BaseConfig(tenant.to_config_args())
        secrets_configs = BaseConfig(tenant.to_config_args(),'secrets')
        secrets_adapter = AWSSecretsAdapter(secrets_configs)
        secrets = secrets_adapter.get_secret(secret_path=configs.get('secret',{}).get('path',configs.tenant))
        body = json.loads(event['body'])
        principal = body['application_id']

        # Your public key can be found on your application in the Developer Portal
        verify_key = VerifyKey(bytes.fromhex(secrets.PUBLIC_KEY))

        signature = event["headers"]["X-Signature-Ed25519"]
        timestamp = event["headers"]["X-Signature-Timestamp"]
        body = event.body

        try:
            verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
            effect = EFFECT.ALLOW
        except BadSignatureError:
            commons.log.warning("Invalid Request Signature")

    result = {
        # The principal user identification associated with the token sent by the client.
        "principalId": principal,
        # "usageIdentifierKey": id_key, #used for usage plan
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": event.get('methodArn')
                }
            ]
        }
    }
    commons.log.info(result)
    return result


def incoming_hook(event,context):
    print(event)

    response = {
        "headers":{
            "content-type": "application/json",
            "Access-Control-Allow-Origin": "*"
            },
        "statusCode": 500
    }

    response['statusCode'] = 200
    #discord url verification response
    response['body'] = json.dumps({"type": 1})

    return response
