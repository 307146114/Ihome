PIC_CODE_EXPIRES_SECONDS = 180  # 图片验证码有效期， 单位秒
SMS_CODE_EXPIRES_SECONDS = 300  #手机验证码有效期,  单位秒
SESSION_EXPIRES_SECONDS = 86400 # session数据有效期， 单位秒
QINIU_URL_PREFIX = 'http://qb3m2g5um.bkt.clouddn.com/' # 七牛存储图片的url地址

REDIS_AREA_INFO_EXPIRES_SECONDES = 86400 # redis缓存城区信息的有效期
HOME_PAGE_DATA_REDIS_EXPIRE_SECOND = 86400 # redis首页保存时间
REDIS_HOUSE_INFO_EXPIRES_SECONDES = 86400 # redis缓存房屋信息的有效期
HOME_PAGE_MAX_HOUSES = 5 # 主页房屋展示最大数量



HOUSE_LIST_PAGE_CAPACITY = 3 # 房源列表页每页显示房屋数目
HOUSE_LIST_PAGE_CACHE_NUM = 2 # 房源列表页每次缓存页面书

REDIS_HOUSE_LIST_EXPIRES_SECONDS = 7200 # 列表页数据缓存时间 秒
