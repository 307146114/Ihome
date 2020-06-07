

from handlers.BaseHandler import BaseHandler
from utils.response_code import RET
from constants import REDIS_AREA_INFO_EXPIRES_SECONDES, QINIU_URL_PREFIX, HOME_PAGE_MAX_HOUSES, HOME_PAGE_DATA_REDIS_EXPIRE_SECOND,HOUSE_LIST_PAGE_CAPACITY,HOUSE_LIST_PAGE_CACHE_NUM,REDIS_HOUSE_LIST_EXPIRES_SECONDS,REDIS_HOUSE_INFO_EXPIRES_SECONDES
from utils.commons import required_login
from utils.qiniuUtils import upload
import logging
import json
import math
class AreaInfoHandler(BaseHandler):
    def get(self):
        try:
            are_info = self.db_redis.get("area_info")
        except  Exception as e:
            logging.ERROR(e)
            are_info = None
        if are_info:
            return self.write('{"errcode":"0", "errmsg":"OK", "data":%s}'%are_info)
        sql = "SELECT ai_area_id area_id,ai_name name FROM ih_area_info;"
        try:
            ret = self.db_mysql.query(sql)
            print(type(ret))
            print(json.dumps(ret))
        except  Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR,errmsg="查询数据库错误"))
        if not ret:
            return self.write(dict(errcode=RET.NODATA, errmsg="没有数据"))
        try:
            self.db_redis.setex('area_info',REDIS_AREA_INFO_EXPIRES_SECONDES,json.dumps(ret))
        except  Exception as e:
            logging.ERROR(e)
        # area_id name
        return self.write(dict(errcode=RET.OK, errmsg="OK",data=ret))

class MyHousesHandler(BaseHandler):
    @required_login
    def get(self):
        """
        获取本人的房源信息
        :return:
        """
        user_id = self.session.data['user_id']
        sql  = "SELECT a.hi_house_id,a.hi_title,a.hi_price,a.hi_ctime,b.ai_name,a.hi_index_image_url from ih_house_info a LEFT JOIN ih_area_info b ON a.hi_area_id =b.ai_area_id WHERE a.hi_user_id = %s"
        try:
            ret = self.db_mysql.query(sql, user_id)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询数据库错误",houses=None))
        if not ret:
            return self.write(dict(errcode=RET.NODATA, errmsg="没有数据",houses=None))
        houses = []
        for house in ret:
            if house.get('hi_index_image_url'):
                img_url = QINIU_URL_PREFIX +house.get('hi_index_image_url')
            else:
                img_url = ""
            info = {
                'house_id':house['hi_house_id'],
                'title':house['hi_title'],
                'img_url':img_url,
                'area_name':house['ai_name'],
                'price':house['hi_price'],
                'ctime':house['hi_ctime'].strftime("%Y-%m-%d"),
            }
            houses.append(info)

        self.write(dict(errcode=RET.OK, errmsg="OK", houses=houses))

