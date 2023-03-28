CREATE DATABASE IF NOT EXISTS logistic;

USE logistic;

CREATE TABLE if not exists `packages` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `shop_id` int,
  `current_station_id` int,
  `customer_id` int,
  `status` tinyint(1),
  `pkg_order` varchar(4) NOT NULL UNIQUE
);

CREATE TABLE if not exists `shops` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `email` varchar(100) NOT NULL,
  `webhook_url` varchar(100) DEFAULT NULL
) character set utf8 collate = utf8_unicode_ci;

CREATE TABLE if not exists `stations` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(150) DEFAULT NULL,
  `address_id` int
) character set utf8 collate = utf8_unicode_ci;

CREATE TABLE if not exists `customers` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  `email` varchar(100) NOT NULL,
  `address_id` int
) character set utf8 collate = utf8_unicode_ci;

CREATE TABLE if not exists `addresses` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(150) DEFAULT NULL
) character set utf8 collate = utf8_unicode_ci;

ALTER TABLE `packages` ADD FOREIGN KEY (`shop_id`) REFERENCES `shops` (`id`);

ALTER TABLE `packages` ADD FOREIGN KEY (`current_station_id`) REFERENCES `stations` (`id`);

ALTER TABLE `packages` ADD FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`);

ALTER TABLE `customers` ADD FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`);

ALTER TABLE `stations` ADD FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`);

INSERT INTO addresses VALUES (29, 'Hà Nội');

INSERT INTO addresses VALUES (50, 'TP Hồ Chí Minh');

INSERT INTO addresses VALUES (43, 'Đà Nẵng');

INSERT INTO addresses VALUES (15, 'Hải Phòng');

INSERT INTO addresses VALUES (65, 'Cần Thơ');

INSERT INTO customers VALUES (1, 'Nguyễn Trường An', 'an1210@gmail.com', 29);

INSERT INTO customers VALUES (2, 'Đặng Văn Cường', 'cuong2305@gmail.com', 29);

INSERT INTO customers VALUES (3, 'Hoàng Đức Mạnh', 'manhkn@gmail.com', 43);

INSERT INTO customers VALUES (4, 'Nguyễn Trọng Khải', 'khaipop1@gmail.com', 50);

INSERT INTO customers VALUES (5, 'Đặng Thùy Chi', 'chi100@gmail.com', 65);

INSERT INTO customers VALUES (6, 'Phạm Mai Hương', 'huong1999@gmail.com', 15);

INSERT INTO shops VALUES (1, 'alpha', 'alpha@gmail.com', '/alpha');

INSERT INTO shops VALUES (2, 'beta', 'beta@gmail.com', '/beta');

INSERT INTO shops VALUES (3, 'gamma', 'gamma@gmail.com', '/gamma');

INSERT INTO stations VALUES (1, 'Kho Hà Nội', 29);

INSERT INTO stations VALUES (2, 'Kho HCM', 50);

INSERT INTO stations VALUES (3, 'Kho Đà Nẵng', 43);

INSERT INTO stations VALUES (4, 'Kho Hải Phòng', 15);

INSERT INTO stations VALUES (5, 'Kho Cần Thơ', 65);

INSERT INTO packages VALUES (1, 1, 1, 1, 4, 'P102');

INSERT INTO packages VALUES (2, 2, 2, 1, 1, 'P664');

INSERT INTO packages VALUES (3, 3, 4, 4, 2, 'P503');

INSERT INTO packages VALUES (4, 2, 5, 3, 3, 'P208');

INSERT INTO packages VALUES (5, 1, 2, 2, 2, 'P952');

INSERT INTO packages VALUES (6, 2, 5, 3, 4, 'P231');

INSERT INTO packages VALUES (7, 1, 4, 5, 3, 'P751');

INSERT INTO packages VALUES (8, 3, 3, 4, 2, 'P152');

