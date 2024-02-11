drop table model

create table model (
	model_id		integer		not null primary key,
	model_name		varchar(30)	not null,
	in_use			boolean		not null,
	constraint model_name_unq unique(model_name)
)
;

insert into model values (0, 'gpt-3.5-turbo-instruct', true);
insert into model values (1, 'gpt-3.5-turbo-0125', true);
insert into model values (2, 'gpt-3.5-turbo', true);
insert into model values (3, 'gpt-3.5-turbo-16k', true);
insert into model values (4, 'gpt-3.5-turbo-0613', true);
insert into model values (5, 'gpt-3.5-turbo-16k-0613', true);
insert into model values (6, 'gpt-3.5-turbo-1106', true);
insert into model values (7, 'gpt-3.5-turbo-0301', true);
insert into model values (8, 'gpt-3.5-turbo-instruct-0914', true);


select *
from model;

drop table "user" cascade;

create table "user" (
	user_id			integer		not null	primary key,
	first_name 		varchar(30)	not null,
	last_name		varchar(30)	not null,
	username		varchar(30)	not null,
	is_admin		bool 		not null	default false,
	is_admitted		bool		not null	default false,
	model_id		integer		not null	default 6	references model(model_id) on delete cascade,
	temperature		float		not null	default 1,
	max_tokens		integer		not null	default 100
);

insert into "user" values(204644083,'lera', 'yatsevich', 'lerabarnard', true);

insert into "user" values(171605607,'kolya', 'panaioti', 'kolya');



update "user" 
set is_admin  = false,
	is_admitted = true
where user_id=171605607;


select *
from "user";


--create table chat (
--	chat_id			integer 	not null	primary key
--);

drop table chat_id 

--create table user_chat (
--	chat_id			integer		not null	references chat(chat_id) on delete cascade,
--	user_id			integer		not null	references "user" (user_id) on delete cascade,
--	constraint user_chat_unq	primary key(chat_id, user_id)
--);


create table role (
	role_id 		integer		not null	primary key,
	role_name		VARCHAR(10)	not null
)

insert into role values(0,'system');
insert into role values(1,'user');
insert into role values(2,'assistant');


select *
from role;

drop table context;

create table context (
	content_id		integer 	not null	primary key,
	content_name	varchar(50)	not null,
	user_id			integer 	not null	references "user" (user_id) on delete cascade,
	context			json 		not null
);

select *
from context;


SELECT *--column_name, data_type, table_schema , table_name 
FROM information_schema.columns
where table_name ='model'
	and table_catalog ='db'
	and table_schema ='public'
	
	;
commit;