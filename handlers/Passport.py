import config
from  handlers.BaseHandler import BaseHandler
from  utils.response_code import RET
from utils.session import Session
from utils import commons
import logging
import re
import hashlib

class RegisterHandler(BaseHandler):


    def post(self):
        """
        注册账号
        :return:
        """
        mobile = self.json_args.get('mobile')
        phonecode = self.json_args.get('phonecode')
        password = self.json_args.get('password')
        print('=='*50)
        print(phonecode)
        print('=='*50)
        # 判断图片验证码\图片id\手机号是否接收完全
        if phonecode and password and mobile:
            try:
                # 从redis数据库中取出图片id对应的验证码
                phton_text = self.db_redis.get("sms_code_%s" % mobile)
            except Exception as e:
                logging.ERROR(e)
                return self.write(dict(errcode=RET.DBERR, errmsg="查询数据库出错"))
            if not phton_text:
                # 没有取到  就是过期了
                return self.write(dict(errcode=RET.NODATA, errmsg="查询验证码过期"))

            if phton_text != phonecode:
                return self.write(dict(errcode=RET.DATAERR, errmsg="手机验证码错误"))
            try:
                # 删除手机验证码
                self.db_redis.delete("sms_code_%s" % mobile)
            except Exception as e:
                logging.ERROR(e)

            # 添加用户名
            sql = "INSERT INTO ih_user_profile(up_name,up_mobile,up_passwd) VALUES(%(name)s,%(mobile)s,%(passwd)s);"

            try:
                user_id = self.db_mysql.execute(sql, name=mobile, mobile=mobile, passwd=hashlib.sha256((password+config.passwd_hash_key).encode('utf8')).hexdigest())
            except Exception as e:
                logging.ERROR(e)
                return self.write(dict(errcode=RET.DATAEXIST, errmsg="手机已存在"))
            session = Session(self)
            session.data['user_id'] = user_id
            session.data['mobile'] = mobile
            session.data['name'] = mobile
            session.save()
            try:
                session.save()
            except Exception as e:
                logging.ERROR(e)
            return self.write(dict(errcode=RET.OK, errmsg="注册成功"))




class LogHandler(BaseHandler):


    def post(self):
        mobile = self.json_args.get("mobile")
        password = self.json_args.get("password")
        if all([mobile,password]):
            # 使用正则判断手机号 格式
            if not re.match(r'^1\d{10}$', mobile):
                return self.write(dict(errcode=RET.PARAMERR, errmsg="手机格式不对"))
            sql = "select up_user_id,up_name FROM ih_user_profile where up_passwd = %(passwd)s and up_mobile = %(mobile)s"
            password =hashlib.sha256((password+config.passwd_hash_key).encode('utf8')).hexdigest()
            try:
                ret = self.db_mysql.get(sql, passwd=password, mobile=mobile)
            except Exception as e:
                logging.ERROR(e)
                return  self.write(dict(errcode = RET.DBERR , errmsg="数据库查询错误"))
            if not ret:
                return self.write(dict(errcode=RET.LOGINERR , errmsg="账号或密码错误"))
            session = Session(self)
            session.data['user_id'] = ret['up_user_id']
            session.data['mobile'] = mobile
            session.data['name'] = ret['up_name']
            session.save()
            self.write(dict(errcode=RET.OK, errmsg='OK'))

        else:
            self.write(dict(errcode = RET.PARAMERR, errmsg="传递参数不正确"))
            
            
class CheckLoginHandler(BaseHandler):
    @commons.required_login
    def get(self):
        data = self.get_current_user()
        if data:
            self.write(dict(errcode=RET.OK,data={'name':data['name']}))
        else:
            self.write(dict(errcode=RET.SESSIONERR,errmsg="false"))
class LogoutHandler(BaseHandler):
    @commons.required_login
    def get(self):
        session = Session(self)
        session.clear()
        self.write(dict(errcode=RET.OK, errmsg="退出成功"))
        