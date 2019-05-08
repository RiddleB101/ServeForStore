create schema if not exists product_db collate utf8mb4_general_ci;

create table if not exists app_access_log
(
	id int auto_increment
		primary key,
	uid bigint default 0 not null comment 'uid',
	referer_url varchar(255) default '' not null comment '当前访问的refer',
	target_url varchar(255) default '' not null comment '访问的url',
	query_params text not null comment 'get和post参数',
	ua varchar(255) default '' not null comment '访问ua',
	ip varchar(32) default '' not null comment '访问ip',
	note varchar(1000) default '' not null comment 'json格式备注字段',
	created_time timestamp default CURRENT_TIMESTAMP not null
)
comment '用户访问记录表';

create index idx_uid
	on app_access_log (uid);

create table if not exists app_error_log
(
	id int(11) unsigned auto_increment
		primary key,
	referer_url varchar(255) default '' not null comment '当前访问的refer',
	target_url varchar(255) default '' not null comment '访问的url',
	query_params text not null comment 'get和post参数',
	content longtext not null comment '日志内容',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间'
)
comment 'app错误日表';

create table if not exists beacon_access_log
(
	id int auto_increment
		primary key,
	member_id int default 0 not null,
	beacon_id int default 0 not null,
	distance int default 0 not null,
	created_time timestamp null
)
comment 'iBeacon访问信息';

create table if not exists beacon_info
(
	id int auto_increment
		primary key,
	uuid varchar(100) default '' not null,
	major int default 0 not null,
	minor int default 0 not null,
	constraint ibeacon_info_uuid_uindex
		unique (uuid)
)
comment 'iBeacon设备信息';

create table if not exists img_info
(
	id int(11) unsigned auto_increment
		primary key,
	file_key varchar(60) default '' not null comment '文件名',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间'
);

create table if not exists member
(
	id int(11) unsigned auto_increment
		primary key,
	nickname varchar(100) default '' not null comment '会员名',
	mobile varchar(11) default '' not null comment '会员手机号码',
	gender tinyint(1) default 0 not null comment '性别 1：男 2：女',
	avatar varchar(200) default '' not null comment '会员头像',
	salt varchar(32) default '' not null comment '随机salt',
	reg_ip varchar(100) default '' not null comment '注册ip',
	status tinyint(1) default 1 not null comment '状态 1：有效 0：无效',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间'
)
comment '会员表';

create table if not exists member_cart
(
	id int(11) unsigned auto_increment
		primary key,
	member_id int(11) unsigned default 0 not null comment '会员id',
	product_id int default 0 not null comment '商品id',
	quantity int default 0 not null comment '数量',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间',
	constraint member_cart_member_id_fk
		foreign key (member_id) references member (id)
			on update cascade on delete cascade
)
comment '购物车';

create index idx_member_id
	on member_cart (member_id);

create table if not exists member_comments
(
	id int(11) unsigned auto_increment
		primary key,
	member_id int default 0 not null comment '会员id',
	food_ids varchar(200) default '' not null comment '商品ids',
	pay_order_id int default 0 not null comment '订单id',
	score tinyint default 0 not null comment '评分',
	content varchar(200) default '' not null comment '评论内容',
	created_time timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '插入时间'
)
comment '会员评论表';

create index idx_member_id
	on member_comments (member_id);

create table if not exists oauth_member_bind
(
	id int(11) unsigned auto_increment
		primary key,
	member_id int(11) unsigned default 0 not null comment '会员id',
	client_type varchar(20) default '' not null comment '客户端来源类型 - qq,weibo,weixin',
	type tinyint(3) default 0 not null comment '类型 type 1:wechat ',
	openid varchar(80) default '' not null comment '第三方id',
	unionid varchar(100) default '' not null,
	extra text not null comment '额外字段',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间',
	constraint oauth_member_bind_member_id_fk
		foreign key (member_id) references member (id)
			on update cascade on delete cascade
)
comment '第三方登录绑定关系';

create index idx_type_openid
	on oauth_member_bind (type, openid);

create table if not exists pay_order
(
	id int(11) unsigned auto_increment
		primary key,
	order_sn varchar(40) default '' not null comment '随机订单号',
	member_id int(11) unsigned default 0 not null comment '会员id',
	total_price decimal(10,2) default 0.00 not null comment '订单应付金额',
	pay_price decimal(10,2) default 0.00 not null comment '订单实付金额',
	pay_sn varchar(128) default '' not null comment '第三方流水号',
	prepay_id varchar(128) default '' not null comment '第三方预付id',
	note text not null comment '备注信息',
	comment_status int default 0 not null,
	pay_time timestamp default CURRENT_TIMESTAMP not null comment '付款到账时间',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最近一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间',
	status tinyint default 0 not null comment '1：支付完成 0 无效 -1 申请退款 -2 退款中 -9 退款成功  -8 待支付  -7 完成支付待确认',
	constraint idx_order_sn
		unique (order_sn),
	constraint pay_order_member_id_fk
		foreign key (member_id) references member (id)
			on update cascade on delete cascade
)
comment '购买订单表';

create index idx_member_id_status
	on pay_order (member_id, status);

create table if not exists pay_order_callback_data
(
	id int auto_increment
		primary key,
	pay_order_id int default 0 not null comment '支付订单id',
	pay_data text not null comment '支付回调信息',
	refund_data text not null comment '退款回调信息',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '创建时间',
	constraint pay_order_id
		unique (pay_order_id)
);

