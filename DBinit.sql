-- 删除数据库
drop database ihome;
-- 新建数据库
CREATE DATABASE ihome charset = 'utf8';
-- 使用当前数据库
use ihome;
-- 创建用户表
CREATE TABLE ih_user_profile(
	up_user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
	up_name VARCHAR(32) NOT NULL COMMENT '昵称',
	up_mobile CHAR(11) NOT NULL COMMENT '手机号',
	up_passwd VARCHAR(64) NOT NULL COMMENT '密码',
	up_real_name VARCHAR(32)  NULL COMMENT '真实姓名',
	up_id_card VARCHAR(20)  NULL COMMENT '身份证号',
	up_avatar VARCHAR(128)  NULL COMMENT '用户头像',
	up_admin tinyint  NOT NULL DEFAULT '0' COMMENT '是否是管理员，0-不是，1-是',
	up_utime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP	COMMENT '最后更新时间',
	up_ctime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
	PRIMARY KEY(up_user_id),
	UNIQUE(up_name),
	UNIQUE(up_mobile)
)ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8 COMMENT='用户信息表';
-- 创建房源区域表
CREATE TABLE ih_area_info(
 ai_area_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '区域ID',
 ai_name VARCHAR(32) NOT NULL COMMENT '区域名称',
 ai_ctime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
 PRIMARY KEY (ai_area_id)
)ENGINE = INNODB DEFAULT CHARSET =utf8 COMMENT='房源区域表';
-- 创建房屋信息表
CREATE TABLE ih_house_info (
	hi_house_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '房屋id',
	hi_user_id BIGINT UNSIGNED NOT NULL COMMENT '用户id',
	hi_title VARCHAR ( 64 ) NOT NULL COMMENT '房屋名称',
	hi_price INT UNSIGNED NOT NULL DEFAULT "0" COMMENT '房屋价格，单位分',
	hi_area_id BIGINT UNSIGNED NOT NULL COMMENT '房屋区域id',
	hi_address VARCHAR ( 512 ) NOT NULL DEFAULT '' COMMENT '地址',
	hi_room_count TINYINT UNSIGNED NOT NULL DEFAULT '1' COMMENT '房间数',
	hi_acreage INT UNSIGNED NOT NULL DEFAULT '0' COMMENT '房屋面积',
	hi_house_unit VARCHAR ( 32 ) NOT NULL DEFAULT '' COMMENT '房屋户型',
	hi_capacity INT UNSIGNED NOT NULL DEFAULT '1' COMMENT '容纳人数',
	hi_beds VARCHAR ( 64 ) NOT NULL DEFAULT '' COMMENT '床配置',
	hi_deposit INT UNSIGNED NOT NULL DEFAULT "0" COMMENT '押金，单位分',
	hi_min_days INT UNSIGNED NOT NULL DEFAULT '1' COMMENT '最短入住时间',
	hi_max_days INT UNSIGNED NOT NULL DEFAULT '0' COMMENT '最长入住时间，0-不限制',
	hi_order_count INT UNSIGNED NOT NULL DEFAULT '1' COMMENT '下单数量',
	hi_verify_status TINYINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '审核状态，0-待审核，1-审核未通过，2-审核通过',
	hi_online_status TINYINT UNSIGNED NOT NULL DEFAULT '1' COMMENT '0-下线，1-上线',
	hi_index_image_url VARCHAR ( 256 ) NOT NULL COMMENT '房屋主图片url',
	hi_utime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
	hi_ctime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
	PRIMARY KEY ( hi_house_id ),
	KEY `hi_status` (`hi_verify_status`, `hi_online_status`),
	CONSTRAINT FOREIGN KEY (`hi_user_id`) REFERENCES `ih_user_profile` (`up_user_id`),
   CONSTRAINT FOREIGN KEY (`hi_area_id`) REFERENCES `ih_area_info` (`ai_area_id`)
) ENGINE = INNODB DEFAULT CHARSET = utf8 COMMENT = '房屋信息表';
-- 房屋设置表
CREATE TABLE ih_house_facility  (
	hf_id  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '自增id',
	hf_house_id  BIGINT UNSIGNED NOT NULL COMMENT '房屋id',
	hf_facility_id  INT UNSIGNED NOT NULL COMMENT '房屋设施',
	hf_ctime  datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
	PRIMARY KEY ( hf_id ),
	CONSTRAINT FOREIGN KEY (`hf_house_id`) REFERENCES `ih_house_info` (`hi_house_id`)
) ENGINE = INNODB DEFAULT CHARSET = utf8 COMMENT = '房屋设施表';

-- 设施型录表
CREATE TABLE ih_facility_catelog   (
	fc_id   INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '自增id',
	fc_name   VARCHAR(32)  NOT NULL COMMENT '设施名称',
	fc_ctime   datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
	PRIMARY KEY ( fc_id )
) ENGINE = INNODB DEFAULT CHARSET = utf8 COMMENT = '设施型录表';
-- 订单表
CREATE TABLE ih_order_info (
	oi_order_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '订单id',
	oi_user_id BIGINT UNSIGNED NOT NULL COMMENT '用户id',
	oi_house_id BIGINT UNSIGNED NOT NULL COMMENT '房屋id',
	oi_begin_date date NOT NULL COMMENT '入住时间',
	oi_end_date date NOT NULL COMMENT '离开时间时间',
	oi_days INT UNSIGNED NOT NULL COMMENT '入住天数',
	oi_house_price INT UNSIGNED NOT NULL COMMENT '房屋单价，单位分',
	oi_amount INT UNSIGNED NOT NULL COMMENT '订单金额，单位分',
	oi_status TINYINT UNSIGNED NOT NULL DEFAULT '0' COMMENT '订单状态，0-待接单，1-待支付，2-已支付，3-待评价，4-已完成，5-已取消，6-拒接单',
	oi_comment text NOT NULL COMMENT '订单评论',
	oi_utime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
	oi_ctime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP  COMMENT '创建时间',
	PRIMARY KEY ( oi_order_id ),
	KEY `oi_status` ( oi_status ),
	CONSTRAINT FOREIGN KEY ( `oi_user_id` ) REFERENCES `ih_user_profile` ( `up_user_id` ),
CONSTRAINT FOREIGN KEY ( `oi_house_id` ) REFERENCES `ih_house_info` ( `hi_house_id` )
) ENGINE = INNODB DEFAULT CHARSET = utf8 COMMENT = '订单表';
-- 图片表
CREATE TABLE ih_house_image  (
	hi_image_id  BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '图片id',
	hi_house_id  BIGINT UNSIGNED NOT NULL COMMENT '房屋id',
	hi_url  VARCHAR(256) NOT NULL COMMENT '图片url',
	hi_ctime  datetime NOT NULL DEFAULT CURRENT_TIMESTAMP  COMMENT '创建时间',
	PRIMARY KEY ( hi_image_id ),
 CONSTRAINT FOREIGN KEY (hi_house_id) REFERENCES ih_house_info (hi_house_id)
) ENGINE = INNODB DEFAULT CHARSET = utf8 COMMENT = '房屋图片表';