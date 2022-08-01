

import json
from external.connectors.default import AWSBaseAuthorizer
import external.utils.commons as commons

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

class DiscordAuthorizer(AWSBaseAuthorizer):

    def authorize(self, event):
        
        body = json.loads(event.get('body','{}')) # doesn't look like this parse should be here
        resource=event.get('methodArn')

        principal = body.get('application_id')


        secrets = self.__secrets_adapter.get_secret(secret_path=self.__configs.get('secret',{}).get('path',self.__configs.tenant))
        verify_key = VerifyKey(bytes.fromhex(secrets.PUBLIC_KEY))

        signature = event["headers"]["X-Signature-Ed25519"]
        timestamp = event["headers"]["X-Signature-Timestamp"]
        body = event.body

        try:
            verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
            effect = super.EFFECT.ALLOW
        except BadSignatureError:
            commons.log.warning("Invalid Request Signature")

        return super().build_response(principal, resource, effect)