class HouseInfoHandler(BaseHandler):
    @required_login
    def get(self):
        """
        获取房屋详细信息
        :return:
        """
        user_id = self.session.data.get('user_id',-1)
        house_id = self.get_argument("house_id")
        # print(house_id)
        if not house_id:
            return self.write(dict(errcode = RET.PARAMERR,errmsg="缺少参数"))
        try:
            house = self.db_redis.get("house_info_%s" % house_id)
        except Exception as e:
            logging(e)
            house=None
        if house:
            return self.write(dict(errcode=RET.OK, errmsg="OK", data=json.loads(house)))
        user_id = self.session.data['user_id']
        try:
            sql = "SELECT a.hi_title,a.hi_address,a.hi_room_count,a.hi_acreage,a.hi_house_unit,a.hi_capacity,a.hi_beds,a.hi_deposit,a.hi_min_days,a.hi_max_days,a.hi_price,a.hi_user_id,b.up_avatar,b.up_name from ih_house_info a LEFT JOIN ih_user_profile b on a.hi_user_id = b.up_user_id WHERE hi_house_id = %s"
            house_info = self.db_mysql.get(sql, house_id)
            if not house_info:
                return self.write(dict(errcode=RET.NODATA, errmsg="没有数据", data=None))
            sql ="SELECT hf_facility_id FROM ih_house_facility where hf_house_id =%s"
            facilitys = self.db_mysql.query(sql, house_id)
            house={
                'title':house_info['hi_title'],
                'user_avatar':QINIU_URL_PREFIX +house_info['up_avatar'],
                'user_name':house_info['up_name'],
                'address':house_info['hi_address'],
                'room_count':house_info['hi_room_count'],
                'acreage':house_info['hi_acreage'],
                'unit':house_info['hi_house_unit'],
                'capacity':house_info['hi_capacity'],
                'beds': house_info['hi_beds'],
                'deposit':house_info['hi_deposit'],
                'min_days':house_info['hi_min_days'],
                'max_days':house_info['hi_max_days'],
                'price':house_info['hi_price'],
                'user_id':house_info['hi_user_id']

            }
            urls=[]
            sql = "select hi_url from ih_house_image where hi_house_id=%s"
            try:
                rets = self.db_mysql.query(sql, house_id)
                if  rets :
                    for ret in rets:
                        urls.append(QINIU_URL_PREFIX+ret['hi_url'])
            except Exception as e:
                logging.ERROR(e)
            house['images'] = urls
            faci=[]
            if  facilitys:
                for facility in facilitys:
                    faci.append(facility['hf_facility_id'])
                house['facilities'] = faci
            else:
                house['facilities'] =""
            sql = "SELECT o.oi_comment,u.up_name,o.oi_utime,u.up_mobile from ih_order_info o INNER JOIN ih_user_profile u  on  o.oi_user_id= u.up_user_id WHERE o.oi_house_id = %s"

            try:
                querys = self.db_mysql.query(sql, house_id)

            except Exception as e:
                logging.ERROR(e)
            comments = []
            if querys:
                for query in querys:
                    comment = {}
                    comment['user_name'] = query['up_name']
                    comment['ctime'] = query['oi_utime'].strftime("%Y-%m-%d")
                    comment['content'] = query['oi_comment']
                    comments.append(comment)
            house['comments'] = comments
            try:
                self.db_redis.setex("house_info_%s" % house_id,REDIS_HOUSE_INFO_EXPIRES_SECONDES,
                                 json.dumps(house))
            except Exception as e:
                logging.error(e)
            return self.write(dict(errcode=RET.OK, errmsg="OK", data=house))
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode = RET.DBERR, errmsg="数据库查询失败", data=None))


    @required_login
    def post(self):
        """
         {"title":"111","price":"111","area_id":"1","address":"1111","room_count":"111","acreage":"111","unit":"1111","capacity":"1111","beds":"111","deposit":"111","min_days":"11","max_days":"11","facility":[]}
        :return:
        """
        """
        acreage: "1000"
        address: "地址：东城区-----asdlkjas"
        area_id: "1"
        beds: "2*1.8*1"
        capacity: "3"
        deposit: "100"
        facility: []
        max_days: "3"
        min_days: "1"
        price: "100"
        room_count: "6"
        title: "test房屋"
        unit: "三室两厅"
        """
        user_id = self.session.data['user_id']
        title = self.json_args.get('title')
        price = self.json_args.get('price')
        area_id = self.json_args.get('area_id')
        address = self.json_args.get('address')
        room_count = self.json_args.get('room_count')
        unit = self.json_args.get('unit')
        capacity = self.json_args.get('capacity')
        beds = self.json_args.get('beds')
        deposit = self.json_args.get('deposit')
        min_days = self.json_args.get('min_days')
        max_days = self.json_args.get('max_days')
        facilitys = self.json_args.get('facility')
        if not all([title,price,area_id,address,room_count,unit,capacity,beds,deposit,min_days,max_days,facilitys]):
            return self.write(dict(errcode=RET.PARAMERR,errmsg="参数错误"))
        try:
            price = int(price)*100
            deposit = int(deposit)*100
        except Exception as e:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="price,deposit参数类型有错误"))
        print(room_count)
        mm = "INSERT INTO ih_house_info(hi_user_id,hi_title,hi_price,hi_area_id,hi_address,hi_room_count,hi_house_unit,hi_capacity,hi_beds,hi_deposit,hi_min_days,hi_max_days) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"%(user_id,title,price,area_id,address,room_count,unit,capacity,beds,deposit,min_days,max_days)
        print(mm)
        sql  = "INSERT INTO ih_house_info(hi_user_id,hi_title,hi_price,hi_area_id,hi_address,hi_room_count,hi_house_unit,hi_capacity,hi_beds,hi_deposit,hi_min_days,hi_max_days) VALUES(%(user_id)s,%(title)s,%(price)s,%(area_id)s,%(address)s,%(room_count)s,%(unit)s,%(capacity)s,%(beds)s,%(deposit)s,%(min_days)s,%(max_days)s)"
        self.db_mysql._db.begin()

        try:
            house_id = self.db_mysql.execute(sql,user_id=user_id,title=title,price=price,area_id=area_id,address=address,room_count=room_count,unit=unit,capacity=capacity,beds=beds,deposit=deposit,min_days=min_days,max_days=max_days)
            sql = "INSERT INTO ih_house_facility(hf_house_id,hf_facility_id) VALUES"
            sql_info=[]
            args = []
            for facility in facilitys:
                sql_info.append("(%s,%s)")
                args.append(house_id)
                args.append(facility)
            sql +=",".join(sql_info)

            self.db_mysql.execute(sql,*tuple(args))
            self.db_mysql._db.commit()
            return self.write(dict(errcode=RET.OK, errmsg="OK", house_id=house_id))
        except Exception as e:
            logging.ERROR(e)
            self.db_mysql._db.rollback()
            return self.write(dict(errcode=RET.DBERR, errmsg="操作数据库错误", houses=None))


