
from external.connectors.default import AWSBaseAuthorizer
from external.connectors.discord_communicator_adapter import DiscordAuthorizer
from external.lib.config import BaseConfig 

class ProviderAuth():

    def __init__(self):

        self.__strategies = {
            'discord':DiscordAuthorizer,
            'default':AWSBaseAuthorizer
        }

    def __call__(self, f):
        
        def run(secrets_adapter, tenant, **kwargs):
            authorizer_configs = BaseConfig(*tenant.to_config_args(),tenant.provider,'authorizer')

            provider_authorizer = self.__strategies.get(tenant.provider,'default')(authorizer_configs,secrets_adapter)
            return f(provider_authorizer=provider_authorizer,tenant=tenant,**kwargs)
        
        return run