import random
from  handlers.BaseHandler import BaseHandler
from utils.captcha.captcha import Captcha
from constants import PIC_CODE_EXPIRES_SECONDS,SMS_CODE_EXPIRES_SECONDS
from utils.response_code import RET,error_map
from libs.yuntongxun.SendTemplateSMS import CCP
import  logging
import re


class PicCodeHandler(BaseHandler):
    def get(self):
        # 获取上次保存的图片的id
        pre = self.get_argument('pre')
        # 获取本次要保存的图片id
        cur = self.get_argument('cur')
        # print("pre%s------"%pre)
        # print("cur%s-------"%cur)

        # print(Captcha.instance().generate_captcha())
        # 获取一个验证码
        imageName,text,imge = Captcha.instance().generate_captcha()
        try:
            if pre:
                self.db_redis.delete(pre)
            self.db_redis.setex("imge_code_%s"%cur,PIC_CODE_EXPIRES_SECONDS,text)
        except Exception as e:
            logging.ERROR(e)
            return self.write("")
        else:
            self.set_header("Content-Type","image/jpg")
            self.write(imge)
class SMSCodeHandler(BaseHandler):
    def post(self):
        # 获取图片验证码
        imageCode = self.json_args.get('piccode')
        # 获取本次要保存的图片id
        imageCodeId = self.json_args.get('piccode_id')
        mobile = self.json_args.get('mobile')
        # 判断图片验证码\图片id\手机号是否接收完全
        if imageCode and imageCodeId and mobile:
            # 使用正则判断手机号 格式
            if not re.match(r'^1\d{10}$',mobile):
                return self.write(dict(errcode=RET.PARAMERR, errmsg="手机格式不对"))
            try:
                # 从redis数据库中取出图片id对应的验证码
                text = self.db_redis.get("imge_code_%s"%imageCodeId)
            except Exception as e:
                logging.ERROR(e)
                return self.write(dict(errcode=RET.DBERR, errmsg="查询数据库出错"))
            if not text:
                # 没有取到  就是过期了
                return self.write(dict(errcode=RET.NODATA, errmsg="查询验证码过期"))
            try:
                # 删除图片id对应的验证码
                self.db_redis.delete("imge_code_%s"%imageCodeId)
            except Exception as e:
                logging.ERROR(e)
                # 比较填写的验证码与数据保存的验证码是否一致
            if imageCode.lower() != text.lower():
                return self.write(dict(errcode=RET.DATAERR, errmsg="验证码错误"))
            # 查询数据库中的电话,看电话是否重复
            sql = "SELECT COUNT(up_user_id) counts FROM ih_user_profile where up_mobile =%s"
            try:
                # 使用get方法  只取第一条即可(因为使用了count 只有一条)
                ret = self.db_mysql.get(sql, mobile)
            except Exception as e:
                logging.ERROR(e)
                # 判断是否已注册过
            if 0!=ret['counts']:
                return self.write(dict(errcode=RET.DATAEXIST, errmsg="手机号已注册"))
            # 发送手机验证码
            ccp = CCP()
            # 1代表模板ID，下载SDK的官网api文档有说明
            # 这里填测试号码 免费发送短信  填的不是测试号码收短信费用
            # 创建一个手机验证码(6位)  取随机数
            sms_code = "%06d" % random.randint(1, 1000000)
            try:
                # 将手机验证码保存到数据库
                self.db_redis.setex("sms_code_%s" % mobile,SMS_CODE_EXPIRES_SECONDS,sms_code )
            except Exception as e:
                logging.ERROR(e)
                return self.write(dict(errcode=RET.DBERR, errmsg="数据库出错"))
            try:
                # 发送书记验证码
                result = ccp.send_Template_sms(mobile, [sms_code, SMS_CODE_EXPIRES_SECONDS/60], 1)
            except Exception as e:
                logging.ERROR(e)
                return self.write(dict(errcode=RET.THIRDERR, errmsg="发送短信失败"))
            if result:
                self.write(dict(errcode=RET.OK, errmsg="发送成功"))
            else:
                self.write(dict(errcode=RET.UNKOWNERR, errmsg="发送失败"))


        else:
            # 判断图片验证码\图片id\手机号接收不完全
            self.write(dict(errcode = RET.DATAERR, errmsg=error_map[RET.PARAMERR]))






