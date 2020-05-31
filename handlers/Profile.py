
from handlers.BaseHandler import BaseHandler
from utils import commons
from utils.qiniuUtils import upload 
from utils.response_code import RET
from utils.session import Session
import logging
import constants
class ProfileHandler(BaseHandler):
    # 判断是否登录
    @commons.required_login
    def get(self):
        # 确定登录后 获取session
        data = self.get_current_user()
        if data:
            # 获取session中的手机号
            mobile = data['mobile']
            # 通过手机号查询嘻嘻嘻
            sql ="select up_user_id,up_name,up_avatar FROM ih_user_profile where up_mobile=%(mobile)s"
            try:
                ret = self.db_mysql.get(sql, mobile=mobile)
            except Exception as e:
                # 数据库查询错误
                logging.ERROR(e)
                return self.write(dict(errcode=RET.DBERR,errmsg="get data error"))
            # 判断是头像 是否存在
            if ret['up_avatar']:
                # 存在头像拼接地址(存在七牛上)
                imgurl =constants.QINIU_URL_PREFIX + ret['up_avatar']
            else:
                # 不存在返回
                imgurl = None
            # 返回数据
            return self.write(dict(errcode=RET.OK,data={'name':ret['up_name'],'mobile':mobile,'avatar':imgurl}))

        else:
            return  self.write(dict(errcode=RET.LOGINERR,errmsg="false"))

class AvatarHandler(BaseHandler):
    @commons.required_login
    def post(self):
        avatar = self.request.files.get('avatar')
        if not avatar:
            return self.write(dict(errcode=RET.PARAMERR,errmsg="未上传图片"))
        img = avatar[0]['body']
        try:
            key = upload.upload(img)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.THIRDERR, errmsg="上传失败"))
        data = self.get_current_user()
        user_id = data['user_id']
        sql = 'UPDATE  ih_user_profile SET up_avatar = %(avatar)s where up_user_id=%(user_id)s'
        try:
            self.db_mysql.execute(sql,avatar=key,user_id=user_id)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="保存错误"))
        self.write(dict(errcode=RET.OK, data=constants.QINIU_URL_PREFIX+key))
class NameHandler(BaseHandler):
    @commons.required_login
    def post(self):
        # 获取要修改的用户名
        name = self.json_args.get('name')
        if not name:
            # 判断用户是否正确
            return self.write(dict(errcode=RET.PARAMERR,errmsg="params error"))
        # 获取session.data
        data = self.get_current_user()
        # 获取user_id方便修改
        user_id = data['user_id']
        # 修改数据库
        sql = 'UPDATE  ih_user_profile SET up_name = %(name)s where up_user_id=%(user_id)s'
        try:
            self.db_mysql.execute(sql,name=name,user_id=user_id)
        except Exception as e:
            # 数据修改失败,用户名重复(数据库设置时,用户名是唯一的)
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="name has exist"))
        # 获取session
        session = Session(self)
        # 更改session
        session['name'] = name
        try:
            # 保存修改后的session
            session.save()
        except Exception as e:
            logging.ERROR(e)

        self.write(dict(errcode=RET.OK, errmsg='OK'))

class AuthHandler(BaseHandler):
    @commons.required_login
    def get(self):
        # 获取session.data
        data = self.get_current_user()
        # 获取user_id方便修改
        user_id = data['user_id']
        sql = "SELECT up_real_name,up_id_card FROM ih_user_profile WHERE up_user_id = %(user_id)s"
        try:
            ret = self.db_mysql.get(sql, user_id=user_id)
        except Exception as e:
            # 数据修改失败,用户名重复(数据库设置时,用户名是唯一的)
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="get data failed"))
        if not ret:
            return self.write(dict(errcode=RET.NODATA, errmsg="no data"))
        self.write(dict(errcode=RET.OK,data={'real_name':ret['up_real_name'],'id_card':ret['up_id_card']}))
    @commons.required_login
    def post(self):
        real_name = self.json_args.get('real_name')
        id_card = self.json_args.get('id_card')
        if not all([real_name,id_card]):
            return self.write(dict(errcode=RET.PARAMERR, errmsg="参数异常"))
        # 获取session.data
        data = self.get_current_user()
        # 获取user_id方便修改
        user_id = data['user_id']
        sql = "UPDATE ih_user_profile SET up_real_name = %(real_name)s,up_id_card=%(id_card)s WHERE up_user_id=%(user_id)s"
        try:
             self.db_mysql.execute_rowcount(sql, real_name=real_name,id_card = id_card,user_id=user_id)
        except Exception as e:
            # 数据修改失败,用户名重复(数据库设置时,用户名是唯一的)
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="update failed"))

        self.write(dict(errcode=RET.OK,errmsg='OK'))
