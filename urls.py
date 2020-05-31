import handlers.IndexHandler
from handlers import  Passport,VerifyCode,Profile
from handlers.BaseHandler import StaticFileHandler
import os
urls =[
    # (r"/",handlers.IndexHandler.IndexHandler)
    (r"/api/register", Passport.RegisterHandler), #注册
    (r"/api/login", Passport.LogHandler),#登录
    (r"/api/check_login", Passport.CheckLoginHandler),  # 判断用户是否登录
    (r"/api/logout", Passport.LogoutHandler),  # 判断用户是否登录
    (r"/api/piccode", VerifyCode.PicCodeHandler),#获取图片验证码
    (r"/api/smscode", VerifyCode.SMSCodeHandler),# 发送手机验证码
    (r"/api/profile", Profile.ProfileHandler),# 获取用户信息
    (r"/api/profile/avatar", Profile.AvatarHandler),# 用户上传头像
    (r"/api/profile/name", Profile.NameHandler),# 修改个人主页的用户名
    (r"/api/profile/auth", Profile.AuthHandler), # 实名认证
    (r"/(.*)",StaticFileHandler,dict(path = os.path.join(os.path.dirname(__file__),'html'),default_filename='index.html')),
]