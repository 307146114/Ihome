import  functools
from  utils.response_code import RET
def required_login(func):
    @functools.wraps(func)
    def wrapper(requestHandler,*args,**kwargs):
        if not requestHandler.get_current_user():
            return requestHandler.write(dict(errcode=RET.LOGINERR,errmsg="用户未登录"))
        else:
            func(requestHandler,*args,**kwargs)

    return wrapper