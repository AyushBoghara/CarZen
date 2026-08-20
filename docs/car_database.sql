CREATE TABLE `users` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100),
  `username` varchar(100) UNIQUE NOT NULL,
  `email` varchar(150) UNIQUE NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone_number` varchar(20) UNIQUE,
  `role` ENUM ('buyer', 'seller', 'reseller', 'service_provider') NOT NULL,
  `status` ENUM ('active', 'inactive', 'blocked', 'deleted') DEFAULT 'active',
  `profile_image_url` varchar(500),
  `created_at` timestamp,
  `updated_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `addresses` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `address_line_1` varchar(255) NOT NULL,
  `address_line_2` varchar(255),
  `landmark` varchar(255),
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `country` varchar(100) DEFAULT 'India',
  `postal_code` varchar(10) NOT NULL,
  `latitude` decimal(10,7),
  `longitude` decimal(10,7),
  `is_default` boolean DEFAULT false,
  `created_at` timestamp,
  `updated_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `car_brands` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(100) UNIQUE NOT NULL,
  `slug` varchar(120) UNIQUE NOT NULL,
  `country` varchar(100),
  `logo_url` varchar(500),
  `description` text,
  `is_active` boolean DEFAULT true,
  `created_at` timestamp,
  `updated_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `car_models` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `brand_id` bigint NOT NULL,
  `name` varchar(100) NOT NULL,
  `slug` varchar(120) UNIQUE NOT NULL,
  `body_type` ENUM ('hatchback', 'sedan', 'suv', 'muv', 'coupe', 'convertible', 'pickup', 'minivan', 'other'),
  `seating_capacity` integer,
  `description` text,
  `is_active` boolean DEFAULT true,
  `created_at` timestamp,
  `updated_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `car_variants` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `model_id` bigint NOT NULL,
  `variant_name` varchar(150) NOT NULL,
  `fuel_type` ENUM ('petrol', 'diesel', 'cng', 'electric', 'hybrid') NOT NULL,
  `transmission` ENUM ('manual', 'automatic', 'amt', 'cvt', 'dct') NOT NULL,
  `engine_cc` decimal(8,2),
  `horsepower` decimal(8,2),
  `seating_capacity` integer,
  `ex_showroom_price` decimal(15,2),
  `created_at` timestamp,
  `updated_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `cars` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `variant_id` bigint NOT NULL,
  `owner_id` bigint NOT NULL,
  `registration_number` varchar(30) UNIQUE,
  `vin_number` varchar(100) UNIQUE,
  `manufacturing_year` integer NOT NULL,
  `registration_year` integer,
  `fuel_type` ENUM ('petrol', 'diesel', 'cng', 'electric', 'hybrid') NOT NULL,
  `transmission` ENUM ('manual', 'automatic', 'amt', 'cvt', 'dct') NOT NULL,
  `engine_cc` decimal(8,2),
  `horsepower` decimal(8,2),
  `mileage_km` decimal(12,2) NOT NULL,
  `color` varchar(50),
  `seating_capacity` integer,
  `owner_count` integer DEFAULT 1,
  `ownership_type` ENUM ('first_owner', 'second_owner', 'third_owner', 'fourth_or_more'),
  `condition` ENUM ('excellent', 'good', 'fair', 'poor') NOT NULL,
  `insurance_company` varchar(150),
  `insurance_type` varchar(100),
  `insurance_expiry` date,
  `rc_status` varchar(50),
  `city` varchar(100) NOT NULL,
  `state` varchar(100) NOT NULL,
  `country` varchar(100) DEFAULT 'India',
  `postal_code` varchar(10),
  `description` text,
  `expected_market_price` decimal(15,2),
  `is_verified` boolean DEFAULT false,
  `created_at` timestamp,
  `updated_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `car_media` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `car_id` bigint NOT NULL,
  `media_type` ENUM ('image', 'video', 'document') NOT NULL,
  `media_url` varchar(500) NOT NULL,
  `thumbnail_url` varchar(500),
  `file_name` varchar(255),
  `file_size` bigint,
  `sort_order` integer DEFAULT 0,
  `is_primary` boolean DEFAULT false,
  `created_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `car_features` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `car_id` bigint NOT NULL,
  `feature_name` varchar(150) NOT NULL,
  `feature_value` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `listings` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `car_id` bigint NOT NULL,
  `seller_id` bigint NOT NULL,
  `listing_type` ENUM ('sale', 'resale') NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text,
  `asking_price` decimal(15,2) NOT NULL,
  `negotiable` boolean DEFAULT true,
  `listing_status` ENUM ('draft', 'active', 'reserved', 'sold', 'expired', 'cancelled', 'removed') DEFAULT 'draft',
  `listed_at` timestamp,
  `expiry_date` timestamp,
  `views_count` integer DEFAULT 0,
  `created_at` timestamp,
  `updated_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `ownership_history` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `car_id` bigint NOT NULL,
  `owner_id` bigint NOT NULL,
  `ownership_number` integer NOT NULL,
  `ownership_type` ENUM ('first_owner', 'second_owner', 'third_owner', 'fourth_or_more'),
  `purchase_date` date,
  `sale_date` date,
  `purchase_price` decimal(15,2),
  `sale_price` decimal(15,2),
  `purchase_location` varchar(150),
  `sale_location` varchar(150),
  `created_at` timestamp
);

CREATE TABLE `service_centers` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `owner_id` bigint,
  `name` varchar(200) NOT NULL,
  `contact_person` varchar(150),
  `email` varchar(150),
  `phone_number` varchar(20),
  `address_line_1` varchar(255),
  `address_line_2` varchar(255),
  `city` varchar(100),
  `state` varchar(100),
  `country` varchar(100) DEFAULT 'India',
  `postal_code` varchar(10),
  `latitude` decimal(10,7),
  `longitude` decimal(10,7),
  `rating` decimal(3,2),
  `is_verified` boolean DEFAULT false,
  `is_active` boolean DEFAULT true,
  `created_at` timestamp,
  `updated_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `service_records` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `car_id` bigint NOT NULL,
  `service_center_id` bigint,
  `service_type` varchar(150) NOT NULL,
  `service_date` date NOT NULL,
  `odometer_reading` decimal(12,2),
  `service_cost` decimal(15,2),
  `parts_cost` decimal(15,2),
  `labor_cost` decimal(15,2),
  `description` text,
  `next_service_date` date,
  `next_service_mileage` decimal(12,2),
  `status` ENUM ('scheduled', 'completed', 'cancelled') DEFAULT 'completed',
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `service_items` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `service_record_id` bigint NOT NULL,
  `item_name` varchar(150) NOT NULL,
  `quantity` integer DEFAULT 1,
  `unit_cost` decimal(15,2),
  `total_cost` decimal(15,2),
  `created_at` timestamp
);

