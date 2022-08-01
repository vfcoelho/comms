
from external.connectors.default import AWSBaseAuthorizer
from external.connectors.discord_communicator_adapter import DiscordAuthorizer 

class ProviderAuth():

    def __init__(self):

        self.__strategies = {
            'discord':DiscordAuthorizer,
            'default':AWSBaseAuthorizer
        }

    def __call__(self, f):
        
        def run(event, context):
            
            pass
        
        return run