from inspect import signature
import json
import os
from pathlib import Path
from functools import wraps
from typing import Any
from external.lib.tenant import Tenant

from external.utils.active_record import ActiveRecord

ROOT_DIR = Path(__file__).parent.parent

class BaseConfig(ActiveRecord):
    """
    ActiveRecord object containing configurations.
    """
    
    @staticmethod
    def configured(*nodes):
        """
        Decorator used to inject a BaseConfig object into the decorated function.
        It expects either a BaseConfig object in args or a BaseConfig with configs
        key in kwargs. Else, it will instantiate a BaseConfig from a configs.json file
        in the root of the project, looking for a config node with the name of the
        decorated function or the specified node decorator param.

        Parameters
        ----------
        nodes : tuple, optional
            A tuple of node names representing a namespace containign the decorated method's
            configuration in the configs.json file in the root of the project. Defaults to 
            the decorated function's name.
        """
        def decorator(f):
            @wraps(f)
            def wrapper(*args,**kwargs):
                configs = next(iter(filter(lambda x: isinstance(x,BaseConfig),args)),None)
                configs = configs or kwargs.get('configs')
                configs = configs or BaseConfig(*nodes or f.__name__) 
                kwargs['configs'] = configs
                return f(*args,**kwargs)

            return wrapper
        return decorator

    def __init__(
            self
            ,*args
            ,**kwargs
            ):
        """
        ActiveRecord object containing configurations.

        Parameters
        ----------
        *args : tuple, optional
            Tuple of strings describing the namespace path of the desired configuration.
            When defined, BaseConfig will try to load a .json file from either an environment
            variable defined path or from a configs folder in the root of the project.
            Once the folder has been accessed, it'll test file names containing the defined args.
            Then, it'll try to access the namespace using the remaining args sequence, finally
            returning an ActiveRecord containing the configuration.
            Furthermore, for every iteration while searching for the configurations, it'll look
            for the last arg. Meaning that one could define a "global" configuration that is
            applied to all configs and overwritten once it's found on a more specific namespace
            Examples:
                Given configs.json file containing:
                    {
                        "foo":{
                            "bar":{
                                "baz":0
                                "qux":1
                            }
                        }
                    }
                BaseConfig('foo')
                is the equivalent of
                ActiveRecord(
                    **{
                        "bar":{
                            "baz":0
                            "qux":1
                            }
                        }
                    )
                and BaseConfig('foo','bar')
                is the equivalent of
                ActiveRecord(
                    **{
                        "baz":0
                        "qux":1
                        }
                    )
                The same results could be achieved with a file named
                configs.json containing:
                    {
                        "bar":{
                            "baz":0
                            "qux":1
                        }
                    }
                As well as configs-foo.json, containing:
                    {
                        "bar":{
                            "baz":0
                            "qux":1
                        }
                    }
                This allows for better flexibility while organizing
                project configurations
        **kwargs: dict, optional
            Dict containing the config itself.
        """
        
        self._config_path_separator = '.'

        if kwargs:
            super().__init__(**kwargs)
        else:
            args = list(args)

            self._config_path = args
            self.tenant = len(signature(Tenant.__init__))-1
            
            configs_path = os.environ.get("configs_path",'configs')

            for index, arg in enumerate(args):
                path = ROOT_DIR.joinpath(configs_path,f'{"-".join(["configs"]+args[:index])}.json')
                if path.exists():
                    config_node = json.load(open(path, encoding='utf-8')) if args else {}
                    current_node = config_node
                    for inner_arg in args[index:]:
                        current_node = config_node.get(inner_arg) or config_node.get(args[-1])
                    self.update(current_node or {})
    
    def get_config(self, *args):
        """
        Method used to interactively access configuration namespaces.
        Looks for namespace in file-based configs, falls back to environment variables
        Attempts to parse string value to json to parse json-based env var.

        Parameters
        ----------
        *args : tuple
            Dynamic arguments, all strings. Should be ordered and represent
            the namespace path to access desired configuration.
            Example:
            A call like get_config('foo','bar') will return 3 in the
            following configuration:
            {
                'baz':{
                    'qux': 2
                    }
                },
                'foo':{
                    'bar': 3
                    }
                }
            }
        """
        result = self._config 
        config_path = f'{self._config_path_separator}'.join(self._config_path + list(args)) 
        for arg in args:
            result = result.get(arg,os.environ.get(arg,os.environ.get(config_path.replace('.','_')))) 
        
        try:
            if result and isinstance(result, str): result = json.loads(result)
        except ValueError as ve:
            pass

        return result