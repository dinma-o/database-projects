PRAGMA foreign_keys=ON;
-- Let's drop the tables in case they exist from previous runs
drop table if exists orderlines;
drop table if exists orders;
drop table if exists cart;
drop table if exists search;
drop table if exists viewedProduct;
drop table if exists sessions;
drop table if exists products;
drop table if exists customers;
drop table if exists users;

CREATE TABLE users (
      uid int primary key,
      pwd text,
      role text
    );
INSERT INTO users VALUES(1,'6631','customer');
INSERT INTO users VALUES(2,'6977','sales');
INSERT INTO users VALUES(3,'1162','customer');
CREATE TABLE customers (
      cid int primary key,
      name text,
      email text,
      foreign key (cid) references users(uid)
    );
INSERT INTO customers VALUES(1,'Angel Vincent','jgonzalez@example.org');
INSERT INTO customers VALUES(3,'Robert Burke','charlesclark@example.org');
CREATE TABLE products (
      pid int primary key,
      name text,
      category text,
      price float,
      stock_count int,
      descr text
    );
INSERT INTO products VALUES(1,'Wireless Keyboard','electronics',9.009999999999999787,9,'Compact wireless keyboard with long battery life and comfortable typing experience using advanced wireless technology.');
INSERT INTO products VALUES(2,'Smart Plug','electronics',267.2200000000000273,5,'WiFi smart outlet with voice control. Turn devices on/off remotely with smart home integration.');
INSERT INTO products VALUES(3,'Stainless Steel Kitchen Knife','kitchen',67.73000000000000397,4,'Chef''s knife with high-carbon stainless steel blade. Precision-forged stainless steel for superior sharpness.');
INSERT INTO products VALUES(4,'Leather Messenger Bag','clothing',282.0600000000000022,3,'Professional leather messenger bag for laptop and documents. Durable leather construction with vintage appeal.');
INSERT INTO products VALUES(5,'Smart Speaker','electronics',146.009999999999991,2,'Voice assistant smart speaker with premium sound. Control smart home devices with voice commands.');
INSERT INTO products VALUES(6,'Leather Watch Strap','clothing',278.3500000000000227,15,'Replacement leather watch band in various colors. Soft leather material with quick-release spring bars.');
INSERT INTO products VALUES(7,'Stainless Steel Travel Mug','accessories',191.6800000000000068,8,'Leak-proof stainless steel travel mug with lid. Vacuum-insulated stainless steel keeps coffee hot.');
INSERT INTO products VALUES(8,'Smart Doorbell','home',280.3999999999999773,16,'Video smart doorbell with motion detection. See and speak to visitors using smart technology.');
INSERT INTO products VALUES(9,'Organic Essential Oils','beauty',48.4200000000000017,18,'Therapeutic grade organic essential oil set. 100% pure organic oils for aromatherapy.');
INSERT INTO products VALUES(10,'Leather Jacket','clothing',19.30999999999999873,2,'Classic leather motorcycle jacket with quilted lining. Authentic leather craftsmanship and timeless style.');
INSERT INTO products VALUES(11,'Stainless Steel Utensil Set','kitchen',170.8400000000000034,5,'Complete stainless steel kitchen utensil set. Food-grade stainless steel tools for cooking.');
INSERT INTO products VALUES(12,'Stainless Steel Cookware Set','home',486.5600000000000022,3,'Professional stainless steel pots and pans set. Premium stainless steel with aluminum core for even heating.');
INSERT INTO products VALUES(13,'Smart Scale','beauty',39.81000000000000227,1,'Body composition smart scale with app sync. Track weight and metrics with smart health monitoring.');
INSERT INTO products VALUES(14,'Leather Journal','books',366.1399999999999864,19,'Refillable leather-bound journal for writing and sketching. Handmade leather cover with rustic charm.');
INSERT INTO products VALUES(15,'Stainless Steel Trash Can','home',206.6699999999999875,13,'Fingerprint-resistant stainless steel trash bin. Step-on design with brushed stainless steel finish.');
INSERT INTO products VALUES(16,'Stainless Steel Bottle','home',29.94999999999999929,12,'Insulated stainless steel water bottle.');
INSERT INTO products VALUES(17,'Stainless Steel Mixing Bowls','kitchen',54.99000000000000198,7,'Set of nesting stainless steel bowls.');
INSERT INTO products VALUES(18,'Stainless Steel Tongs','kitchen-tools',12.5,25,'Cooking tongs with stainless steel arms.');
INSERT INTO products VALUES(19,'Stainless Steel Shelf','furniture',89.0,6,'Wall-mounted stainless steel utility shelf.');
INSERT INTO products VALUES(20,'Stainless Steel Lunch Box','kids',34.75,10,'Leak-proof stainless steel lunch container.');
INSERT INTO products VALUES(21,'Smart Home Hub','electronics',189.99,12,'All-in-one smart home hub with voice control for connected device.');
INSERT INTO products VALUES(22,'Smart Home Voice Light','home',45.99,25,'Voice-controlled smart home light with brightness automation.');
INSERT INTO products VALUES(23,'Smart Home Voice Camera','electronics',129.5,9,'Smart home security camera with motion detection and voice alerts.');

