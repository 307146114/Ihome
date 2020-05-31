
import uuid
import logging
import json
from  constants import SESSION_EXPIRES_SECONDS
class Session(object):
    def __init__(self,requestHandler):
        # 设置handler 方便修改cookie 和操作数据库
        self.requestHandler = requestHandler
        # 从cookie中获取session_id
        self.see_id = self.requestHandler.get_secure_cookie('session_id')
        # 没有session_id 新重建一个session_id
        if not self.see_id:
            self.see_id = uuid.uuid4().hex
            # 新创建的session_id 为{}
            self.data = {}
            self.requestHandler.set_secure_cookie('session_id',self.see_id)
        else:
            # 已经存在session_id
            try:
                # 从数据库中查询保存在信息
                data = self.requestHandler.db_redis.get("see_id_%s"%self.see_id)
            except  Exception as e:
                logging.ERROR(e)
                raise Exception('查询数据出错了')
            # 如果没有查询到数据
            if not data:
                self.data = {}
            else:
                # 查询到数据将数据转成json格式
                self.data = json.loads(data)

    def save(self):
        """
            向数据库写入json数据
        :return:
        """
        # 将json转成字符串
        json_str = json.dumps(self.data)
        try:
            # 写入接送 有效期是一天
            data = self.requestHandler.db_redis.setex("see_id_%s"%self.see_id,SESSION_EXPIRES_SECONDS,json_str)
        except  Exception as e:
            logging.ERROR(e)
            raise Exception('查询数据输错了')
    def clear(self):
        """
            清除保存的session信息
        :return:
        """
        try:
            # 清除数据库信息
            data = self.requestHandler.db_redis.delete("see_id_%s"%self.see_id)
        except  Exception as e:
            logging.ERROR(e)
        # 清除cookie
        self.requestHandler.clear_cookie('session_id')