class HouseImageHandler(BaseHandler):
    @required_login
    def post(self):
        hose_id = self.get_argument('house_id')
        img_files = self.request.files['house_image']
        if not img_files:
            return self.write(dict(errcode=RET.PARAMERR, errmsg="请上传图片"))

        img = img_files[0]['body']
        try:
            img_key = upload.upload(img)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.THIRDERR, errmsg="上传失败"))
        sql  = "INSERT INTO  ih_house_image(hi_house_id,hi_url) VALUES(%s,%s);" \
               "UPDATE ih_house_info SET hi_index_image_url = %s where hi_house_id = %s and hi_index_image_url is null;"
        try:
            self.db_mysql.execute(sql,hose_id,img_key,img_key,hose_id)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="保存图片"))
        return self.write(dict(errcode=RET.OK, errmsg="OK",url=QINIU_URL_PREFIX+img_key))

class IndexHandler(BaseHandler):
    def get(self):
        """获取首页数据包括地址"""
        try:
           are_info = self.db_redis.get('area_info')
        except Exception as e:
            logging.ERROR(e)
            areas = None
        if are_info:
            areas =are_info
        sql = "SELECT ai_area_id area_id,ai_name name FROM ih_area_info;"
        try:
            areas = self.db_mysql.query(sql)
        except  Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询数据库错误"))
        if not areas:
            return self.write(dict(errcode=RET.NODATA, errmsg="没有数据"))
        try:
            self.db_redis.setex('area_info', REDIS_AREA_INFO_EXPIRES_SECONDES, json.dumps(areas))
        except  Exception as e:
            logging.ERROR(e)

        try:
            ret = self.db_redis.get('home_page_data')
        except Exception as e:
            logging.ERROR(e)
        if ret:
            return self.write(dict(errcode=RET.OK, errmsg="OK", houses=json.loads(ret), areas=areas))

        sql = "select hi_house_id house_id, hi_index_image_url img_url,hi_title title  from ih_house_info ORDER BY hi_ctime DESC LIMIT %s"
        try:
            ret = self.db_mysql.query(sql, HOME_PAGE_MAX_HOUSES)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询房屋出错",houses=None))
        if not ret:
            return self.write(dict(errcode=RET.NODATA, errmsg="没有数据", houses=None,areas=areas))
        for house in ret:
            house['img_url'] = QINIU_URL_PREFIX+house['img_url'] if house['img_url']else""
        try :
            self.db_redis.setex("home_page_data",HOME_PAGE_DATA_REDIS_EXPIRE_SECOND,json.dumps(ret))
        except Exception as e:
            logging.ERROR(e)
        return self.write(dict(errcode=RET.OK, errmsg="OK", houses=ret,areas=areas))
