from tornado.web import RequestHandler
import tornado.web
import json
from utils.session import Session
class BaseHandler(RequestHandler):
    @property
    def db_redis(self):
        return self.application.db_redis
    @property
    def db_mysql(self):
        return self.application.db_mysql
    def set_default_headers(self):
        """设置默认json格式"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def prepare(self):
        self.xsrf_token
        if self.request.headers.get('Content-Type','').startswith('application/json'):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = {}

    def write_error(self, status_code, **kwargs):
        pass
    def get_current_user(self):
        self.session = Session(self)
        # 判断是否存在seesion.data,存在登录,不存在未登录
        return self.session.data

    # def flush(self, include_footers: bool = False) :
    #     pass

class StaticFileHandler(tornado.web.StaticFileHandler):
    def __init__(self,*args,**kwargs):
        super(StaticFileHandler,self).__init__(*args,**kwargs)
        self.xsrf_token