CREATE TABLE `favorites` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `car_id` bigint NOT NULL,
  `created_at` timestamp
);

CREATE TABLE `inquiries` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `listing_id` bigint NOT NULL,
  `buyer_id` bigint NOT NULL,
  `seller_id` bigint NOT NULL,
  `subject` varchar(255),
  `message` text NOT NULL,
  `status` ENUM ('open', 'contacted', 'closed') DEFAULT 'open',
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `transactions` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `listing_id` bigint NOT NULL,
  `car_id` bigint NOT NULL,
  `buyer_id` bigint NOT NULL,
  `seller_id` bigint NOT NULL,
  `final_price` decimal(15,2) NOT NULL,
  `transaction_date` timestamp,
  `payment_method` ENUM ('cash', 'upi', 'card', 'bank_transfer', 'finance', 'other'),
  `payment_status` ENUM ('pending', 'partial', 'paid', 'failed', 'refunded') DEFAULT 'pending',
  `transaction_status` ENUM ('initiated', 'completed', 'cancelled', 'failed') DEFAULT 'initiated',
  `notes` text,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `payments` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `transaction_id` bigint NOT NULL,
  `amount` decimal(15,2) NOT NULL,
  `currency` varchar(10) DEFAULT 'INR',
  `payment_method` ENUM ('cash', 'upi', 'card', 'bank_transfer', 'finance', 'other'),
  `provider` varchar(100),
  `provider_transaction_id` varchar(255),
  `status` ENUM ('pending', 'partial', 'paid', 'failed', 'refunded') DEFAULT 'pending',
  `payment_date` timestamp,
  `metadata` json,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `price_predictions` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `car_id` bigint,
  `user_id` bigint NOT NULL,
  `prediction_status` ENUM ('requested', 'completed', 'failed') DEFAULT 'requested',
  `predicted_price` decimal(15,2),
  `minimum_price` decimal(15,2),
  `maximum_price` decimal(15,2),
  `confidence_score` decimal(5,2),
  `model_name` varchar(150),
  `model_version` varchar(100),
  `prediction_input` json,
  `prediction_date` timestamp,
  `created_at` timestamp
);