class HouseListHandler(BaseHandler):
    def get(self):
        """ 筛选数据库 未使用缓存"""
        aid = self.get_argument('aid',"")
        startDate = self.get_argument('sd',"")
        endDate = self.get_argument('ed',"")
        sk = self.get_argument('sk','new')
        page = self.get_argument('p',1)
        sql ="SELECT DISTINCT h.hi_house_id house_id,h.hi_index_image_url image_url,h.hi_price price,h.hi_title title,h.hi_room_count room_count,h.hi_order_count order_count,h.hi_address address,u.up_avatar avatar,h.hi_ctime ctime from ih_house_info h LEFT JOIN ih_order_info o on h.hi_house_id = o.oi_house_id INNER JOIN ih_user_profile u ON h.hi_user_id = u.up_user_id"
        sql_total_count ="SELECT count(DISTINCT h.hi_house_id)  count from ih_house_info h LEFT JOIN ih_order_info o on h.hi_house_id = o.oi_house_id"
        sql_where = []  # 用来保存sql语句的where条件
        sql_params = {}  # 用来保存sql查询所需的动态数据
        if aid:
            sql_where.append("h.hi_area_id = %(aid)s")
            sql_params['aid'] = aid
        if startDate and endDate:
            sql_where.append("((o.oi_end_date<%(startDate)s and o.oi_begin_date>%(endDate)s) or ( oi_begin_date is null and oi_end_date is null))")
            sql_params['startDate'] = startDate
            sql_params['endDate'] = endDate
        elif startDate:
            sql_where.append("((o.oi_end_date<%(startDate)s) or ( oi_begin_date is null and oi_end_date is null))")
            sql_params['startDate'] = startDate
        elif endDate:
            sql_where.append("(o.oi_begin_date>%(endDate)s) or ( oi_begin_date is null and oi_end_date is null))")
            sql_params['endDate'] = endDate
        if sql_where:
            sql += " where " + " and ".join(sql_where)
            sql_total_count += " where " + " and ".join(sql_where)

        try:
            ret = self.db_mysql.get(sql_total_count, **sql_params)
        except Exception as e:
            logging.ERROR(e)
            total_page = -1
        else:
            total_page = int(math.ceil(ret['count']/float(HOUSE_LIST_PAGE_CAPACITY)))
        page = int(page)
        if page>total_page:
            return self.write(dict(errcode=RET.OK,errmsg="OK",data=[],total_page=total_page))
        if sk == 'new':
            sql += " order by h.hi_ctime desc"
        elif "booking" == sk: # 最受欢迎
            sql += " ORDER BY h.hi_order_count desc"
        elif "price" == sk: # 价格有低到高
            sql += " ORDER BY h.hi_price asc"
        elif "price-des" == sk: # 价格有高到低
            sql += " ORDER BY h.hi_price desc"

        if 1==page:
            sql +=" LIMIT %s" %HOUSE_LIST_PAGE_CAPACITY
        else:
            sql += " LIMIT %s,%s" %((page-1)*HOUSE_LIST_PAGE_CAPACITY,HOUSE_LIST_PAGE_CAPACITY)
        try:
            ret = self.db_mysql.query(sql, **sql_params)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询房屋错误", data=[], total_page=total_page))
        if not ret:
            return self.write(dict(errcode=RET.NODATA, errmsg="没有数据", data=[], total_page=total_page))
        for house in ret:
            house['ctime'] = house['ctime'].strftime("%Y-%m-%d")
        return self.write(dict(errcode=RET.OK, errmsg="OK", data=ret, total_page=total_page))
