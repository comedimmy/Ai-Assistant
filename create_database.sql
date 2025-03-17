

#Table:水族箱
create table if not exists Aquarium(
	aquarium_id varchar(50),
	highest_temperature float,
	lowest_temperature  float,
	fish_species    varchar(20),
	fish_amount     integer,
	feed_amount     integer,
	feed_time       time,
	water_level     integer,
	AI_model        enum('ChatGPT','Gemini','Deepseek'),
	light_status    bool,
	TDS             float,
	temperature     float,
	QR_code         integer,
	Last_update     datetime
);

#Table:使用者
create table if not exists users(
    user_id varchar(50),
    nickname varchar(20),
    Login_type enum('Google', 'Line'),
    Last_login datetime
);
#Table:水族箱名稱
create table if not exists aquriumName(
	user_id varchar(50),
	aquarium_id varchar(50),
	aquarium_name varchar(20)
);
#Table:照片
create table if not exists photos(
	user_id varchar(50),
	aquarium_id varchar(50),
	path varchar(50)
);
##Table:事件紀錄
#create table if not exists events(
#	event_id integer,
#	status bool,
#	event_class enum(),
#	action varchar(50)
#);

#Table:對話紀錄
create table if not exists Dialogue(
	message_id integer,
	aquarium_id varchar(50),
	content varchar(1024),
	transmit_time datetime,
	sender enum('AI','使用者')
);

#Table:狀態歷史紀錄
create table if not exists statusHistory(
	record_id integer,
	TDS float,
	temperature float,
	water_level float,
	record_time datetime
);

#Table:定時任務
create table if not exists Tasks(
	task_id integer,
	task_name varchar(20),
	mqtt_topic varchar(20),
	instructions varchar(20),
	daily time,
	frequency enum('day','week','month'),
	next_exe_time datetime,
	status enum('execution','pause'),
	create_time datetime,
	last_update datetime
);

#Table:通知管理
create table if not exists notification(
	notification_id integer,
	user_id varchar(50),
	content varchar(50),
	send_time datetime,
	status enum('success','fail')
);