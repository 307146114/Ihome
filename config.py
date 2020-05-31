import os
settings =dict (
    debug=True,
    static_path = os.path.join(os.path.dirname(__file__),'static'),
    # template_path = os.path.join(os.path.dirname(__file__),'static'),
    cookie_secret="6wQ9cOJAR6KXxlz/wGA9NQpLQh4PM08YrsLhtekhtgk=",
    xsrf_cooikes = True
)
mysql_options=dict (
    host = "192.168.163.135",
    user = "root",
    password = "root",
    database = "ihome"
)
redis_options=dict (
    host = "192.168.163.135",
    port = 6379,
    # python特殊属性  否则取出额是bytes
    decode_responses=True
)
# 日志配置
log_path = os.path.join(os.path.dirname(__file__), "logs/log")
log_level = "debug"
# 密码加密密钥
passwd_hash_key = "nlgCjaTXQX2jpupQFQLoQo5N4OkEmkeHsHD9+BBx2WQ="
