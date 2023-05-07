CREATE TABLE `packages` (
  `id` int PRIMARY KEY,
  `code` varchar(255),
  `shop_id` int,
  `current_station_id` int,
  `customer_id` int,
  `cod_id` int,
  `status` int,
  `picked_at` timestamp,
  `delivered_at` timestamp,
  `done_at` timestamp,
  `audited_at` timestamp,
  `created` timestamp default now(),
  `modified` timestamp
);

CREATE TABLE `shops` (
  `id` int PRIMARY KEY,
  `name` varchar(255),
  `email` varchar(255),
  `webhook_url` varchar(255),
  `created` datetime,
  `modified` datetime
);

CREATE TABLE `stations` (
  `id` int PRIMARY KEY,
  `name` varchar(255),
  `address_id` int,
  `created` datetime,
  `modified` datetime
);

CREATE TABLE `customers` (
  `id` int PRIMARY KEY,
  `name` varchar(255),
  `email` varchar(255),
  `address_id` int,
  `created` datetime,
  `modified` datetime
);

CREATE TABLE `addresses` (
  `id` int PRIMARY KEY,
  `name` varchar(255),
  `created` datetime,
  `modified` datetime
);

CREATE TABLE `cods` (
  `id` int PRIMARY KEY,
  `name` varchar(255),
  `station_id` int,
  `created` datetime,
  `modified` datetime
);

ALTER TABLE `packages` ADD FOREIGN KEY (`shop_id`) REFERENCES `shops` (`id`);

ALTER TABLE `packages` ADD FOREIGN KEY (`current_station_id`) REFERENCES `stations` (`id`);

ALTER TABLE `packages` ADD FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`);

ALTER TABLE `packages` ADD FOREIGN KEY (`cod_id`) REFERENCES `cods` (`id`);

ALTER TABLE `stations` ADD FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`);

ALTER TABLE `customers` ADD FOREIGN KEY (`address_id`) REFERENCES `addresses` (`id`);

ALTER TABLE `cods` ADD FOREIGN KEY (`station_id`) REFERENCES `stations` (`id`);