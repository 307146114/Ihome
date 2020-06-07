from tornado.web import HTTPServer
from tornado.options import define,options
from tornado.ioloop import IOLoop
from  config import settings,mysql_options,redis_options
from  urls import urls
from  redis import Redis
import torndb_python3
import config
import tornado.web
define('port',default=8000,type=int,help="")
class Application(tornado.web.Application):
    def __init__(self,*args ,**kwargs):
        super(Application,self).__init__(*args,**kwargs)
        # 绑定 数据库
        self.db_mysql = torndb_python3.Connection(**mysql_options)
        self.db_redis = Redis(**redis_options)


def main():
    # 接卸命令行 参数
    tornado.options.parse_command_line()
    if settings.get('debug') !=True:
        options.log_file_prefix=config.log_file_prefix
        options.logging = config.log_level
    """服务器启动文件"""
    app = Application(urls,**settings)
    http_server = HTTPServer(app)
    http_server.listen(options['port'])
    IOLoop.current().start()

if __name__ == '__main__':
    main()