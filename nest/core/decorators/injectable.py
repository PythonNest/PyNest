from nest.common.constants import INJECTABLE_TOKEN 

def Injectable(cls):
    setattr(cls, INJECTABLE_TOKEN, True)
    return cls