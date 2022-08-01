import json

class ActiveRecord(dict):
    """
    A class that extends the dict builtin type.
    By using this, we can create mutable objects with properties that could
    be created and accessed dynamically while maintaining dict versatility
    and operations. With this class, one doesn't need to use the object's
    __dict__ property and one can use the dict operations directly in the
    object.
    Its main purpose is to improve quality of life during development, 
    combining object and dict operations.
    Bear in mind that the update operation is a deep operation, as opposed
    to the builtin dict type update.

    - Creating properties:
        - x = ActiveRecord(foo=0,bar=1,baz=3)
        - x = ActiveRecord(**{'foo':0,'bar':1,'baz':3})

        - x = ActiveRecord()
        - x.foo = 0
        - x['bar'] = 1
        - x.update({'baz':2})
    - Retrieving properties:
        - y = x.foo
        - y = x['bar']
        - y = getattr(x,'baz')
        - y = x.get('qux')
    """
    
    def __init__(self, **kwargs):
        """
        Receives kwargs containing the data
        
        - x = ActiveRecord(foo=0,bar=1,baz=3)
        - x = ActiveRecord(**{'foo':0,'bar':1,'baz':3})

        - x = ActiveRecord()
        - x.foo = 0
        - x['bar'] = 1
        - x.update({'baz':2})
        """
        dict.__init__(self)
        self.update(**kwargs)

    def __setitem__(self, name, value):
        name = str(name) if name else 'undefined'
        dict.__setitem__(self, name, value)
    
    def __getitem__(self, name):
        name = str(name) if name else 'undefined'
        return dict.__getitem__(self,name)

    def __setattr__(self, name, value):
        self[name] = value
    
    def __getattr__(self, name):
        return self.get(name,None)

    def __str__(self):
        return json.dumps(self,default=str,ensure_ascii=False)

    def __delattr__(self,name):
        del self[name]
        
    def get(self, key, value=None):
        key = str(key) if key else 'undefined'
        return dict.get(self, key, value)

    def update(self, *args,**kwargs):
        args = list(args)
        args.append(kwargs)
        for arg in args:
            for key,value in arg.items():
                if isinstance(value,ActiveRecord):
                    pass
                elif isinstance(value, dict):
                    value = ActiveRecord(**self.get(key,{}),**value)
                elif isinstance(value, list):
                    result = []
                    for item in value:
                        if isinstance(item,ActiveRecord):
                            result.append(item)
                        elif isinstance(item, dict):
                            result.append(ActiveRecord(**item))
                        else:
                            result.append(item)
                    value = result
                self[key] = value
                
        return self