CREATE TABLE sessions (
      cid int,
      sessionNo int,
      start_time datetime,
      end_time datetime,
      primary key (cid, sessionNo),
      foreign key (cid) references customers(cid) on delete cascade
    );

INSERT INTO sessions VALUES (1, 1, datetime('now', '-3 months', '-2 hours'), datetime('now', '-3 months', '+1 hours'));

INSERT INTO sessions VALUES (1, 2, datetime('now', '-6 months', '-2 hours'), datetime('now', '-6 months', '+1 hours'));

INSERT INTO sessions VALUES (3, 1, datetime('now', '-5 months', '-2 hours'), datetime('now', '-5 months', '+2 hours'));

INSERT INTO sessions VALUES (1, 3, datetime('now', '-2 hours'), NULL);

INSERT INTO sessions VALUES (1, 4, date('now', '-1 day', '-3 hours'), NULL);
INSERT INTO sessions VALUES (1, 8, date('now', '-2 days', '-2 hours'), NULL);


CREATE TABLE viewedProduct (
      cid int,
      sessionNo int,
      ts timestamp,
      pid int,
      primary key (cid, sessionNo, ts),
      foreign key (cid, sessionNo) references sessions(cid, sessionNo),
      foreign key (pid) references products(pid)
    );
INSERT INTO viewedProduct VALUES (1, 1, datetime('now', '-3 months', '-2 hours'), 8);

INSERT INTO viewedProduct VALUES (1, 2, datetime('now', '-6 months', '-1 hour', '-14 minutes'), 3);

INSERT INTO viewedProduct VALUES (1, 2, datetime('now', '-6 months', '-1 hour', '+10 minutes'), 6);

INSERT INTO viewedProduct VALUES (3, 1, datetime('now', '-5 months', '-1 hour'), 13);
CREATE TABLE search (
      cid int,
      sessionNo int,
      ts timestamp,
      query text,
      primary key (cid, sessionNo, ts),
      foreign key (cid, sessionNo) references sessions(cid, sessionNo)
    );
INSERT INTO search VALUES (1, 1, datetime('now', '-3 months', '-1 hour', '-10 minutes'), 'organic');
INSERT INTO search VALUES (1, 1, datetime('now', '-3 months', '-1 hour'), 'smart');
INSERT INTO search VALUES (1, 1, datetime('now', '-3 months', '+40 minutes'), 'leather');

INSERT INTO search VALUES (1, 2, datetime('now', '-6 months', '-1 hour', '-8 minutes'), 'organic');
INSERT INTO search VALUES (1, 2, datetime('now', '-6 months', '+5 minutes'), 'wireless');
INSERT INTO search VALUES (1, 2, datetime('now', '-6 months', '+21 minutes'), 'organic');

INSERT INTO search VALUES (3, 1, datetime('now', '-5 months', '+15 minutes'), 'stainless');
INSERT INTO search VALUES (3, 1, datetime('now', '-5 months', '+16 minutes'), 'organic');
CREATE TABLE cart (
      cid int,
      sessionNo int,
      pid int,
      qty int,
      primary key (cid, sessionNo, pid),
      foreign key (cid, sessionNo) references sessions(cid, sessionNo),
      foreign key (pid) references products(pid)
    );
INSERT INTO cart VALUES(1,1,15,2);
INSERT INTO cart VALUES(1,1,12,1);
INSERT INTO cart VALUES(1,2,5,2);
INSERT INTO cart VALUES(3,1,6,1);
CREATE TABLE orders (
      ono int primary key,
      cid int,
      sessionNo int,
      odate date,
      shipping_address text,
      foreign key (cid, sessionNo) references sessions(cid, sessionNo)
    );