CREATE TABLE `prediction_features` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `prediction_id` bigint NOT NULL,
  `feature_name` varchar(100) NOT NULL,
  `feature_value` varchar(255),
  `created_at` timestamp
);

CREATE TABLE `reviews` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `car_id` bigint,
  `listing_id` bigint,
  `rating` integer NOT NULL,
  `title` varchar(255),
  `review_text` text,
  `is_visible` boolean DEFAULT true,
  `created_at` timestamp,
  `updated_at` timestamp,
  `deleted_at` timestamp
);

CREATE TABLE `admins` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint UNIQUE NOT NULL,
  `role` ENUM ('super_admin', 'admin', 'moderator') NOT NULL,
  `is_active` boolean DEFAULT true,
  `created_at` timestamp,
  `updated_at` timestamp
);

CREATE TABLE `reports` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `reporter_id` bigint NOT NULL,
  `listing_id` bigint,
  `car_id` bigint,
  `reason` varchar(255) NOT NULL,
  `description` text,
  `status` varchar(50) DEFAULT 'pending',
  `created_at` timestamp,
  `resolved_at` timestamp
);

CREATE TABLE `notifications` (
  `id` bigint PRIMARY KEY AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `notification_type` varchar(100),
  `reference_id` bigint,
  `reference_type` varchar(100),
  `is_read` boolean DEFAULT false,
  `created_at` timestamp
);

ALTER TABLE `addresses` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `car_models` ADD FOREIGN KEY (`brand_id`) REFERENCES `car_brands` (`id`);

ALTER TABLE `car_variants` ADD FOREIGN KEY (`model_id`) REFERENCES `car_models` (`id`);

ALTER TABLE `cars` ADD FOREIGN KEY (`variant_id`) REFERENCES `car_variants` (`id`);

ALTER TABLE `cars` ADD FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`);

ALTER TABLE `car_media` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `car_features` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `listings` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `listings` ADD FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`);

ALTER TABLE `ownership_history` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `ownership_history` ADD FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`);

ALTER TABLE `service_centers` ADD FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`);

ALTER TABLE `service_records` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `service_records` ADD FOREIGN KEY (`service_center_id`) REFERENCES `service_centers` (`id`);

ALTER TABLE `service_items` ADD FOREIGN KEY (`service_record_id`) REFERENCES `service_records` (`id`);

ALTER TABLE `favorites` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `favorites` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `inquiries` ADD FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`);

ALTER TABLE `inquiries` ADD FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`);

ALTER TABLE `inquiries` ADD FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`);

ALTER TABLE `transactions` ADD FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`);

ALTER TABLE `payments` ADD FOREIGN KEY (`transaction_id`) REFERENCES `transactions` (`id`);

ALTER TABLE `price_predictions` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `price_predictions` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `prediction_features` ADD FOREIGN KEY (`prediction_id`) REFERENCES `price_predictions` (`id`);

ALTER TABLE `reviews` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `reviews` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `reviews` ADD FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`);

ALTER TABLE `admins` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

ALTER TABLE `reports` ADD FOREIGN KEY (`reporter_id`) REFERENCES `users` (`id`);

ALTER TABLE `reports` ADD FOREIGN KEY (`listing_id`) REFERENCES `listings` (`id`);

ALTER TABLE `reports` ADD FOREIGN KEY (`car_id`) REFERENCES `cars` (`id`);

ALTER TABLE `notifications` ADD FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);
