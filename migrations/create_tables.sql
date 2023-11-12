drop table if exists customer_research;
CREATE TABLE stage.customer_research(
   ID serial,
   date_id          TIMESTAMP ,
   category_id integer,
   geo_id   integer,
   sales_qty    integer,
   sales_amt numeric(14,2),
   PRIMARY KEY (ID)
);

CREATE INDEX main3 ON stage.customer_research (category_id);


drop table if exists user_activity_log;
create table if not exists user_activity_log (
    id serial,
    uniq_id varchar,
    date_time timestamp,
    action_id bigint,
    customer_id bigint,
    quantity bigint,
    primary key (id)
    
);


drop table if exists user_order_log;
create table if not exists user_order_log (
    id serial,
    uniq_id varchar(100),
    date_time timestamp,
    city_id integer,
    city_name varchar(100),
    customer_id bigint,
    first_name varchar(100),
    last_name varchar(100),
    item_id integer,
    item_name varchar(100),
    quantity bigint,
    payment_amount numeric(14, 2),
    primary key (id)
);

--create table prod.customer_research
--as 
--select scr.date_id, scr.geo_id, scr.sales_qty, scr.sales_amt
--from stage.customer_research scr; 
--
--create table prod.user_order_log
--as 
--select suol.date_time, suol.customer_id, suol.quantity, suol.payment_amount
--from stage.user_order_log suol; 
--
--create table prod.user_activity_log
--as 
--select sual.date_time, sual.customer_id
--from stage.user_activity_log sual; 