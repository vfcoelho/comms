
class AWSBaseAuthorizer():

    class EFFECT():
        DENY="Deny"
        ALLOW="Allow"

    def __init__(self,configs,secrets_adapter) -> None:
        self.__secrets_adapter = secrets_adapter
        self.__configs = configs

    def authorize(self,event):
        
        return self.build_response()


    def build_response(self,principal=None,resource=None,effect=EFFECT.DENY):
        
        id_key = id_key or principal

        result = {
            # The principal user identification associated with the token sent by the client.
            "principalId": principal,
            "usageIdentifierKey": id_key, #used for usage plan
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": effect,
                        "Resource": resource
                    }
                ]
            }
        }

        return result