create table if not exists pay_order_item
(
	id int(11) unsigned auto_increment
		primary key,
	pay_order_id int(11) unsigned default 0 not null comment '订单id',
	member_id bigint(11) default 0 not null comment '会员id',
	quantity int default 1 not null comment '购买数量 默认1份',
	price decimal(10,2) default 0.00 not null comment '商品总价格，售价 * 数量',
	product_id int default 0 not null comment '商品表id',
	note text not null comment '备注信息',
	status tinyint(1) default 1 not null comment '状态：1：成功 0 失败',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最近一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间',
	constraint pay_order_item_pay_order_id_fk
		foreign key (pay_order_id) references pay_order (id)
			on update cascade on delete cascade
)
comment '订单详情表';

create index id_order_id
	on pay_order_item (pay_order_id);

create index idx_product_id
	on pay_order_item (product_id);

create table if not exists product_cat
(
	id int(11) unsigned auto_increment,
	name varchar(50) default '' not null comment '类别名称',
	weight tinyint default 1 not null comment '权重',
	status tinyint(1) default 1 not null comment '状态 1：有效 0：无效',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间',
	constraint idx_name
		unique (id)
)
comment '商品分类';

alter table product_cat
	add primary key (id);

create table if not exists product
(
	id int(11) unsigned auto_increment
		primary key,
	cat_id int(11) unsigned default 0 not null comment '分类id',
	name varchar(100) default '' not null comment '商品名称',
	price decimal(10,2) default 0.00 not null comment '售卖金额',
	main_image varchar(100) default '' not null comment '主图',
	summary varchar(10000) default '' not null comment '描述',
	stock int default 0 not null comment '库存量',
	tags varchar(200) default '' not null comment 'tag关键字，以","连接',
	status tinyint(1) default 1 not null comment '状态 1：有效 0：无效',
	month_count int default 0 not null comment '月销售数量',
	total_count int default 0 not null comment '总销售量',
	view_count int default 0 not null comment '总浏览次数',
	comment_count int default 0 not null comment '总评论量',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '最后插入时间',
	beacon_id int not null,
	constraint product_product_cat_id_fk
		foreign key (cat_id) references product_cat (id)
)
comment '商品表';

create table if not exists product_sale_change_log
(
	id int(11) unsigned auto_increment
		primary key,
	product_id int(11) unsigned default 0 not null comment '商品id',
	quantity int default 0 not null comment '售卖数量',
	price decimal(10,2) default 0.00 not null comment '售卖金额',
	member_id int default 0 not null comment '会员id',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '售卖时间',
	constraint product_sale_change_log_product_id_fk
		foreign key (product_id) references product (id)
)
comment '商品销售情况';

create index idx_prodcut_id_id
	on product_sale_change_log (product_id);

create table if not exists product_stock_change_log
(
	id int(11) unsigned auto_increment
		primary key,
	product_id int(11) unsigned not null comment '商品id',
	unit int default 0 not null comment '变更多少',
	total_stock int default 0 not null comment '变更之后总量',
	note varchar(100) default '' not null comment '备注字段',
	created_time datetime default CURRENT_TIMESTAMP not null comment '插入时间',
	constraint product_stock_change_log_product_id_fk
		foreign key (product_id) references product (id)
)
comment '数据库存变更表';

create index idx_product_id
	on product_stock_change_log (product_id);

create table if not exists stat_daily_food
(
	id int(11) unsigned auto_increment
		primary key,
	date date not null,
	food_id int default 0 not null comment '菜品id',
	total_count int default 0 not null comment '售卖总数量',
	total_pay_money decimal(10,2) default 0.00 not null comment '总售卖金额',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间'
)
comment '书籍售卖日统计';

create index date_food_id
	on stat_daily_food (date, food_id);

create table if not exists stat_daily_member
(
	id int(11) unsigned auto_increment
		primary key,
	date date not null comment '日期',
	member_id int default 0 not null comment '会员id',
	total_shared_count int default 0 not null comment '当日分享总次数',
	total_pay_money decimal(10,2) default 0.00 not null comment '当日付款总金额',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间'
)
comment '会员日统计';

create index idx_date_member_id
	on stat_daily_member (date, member_id);

create table if not exists stat_daily_site
(
	id int(11) unsigned auto_increment
		primary key,
	date date not null comment '日期',
	total_pay_money decimal(10,2) default 0.00 not null comment '当日应收总金额',
	total_member_count int not null comment '会员总数',
	total_new_member_count int not null comment '当日新增会员数',
	total_order_count int not null comment '当日订单数',
	total_shared_count int not null,
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间'
)
comment '全站日统计';

create index idx_date
	on stat_daily_site (date);

create table if not exists user
(
	uid bigint auto_increment comment '用户uid'
		primary key,
	nickname varchar(100) default '' not null comment '用户名',
	mobile varchar(20) default '' not null comment '手机号码',
	email varchar(100) default '' not null comment '邮箱地址',
	gender tinyint(1) default 0 not null comment '1：男 2：女 0：没填写',
	avatar varchar(64) default '' not null comment '头像',
	login_name varchar(20) default '' not null comment '登录用户名',
	login_pwd varchar(32) default '' not null comment '登录密码',
	login_salt varchar(32) default '' not null comment '登录密码的随机加密秘钥',
	status tinyint(1) default 1 not null comment '1：有效 0：无效',
	updated_time timestamp default CURRENT_TIMESTAMP not null comment '最后一次更新时间',
	created_time timestamp default CURRENT_TIMESTAMP not null comment '插入时间',
	constraint login_name
		unique (login_name)
)
comment '用户表（管理员）';

