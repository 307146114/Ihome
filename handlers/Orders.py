
from  handlers.BaseHandler import  BaseHandler
from  utils.commons import  required_login
import logging
from utils.response_code import RET
import constants
from datetime import datetime
class MyOrdersHandler(BaseHandler):
    @required_login
    def get(self):
        role = self.get_argument("role", 'custom')
        user_id = self.session.data['user_id']
        if "landlord" ==role:
            sql = "SELECT oi_order_id order_id, oi_status status,oi_ctime ctime,oi_begin_date start_date,oi_end_date end_date,oi_amount amount,oi_days days,oi_comment comment,hi_index_image_url img_url,hi_title title FROM ih_order_info INNER JOIN ih_house_info on oi_house_id = hi_house_id where oi_user_id =%s"
        else:
            sql = "SELECT oi_order_id order_id, oi_status status,oi_ctime ctime,oi_begin_date start_date,oi_end_date end_date,oi_amount amount,oi_days days,oi_comment comment,hi_index_image_url img_url,hi_title title FROM ih_order_info INNER JOIN ih_house_info on oi_house_id = hi_house_id where oi_user_id =%s"
        try:
            ret = self.db_mysql.query(sql, user_id)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR,errmsg="查询订单错误",orders={}))
        if not ret:
            return self.write(dict(errcode=RET.NODATA, errmsg="没有数据", orders={}))
        for order in ret :
            order['ctime'] =order['ctime'].strftime("%Y-%m-%d")
            order['start_date'] =order['start_date'].strftime("%Y-%m-%d")
            order['end_date'] =order['end_date'].strftime("%Y-%m-%d")
            order['img_url'] = constants.QINIU_URL_PREFIX+order['img_url'] if order['img_url'] else ""
        return self.write(dict(errcode=RET.OK, errmsg="OK", orders=ret))

class OrderCommentHandler(BaseHandler):
    @required_login
    def post(self):
        """评论"""
        user_id = self.session.data['user_id']
        comment = self.json_args.get('comment')
        order_id = self.json_args.get('order_id')
        if not all((user_id,comment,order_id)):
            return self.write(dict(errcode=RET.PARAMERR,errmsg="参数错误"))
        sql = "UPDATE ih_order_info SET oi_status = 4 ,oi_comment =%(comment)s where oi_order_id =%(order_id)s and oi_user_id=%(user_id)s"
        try:
            self.db_mysql.execute(sql,comment=comment,order_id=order_id,user_id=user_id)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR,errmsg="数据库操作错误"))
        sql = 'SELECT oi_house_id FROM ih_order_info where oi_order_id =%s'
        try:
            ret = self.db_mysql.get(sql, order_id)
            self.db_redis.delete("house_info_%s" % ret['oi_house_id'])
        except Exception as e:
            logging.ERROR(e)
        #缓存中保存的 房屋详细信息中含有评论,在更新评论后删除房屋的缓存信息

        self.write(dict(errcode=RET.OK, errmsg="ok"))
class AcceptOrderHandler(BaseHandler):
    @required_login
    def post(self):
        """接单"""
        user_id = self.session.data['user_id']
        order_id = self.json_args.get('order_id')
        if not all((user_id,order_id)):
            return self.write(dict(errcode=RET.PARAMERR,errmsg="参数错误"))
        sql = "UPDATE ih_order_info SET oi_status=3 where oi_order_id=%(order_id)s and oi_house_id in (SELECT hi_house_id FROM ih_house_info WHERE hi_user_id = %(user_id)s) and oi_status = 0"
        try:
            self.db_mysql.execute(sql,order_id=order_id,user_id=user_id)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR,errmsg="数据库操作错误"))

        self.write(dict(errcode=RET.OK, errmsg="ok"))
class RejectOrderHandler(BaseHandler):
    @required_login
    def post(self):
        """拒单"""
        user_id = self.session.data['user_id']
        order_id = self.json_args.get('order_id')
        reject_reason = self.json_args.get('reject_reason')
        if not all((user_id,order_id,reject_reason)):
            return self.write(dict(errcode=RET.PARAMERR,errmsg="参数错误"))
        sql = "UPDATE ih_order_info SET oi_status=6,oi_comment =%(reject_reason)s where oi_order_id=%(order_id)s and oi_house_id in (SELECT hi_house_id FROM ih_house_info WHERE hi_user_id = %(user_id)s) and oi_status = 0"
        try:
            self.db_mysql.execute(sql,reject_reason=reject_reason,order_id=order_id,user_id=user_id)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR,errmsg="数据库操作错误"))

        self.write(dict(errcode=RET.OK, errmsg="ok"))

class OrderHandler(BaseHandler):
    @required_login
    def post(self):
        """提交订单"""
        user_id = self.session.data['user_id']
        house_id = self.json_args.get('house_id')
        start_date = self.json_args.get('start_date')
        end_date = self.json_args.get('end_date')
        if  not all((house_id,start_date,end_date)):
            return self.write(dict(errcode=RET.PARAMERR,errmsg="参数错误"))
        sql = "SELECT hi_price ,hi_user_id FROM ih_house_info where hi_house_id = %s"
        try:
            house = self.db_mysql.get(sql, house_id)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询房屋出错"))

        if not house:
            return self.write(dict(errcode=RET.NODATA, errmsg="房屋不存在"))
        # if house['hi_user_id']==user_id:
        #     return self.write(dict(errcode=RET.PARAMERR, errmsg="自己房屋不能下单"))
        days = (datetime.strptime(end_date, "%Y-%m-%d") -datetime.strptime(start_date, "%Y-%m-%d")).days+1
        if days<=0:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="入住的天数异常"))
        amount = days * house["hi_price"]
        # 确保用户预订的时间内，房屋没有被别人下单
        try:
            ret = self.db_mysql.get("select count(*) counts from ih_order_info where oi_house_id=%(house_id)s and oi_begin_date<%(end_date)s and oi_end_date>%(start_date)s",
                              house_id=house_id, end_date=end_date, start_date=start_date)
        except Exception as e:
            logging.error(e)
            return self.write({"errcode": RET.DBERR, "errmsg": "get date error"})
        if ret['counts']>0:
            return self.write({"errcode": RET.PARAMERR, "errmsg": "房间已预订了"})

        try:
            self.db_mysql._db.begin()
            # 保存订单数据ih_order_info，
            self.db_mysql.execute("INSERT INTO ih_order_info(oi_user_id,oi_house_id,oi_begin_date,oi_end_date,oi_days,oi_house_price,oi_amount) VALUES(%(user_id)s,%(house_id)s,%(begin_date)s,%(end_date)s,%(days)s,%(price)s,%(amount)s);",user_id=user_id, house_id=house_id, begin_date=start_date, end_date=end_date, days=days, price=house["hi_price"], amount=amount)
            self.db_mysql.execute("UPDATE ih_house_info SET hi_order_count=hi_order_count+1 where hi_house_id=%(house_id)s;",house_id=house_id)
            self.db_mysql._db.commit()
        except Exception as e:
            logging.error(e)
            self.db_mysql._db.rollback()
            return self.write({"errcode":RET.DBERR, "errmsg":"save data error"})
        self.write({"errcode":RET.OK, "errmsg":"OK"})