INSERT INTO orders VALUES (1, 1, 2, date('now', '-6 months', '-2 hours'), '37496 Paul Keys Suite 670, Michelletown, NV 90697');
INSERT INTO orders VALUES (2, 1, 1, date('now', '-5 months', '-5 days', '-2 hours'), '9653 Martin Motorway Suite 101, Richardbury, NV 33283');
INSERT INTO orders VALUES (3, 1, 1, date('now', '-17 days'), '91976 Stephanie Road, Brownstad, MN 37133');  -- October
INSERT INTO orders VALUES (4, 1, 2, date('now', '-4 months', '-2 hours'), '0908 Chris Islands, Michelletown, WY 63636');
INSERT INTO orders VALUES (5, 1, 1, date('now', '-16 days', '-2 hours'), '34477 Randy Turnpike Apt. 060, Lake Jenniferview, PR 60126');
INSERT INTO orders VALUES (6, 1, 2, date('now', '-5 months', '-2 hours'), '05441 Frank Oval, Stephenland, KS 83584');
INSERT INTO orders VALUES (7, 1, 1, date('now', '-7 months', '-2 hours'), '79445 Summer Mountains, Brittanychester, WV 04543');
INSERT INTO orders VALUES (8, 1, 2, date('now', '-5 months', '-2 hours'), 'USCGC Mann, FPO AE 08086');
INSERT INTO orders VALUES (9, 3, 1, date('now', '-8 months', '-2 hours'), '9490 Richard Squares, Hicksborough, MT 49592');
INSERT INTO orders VALUES (10, 3, 1, date('now', '-2 months', '-2 hours'), '47832 Watson Mission, Wrightview, MP 72010');
INSERT INTO orders VALUES (11, 1, 4, date('now', '-1 day'), '12345 109 St NW, Edmonton, AB');
INSERT INTO orders VALUES (21, 1, 1, date('now', '-3 days'), '9999 Test Order Street');
INSERT INTO orders VALUES (22, 3, 1, date('now', '-3 days'), '2222 Second Customer Ave');
INSERT INTO orders VALUES (23, 1, 8, date('now', '-2 days'), '123 house');

CREATE TABLE orderlines (
      ono int,
      lineNo int,
      pid int,
      qty int,
      uprice float,
      primary key (ono, lineNo),
      foreign key (ono) references orders(ono) on delete cascade
    );
INSERT INTO orderlines VALUES(1,1,7,4,191.6800000000000068);
INSERT INTO orderlines VALUES(2,1,6,3,278.3500000000000227);
INSERT INTO orderlines VALUES(2,2,12,2,486.5600000000000022);
INSERT INTO orderlines VALUES(2,3,1,3,9.009999999999999787);
INSERT INTO orderlines VALUES(3,1,4,3,282.0600000000000022);
INSERT INTO orderlines VALUES(3,2,8,4,280.3999999999999773);
INSERT INTO orderlines VALUES(3,3,1,1,9.009999999999999787);
INSERT INTO orderlines VALUES(4,1,4,5,282.0600000000000022);
INSERT INTO orderlines VALUES(4,2,7,4,191.6800000000000068);
INSERT INTO orderlines VALUES(5,1,12,3,486.5600000000000022);
INSERT INTO orderlines VALUES(6,1,11,5,170.8400000000000034);
INSERT INTO orderlines VALUES(6,2,8,2,280.3999999999999773);
INSERT INTO orderlines VALUES(7,1,10,3,19.30999999999999873);
INSERT INTO orderlines VALUES(7,2,8,5,280.3999999999999773);
INSERT INTO orderlines VALUES(8,1,3,4,67.73000000000000397);
INSERT INTO orderlines VALUES(9,1,8,3,280.3999999999999773);
INSERT INTO orderlines VALUES(9,2,11,1,170.8400000000000034);
INSERT INTO orderlines VALUES(9,3,14,3,366.1399999999999864);
INSERT INTO orderlines VALUES(10,1,13,5,39.81000000000000227);
INSERT INTO orderlines VALUES(10,2,6,1,278.3500000000000227);

-- Order 11
INSERT INTO orderlines VALUES(11,1,5,2,19.99);
INSERT INTO orderlines VALUES(11,2,12,1,9.50);

-- Order 21
INSERT INTO orderlines VALUES(21,1,7,2,14.25);

-- Order 22
INSERT INTO orderlines VALUES(22,1,3,1,29.99);
INSERT INTO orderlines VALUES(22,2,18,2,11.75);

-- Order 23
INSERT INTO orderlines VALUES(23,1,10,2,6.99);