class HouseListRedisHandler(BaseHandler):
    def get(self):
        """ 筛选数据库 使用缓存"""
        aid = self.get_argument('aid', "")
        startDate = self.get_argument('sd', "")
        endDate = self.get_argument('ed', "")
        sk = self.get_argument('ed', 'new')
        page = self.get_argument('p', 1)
        redis_keys = "houses_%s_%s_%s_%s" % (startDate, endDate, aid, sk)
        try:
            ret = self.db_redis.hget(redis_keys,page)
        except Exception as e:
            logging.ERROR(e)
        if ret:
            return self.write(ret)

        sql = "SELECT DISTINCT h.hi_house_id house_id,h.hi_index_image_url image_url,h.hi_price price,h.hi_title title,h.hi_room_count room_count,h.hi_order_count order_count,h.hi_address address,u.up_avatar avatar,h.hi_ctime ctime from ih_house_info h LEFT JOIN ih_order_info o on h.hi_house_id = o.oi_house_id INNER JOIN ih_user_profile u ON h.hi_user_id = u.up_user_id"
        sql_total_count = "SELECT count(DISTINCT h.hi_house_id)  count from ih_house_info h LEFT JOIN ih_order_info o on h.hi_house_id = o.oi_house_id"
        sql_where = []  # 用来保存sql语句的where条件
        sql_params = {}  # 用来保存sql查询所需的动态数据
        if aid:
            sql_where.append("h.hi_area_id = %(aid)s")
            sql_params['aid'] = aid
        if startDate and endDate:
            sql_where.append(
                "((o.oi_end_date<%(startDate)s and o.oi_begin_date>%(endDate)s) or ( oi_begin_date is null and oi_end_date is null))")
            sql_params['startDate'] = startDate
            sql_params['endDate'] = endDate
        elif startDate:
            sql_where.append("((o.oi_end_date<%(startDate)s) or ( oi_begin_date is null and oi_end_date is null))")
            sql_params['startDate'] = startDate
        elif endDate:
            sql_where.append("(o.oi_begin_date>%(endDate)s) or ( oi_begin_date is null and oi_end_date is null))")
            sql_params['endDate'] = endDate
        if sql_where:
            sql += " where " + " and ".join(sql_where)
            sql_total_count += " where " + " and ".join(sql_where)

        try:
            ret = self.db_mysql.get(sql_total_count, **sql_params)
        except Exception as e:
            logging.ERROR(e)
            total_page = -1
        else:
            total_page = int(math.ceil(ret['count'] / float(HOUSE_LIST_PAGE_CAPACITY)))
        page = int(page)
        if page > total_page:
            return self.write(dict(errcode=RET.OK, errmsg="OK", data=[], total_page=total_page))
        if sk == 'new':
            sql += " order by h.hi_ctime desc"
        elif "booking" == sk:  # 最受欢迎
            sql += " ORDER BY h.hi_order_count desc"
        elif "price" == sk:  # 价格有低到高
            sql += " ORDER BY h.hi_price asc"
        elif "price-des" == sk:  # 价格有高到低
            sql += " ORDER BY h.hi_price desc"

        if 1 == page:
            sql += " LIMIT %s" % HOUSE_LIST_PAGE_CAPACITY
        else:
            sql += " LIMIT %s,%s" % ((page - 1) * HOUSE_LIST_PAGE_CAPACITY, HOUSE_LIST_PAGE_CAPACITY*HOUSE_LIST_PAGE_CACHE_NUM)
        try:
            ret = self.db_mysql.query(sql, **sql_params)
        except Exception as e:
            logging.ERROR(e)
            return self.write(dict(errcode=RET.DBERR, errmsg="查询房屋错误", data=[], total_page=total_page))
        if not ret:
            return self.write(dict(errcode=RET.NODATA, errmsg="没有数据", data=[], total_page=total_page))
        for house in ret:
            house['ctime'] = house['ctime'].strftime("%Y-%m-%d")
            house['image_url'] = QINIU_URL_PREFIX+house['image_url'] if house['image_url'] else ""
            house['avatar'] = QINIU_URL_PREFIX+house['avatar'] if house['avatar'] else ""
        cur_ret = ret[:HOUSE_LIST_PAGE_CAPACITY]
        house_data ={}
        house_data[page] = json.dumps(dict(errcode=RET.OK, errmsg="OK", data=cur_ret, total_page=total_page))
        count = 1
        while 1:
            next_ret = ret[count * HOUSE_LIST_PAGE_CAPACITY:(count + 1) * HOUSE_LIST_PAGE_CACHE_NUM]
            if not next_ret:
                break
            house_data[page+1] = json.dumps(dict(errcode=RET.OK, errmsg="OK", data=next_ret, total_page=total_page))
        redis_keys = "houses_%s_%s_%s_%s" % (startDate, endDate, aid, sk)
        self.db_redis.hmset(redis_keys, house_data)
        self.db_redis.expire(redis_keys,REDIS_HOUSE_LIST_EXPIRES_SECONDS)
        return self.write(dict(errcode=RET.OK, errmsg="OK", data=cur_ret, total_page=total_page))