import os
from external.utils.active_record import ActiveRecord

class Tenant(ActiveRecord):
    
    def __init__(self,provider,tenant_name):
        self.project = os.environ['repoName']
        self.stage = os.environ['stage']
        self.provider = provider
        self.tenant_name = tenant_name

    def to_config_args(self):
        return [
            self.stage,
            self.provider,
            self.tenant_name
        ]

    def tenant(self):
        return '-'.join(filter(None,[self.project]+self.to_config_args()))