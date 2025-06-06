/*
 Navicat Premium Data Transfer

 Source Server         : 本科论文
 Source Server Type    : MySQL
 Source Server Version : 80025
 Source Host           : localhost:3306
 Source Schema         : warehouse

 Target Server Type    : MySQL
 Target Server Version : 80025
 File Encoding         : 65001

 Date: 06/06/2025 19:29:13
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for charging_orders
-- ----------------------------
DROP TABLE IF EXISTS `charging_orders`;
CREATE TABLE `charging_orders`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `robot_id` int NOT NULL,
  `station_id` int NOT NULL,
  `start_time` datetime NULL DEFAULT NULL,
  `end_time` datetime NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `charge_amount` float NULL DEFAULT NULL,
  `charging_efficiency` float NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `robot_id`(`robot_id` ASC) USING BTREE,
  INDEX `station_id`(`station_id` ASC) USING BTREE,
  CONSTRAINT `charging_orders_ibfk_1` FOREIGN KEY (`robot_id`) REFERENCES `robots` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `charging_orders_ibfk_2` FOREIGN KEY (`station_id`) REFERENCES `charging_stations` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 72 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of charging_orders
-- ----------------------------
INSERT INTO `charging_orders` VALUES (1, 1, 4, '2025-05-19 20:15:50', '2025-05-19 21:50:41', 'completed', 14.5012, 91.7281, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (2, 1, 5, '2025-05-08 12:24:50', '2025-05-08 15:53:41', 'completed', 14.4419, 82.9749, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (3, 1, 10, '2025-06-01 11:30:50', '2025-06-01 15:02:43', 'completed', 33.6927, 95.4093, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (4, 2, 7, '2025-05-27 18:30:50', '2025-05-27 20:28:34', 'completed', 8.59799, 87.6341, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (5, 2, 7, '2025-05-06 05:41:50', '2025-05-06 07:20:42', 'completed', 7.0045, 85.0127, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (6, 2, 1, '2025-06-01 17:37:50', '2025-06-01 18:45:28', 'completed', 8.05007, 95.1993, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (7, 2, 1, '2025-05-15 19:16:50', '2025-05-15 22:05:50', 'completed', 17.368, 82.2081, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (8, 3, 9, '2025-05-31 14:55:50', '2025-05-31 16:34:52', 'completed', 19.1951, 96.9058, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (9, 4, 8, '2025-05-13 20:24:50', '2025-05-13 22:02:16', 'completed', 18.7931, 96.4368, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (10, 4, 2, '2025-06-01 01:55:50', '2025-06-01 05:48:42', 'completed', 40.9237, 87.8677, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (11, 4, 7, '2025-06-04 15:52:50', '2025-06-04 17:35:39', 'completed', 7.94046, 92.6747, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (12, 4, 1, '2025-05-25 11:05:50', '2025-05-25 14:59:56', 'completed', 25.4861, 87.0934, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (13, 4, 10, '2025-05-18 22:46:50', '2025-05-19 00:17:57', 'completed', 14.4492, 95.1354, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (14, 5, 8, '2025-05-21 14:05:50', '2025-05-21 17:26:31', 'completed', 37.7249, 93.9902, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (15, 5, 1, '2025-05-30 01:23:50', '2025-05-30 03:49:24', 'completed', 17.7647, 97.6215, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (16, 6, 6, '2025-05-26 01:29:50', '2025-05-26 05:01:50', 'completed', 34.8595, 82.2117, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (17, 6, 7, '2025-05-10 18:18:50', '2025-05-10 22:03:29', 'completed', 16.4888, 88.0738, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (18, 6, 12, '2025-05-22 13:17:50', '2025-05-22 16:17:58', 'completed', 32.2806, 89.602, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (19, 6, 11, '2025-05-05 18:08:50', '2025-05-05 22:05:17', 'completed', 24.9907, 84.5486, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (20, 6, 2, '2025-05-09 23:07:50', '2025-05-10 00:13:26', 'completed', 12.4885, 95.1718, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (21, 7, 8, '2025-05-17 23:20:50', '2025-05-18 01:36:14', 'completed', 23.1166, 85.3606, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (22, 7, 8, '2025-05-09 02:29:50', '2025-05-09 03:54:07', 'completed', 14.3637, 85.203, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (23, 7, 10, '2025-05-15 15:35:50', '2025-05-15 16:52:22', 'completed', 10.3409, 81.0654, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (24, 7, 8, '2025-05-11 10:12:50', '2025-05-11 11:18:57', 'completed', 11.7807, 89.078, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (25, 8, 5, '2025-05-22 17:39:50', '2025-05-22 21:27:02', 'completed', 16.5199, 87.2485, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (26, 8, 2, '2025-05-25 05:36:50', '2025-05-25 06:47:45', 'completed', 13.0549, 92.0322, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (27, 8, 8, '2025-05-24 13:25:50', '2025-05-24 14:44:33', 'completed', 14.7639, 93.7752, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (28, 9, 8, '2025-05-19 12:25:50', '2025-05-19 16:04:03', 'completed', 35.6157, 81.6023, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (29, 10, 5, '2025-05-14 15:36:50', '2025-05-14 18:23:02', 'completed', 12.7886, 92.3302, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (30, 10, 12, '2025-05-15 01:17:50', '2025-05-15 03:56:38', 'completed', 26.8168, 84.4282, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (31, 10, 6, '2025-05-20 20:10:50', '2025-05-20 23:04:39', 'completed', 33.4088, 96.0966, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (32, 10, 4, '2025-05-17 04:34:50', '2025-05-17 06:21:36', 'completed', 14.9217, 83.8562, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (33, 10, 3, '2025-06-01 19:59:50', '2025-06-01 21:37:43', 'completed', 6.81609, 83.5536, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (34, 11, 12, '2025-05-12 06:08:50', '2025-05-12 07:54:51', 'completed', 17.5845, 82.9217, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (35, 11, 7, '2025-05-05 19:24:50', '2025-05-05 20:41:25', 'completed', 5.93855, 93.046, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (36, 11, 5, '2025-05-21 09:46:50', '2025-05-21 11:13:11', 'completed', 6.03485, 83.8639, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (37, 11, 10, '2025-05-29 23:28:50', '2025-05-30 01:07:00', 'completed', 15.0929, 92.2436, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (38, 11, 1, '2025-06-03 11:24:50', '2025-06-03 14:59:26', 'completed', 22.992, 85.7091, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (39, 12, 12, '2025-05-23 18:41:50', '2025-05-23 20:17:08', 'completed', 18.3486, 96.263, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (40, 12, 11, '2025-05-17 12:36:50', '2025-05-17 15:13:14', 'completed', 17.2942, 88.4554, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (41, 12, 6, '2025-05-31 13:42:50', '2025-05-31 15:19:49', 'completed', 18.943, 97.652, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (42, 13, 3, '2025-05-14 10:02:50', '2025-05-14 11:15:11', 'completed', 5.13482, 85.1495, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (43, 13, 1, '2025-06-01 05:09:50', '2025-06-01 08:23:12', 'completed', 20.6346, 85.364, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (44, 13, 2, '2025-05-28 12:07:50', '2025-05-28 13:28:46', 'completed', 13.2468, 81.8383, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (45, 13, 3, '2025-05-14 20:32:50', '2025-05-14 22:56:56', 'completed', 10.5081, 87.4981, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (46, 14, 2, '2025-05-27 05:58:50', '2025-05-27 07:20:44', 'completed', 13.2196, 80.6933, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (47, 14, 3, '2025-05-27 15:48:50', '2025-05-27 19:14:22', 'completed', 16.2591, 94.9286, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (48, 14, 6, '2025-05-25 09:57:50', '2025-05-25 12:48:41', 'completed', 33.067, 96.7678, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (49, 14, 12, '2025-05-17 23:57:50', '2025-05-18 03:17:09', 'completed', 34.0805, 85.4876, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (50, 14, 8, '2025-05-16 03:14:50', '2025-05-16 05:11:53', 'completed', 20.0361, 85.5849, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (51, 15, 2, '2025-05-16 15:09:50', '2025-05-16 17:10:56', 'completed', 21.8497, 90.2028, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (52, 15, 7, '2025-05-09 23:37:50', '2025-05-10 03:02:44', 'completed', 16.7184, 97.912, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (53, 16, 3, '2025-05-11 09:40:50', '2025-05-11 11:14:18', 'completed', 7.57487, 97.2439, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (54, 16, 9, '2025-05-31 17:06:50', '2025-05-31 20:25:12', 'completed', 36.3452, 91.6116, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (55, 16, 6, '2025-05-21 22:27:50', '2025-05-22 00:54:42', 'completed', 28.0505, 95.4893, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (56, 16, 1, '2025-05-11 11:19:50', '2025-05-11 14:58:41', 'completed', 25.098, 91.7408, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (57, 17, 8, '2025-05-12 06:21:50', '2025-05-12 07:34:33', 'completed', 13.5365, 93.0754, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (58, 17, 7, '2025-05-09 10:11:50', '2025-05-09 11:46:29', 'completed', 7.02846, 89.0976, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (59, 17, 10, '2025-05-30 03:40:50', '2025-05-30 06:23:47', 'completed', 24.6611, 90.8006, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (60, 17, 2, '2025-05-24 05:11:50', '2025-05-24 07:59:12', 'completed', 29.8089, 89.0513, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (61, 18, 5, '2025-05-18 08:29:50', '2025-05-18 09:57:47', 'completed', 6.46663, 88.2223, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (62, 18, 2, '2025-05-16 16:57:50', '2025-05-16 19:22:47', 'completed', 27.1758, 93.7399, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (63, 18, 10, '2025-05-21 12:08:50', '2025-05-21 14:15:13', 'completed', 19.3959, 92.0706, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (64, 19, 7, '2025-05-20 10:36:50', '2025-05-20 14:19:00', 'completed', 18.0044, 97.2414, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (65, 19, 6, '2025-05-27 14:57:50', '2025-05-27 16:19:39', 'completed', 15.8021, 96.5583, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (66, 19, 10, '2025-05-07 11:03:50', '2025-05-07 12:34:51', 'completed', 14.7897, 97.4931, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (67, 20, 10, '2025-05-17 04:35:50', '2025-05-17 08:11:27', 'completed', 29.6294, 82.4474, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (68, 20, 7, '2025-06-01 00:39:50', '2025-06-01 01:59:30', 'completed', 5.62653, 84.7447, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (69, 20, 2, '2025-05-17 07:47:50', '2025-05-17 10:49:41', 'completed', 34.0059, 93.4956, '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_orders` VALUES (70, 1, 2, '2025-06-05 17:13:01', '2025-06-05 17:15:30', 'completed', 0, 90, '2025-06-05 17:13:01', '2025-06-05 17:15:30');
INSERT INTO `charging_orders` VALUES (71, 1, 2, '2025-06-05 17:15:36', '2025-06-06 10:38:51', 'completed', 0, 90, '2025-06-05 17:15:36', '2025-06-06 10:38:51');
INSERT INTO `charging_orders` VALUES (72, 1, 2, '2025-06-06 10:45:07', '2025-06-06 10:45:28', 'completed', 0, 90, '2025-06-06 10:45:07', '2025-06-06 10:45:28');
INSERT INTO `charging_orders` VALUES (73, 2, 6, '2025-06-06 10:45:18', '2025-06-06 10:45:23', 'completed', 0, 90, '2025-06-06 10:45:18', '2025-06-06 10:45:23');
INSERT INTO `charging_orders` VALUES (74, 1, 1, '2025-06-06 10:45:35', '2025-06-06 10:58:59', 'completed', 0, 90, '2025-06-06 10:45:35', '2025-06-06 10:58:59');
INSERT INTO `charging_orders` VALUES (75, 2, 2, '2025-06-06 10:45:38', '2025-06-06 10:59:00', 'completed', 0, 90, '2025-06-06 10:45:38', '2025-06-06 10:59:00');
INSERT INTO `charging_orders` VALUES (76, 1, 1, '2025-06-06 10:59:06', '2025-06-06 11:17:27', 'completed', 0, 90, '2025-06-06 10:59:06', '2025-06-06 11:17:27');
INSERT INTO `charging_orders` VALUES (77, 2, 2, '2025-06-06 10:59:17', NULL, 'charging', 0, 0, '2025-06-06 10:59:17', '2025-06-06 10:59:17');
INSERT INTO `charging_orders` VALUES (78, 3, 10, '2025-06-06 10:59:22', NULL, 'charging', 0, 0, '2025-06-06 10:59:22', '2025-06-06 10:59:22');
INSERT INTO `charging_orders` VALUES (79, 4, 5, '2025-06-06 11:06:53', NULL, 'charging', 0, 0, '2025-06-06 11:06:53', '2025-06-06 11:06:53');

-- ----------------------------
-- Table structure for charging_stations
-- ----------------------------
DROP TABLE IF EXISTS `charging_stations`;
CREATE TABLE `charging_stations`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `location` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `power_output` float NULL DEFAULT NULL,
  `efficiency` float NULL DEFAULT NULL,
  `power_rating` float NULL DEFAULT NULL,
  `last_maintenance` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of charging_stations
-- ----------------------------
INSERT INTO `charging_stations` VALUES (1, '充电站-001', '位置-1', 'idle', 0, 85.784, 7.5, '2025-05-07 16:42:50', '2025-06-05 16:42:50', '2025-06-06 11:17:27');
INSERT INTO `charging_stations` VALUES (2, '充电站-002', '位置-2', 'charging', 0, 92.4562, 12, '2025-04-21 16:42:50', '2025-06-05 16:42:50', '2025-06-06 10:59:17');
INSERT INTO `charging_stations` VALUES (3, '充电站-003', '位置-3', 'idle', 0, 86.2136, 5, '2025-05-06 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_stations` VALUES (4, '充电站-004', '位置-4', 'idle', 0, 86.6262, 10, '2025-04-09 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_stations` VALUES (5, '充电站-005', '位置-5', 'charging', 0, 86.8272, 5, '2025-05-12 16:42:50', '2025-06-05 16:42:50', '2025-06-06 11:06:53');
INSERT INTO `charging_stations` VALUES (6, '充电站-006', '位置-6', 'idle', 0, 87.2964, 12, '2025-06-04 16:42:50', '2025-06-05 16:42:50', '2025-06-06 10:45:23');
INSERT INTO `charging_stations` VALUES (7, '充电站-007', '位置-7', 'idle', 0, 87.975, 5, '2025-04-06 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_stations` VALUES (8, '充电站-008', '位置-8', 'idle', 0, 88.8789, 12, '2025-04-24 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_stations` VALUES (9, '充电站-009', '位置-9', 'idle', 0, 91.0178, 12, '2025-05-14 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_stations` VALUES (10, '充电站-010', '位置-10', 'charging', 0, 95.77, 10, '2025-04-26 16:42:50', '2025-06-05 16:42:50', '2025-06-06 10:59:22');
INSERT INTO `charging_stations` VALUES (11, '充电站-011', '位置-11', 'idle', 0, 94.8842, 7.5, '2025-05-05 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_stations` VALUES (12, '充电站-012', '位置-12', 'idle', 0, 90.6492, 12, '2025-05-25 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `charging_stations` VALUES (13, '充电站-013', '位置-13', 'idle', 22, 80, 22, NULL, '2025-06-06 10:41:21', '2025-06-06 10:41:21');
INSERT INTO `charging_stations` VALUES (14, '14', '位置-14', 'idle', 33.33, 80, 33, NULL, '2025-06-06 10:58:19', '2025-06-06 10:58:19');

-- ----------------------------
-- Table structure for efficiency_logs
-- ----------------------------
DROP TABLE IF EXISTS `efficiency_logs`;
CREATE TABLE `efficiency_logs`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `station_id` int NOT NULL,
  `efficiency` float NOT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `station_id`(`station_id` ASC) USING BTREE,
  CONSTRAINT `efficiency_logs_ibfk_1` FOREIGN KEY (`station_id`) REFERENCES `charging_stations` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of efficiency_logs
-- ----------------------------
INSERT INTO `efficiency_logs` VALUES (1, 1, 84.63, '2025-05-29 06:11:40');
INSERT INTO `efficiency_logs` VALUES (2, 1, 84.24, '2025-05-29 12:11:40');
INSERT INTO `efficiency_logs` VALUES (3, 1, 86.87, '2025-05-28 18:11:40');
INSERT INTO `efficiency_logs` VALUES (4, 1, 84.13, '2025-05-28 23:11:40');
INSERT INTO `efficiency_logs` VALUES (5, 1, 88.58, '2025-05-28 06:11:40');
INSERT INTO `efficiency_logs` VALUES (6, 1, 91.42, '2025-05-28 12:11:40');
INSERT INTO `efficiency_logs` VALUES (7, 1, 93.74, '2025-05-27 18:11:40');
INSERT INTO `efficiency_logs` VALUES (8, 1, 85.1, '2025-05-27 23:11:40');
INSERT INTO `efficiency_logs` VALUES (9, 1, 87.81, '2025-05-27 06:11:40');
INSERT INTO `efficiency_logs` VALUES (10, 1, 90.59, '2025-05-27 12:11:40');

-- ----------------------------
-- Table structure for robots
-- ----------------------------
DROP TABLE IF EXISTS `robots`;
CREATE TABLE `robots`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `battery_level` float NULL DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `station_id` int NULL DEFAULT NULL,
  `last_charging` datetime NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `station_id`(`station_id` ASC) USING BTREE,
  CONSTRAINT `robots_ibfk_1` FOREIGN KEY (`station_id`) REFERENCES `charging_stations` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 21 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of robots
-- ----------------------------
INSERT INTO `robots` VALUES (1, '机器人-001', 100, 'idle', 1, '2025-06-06 11:17:27', '2025-06-05 16:42:50', '2025-06-06 11:17:27');
INSERT INTO `robots` VALUES (2, '机器人-002', 85.2996, 'charging', 2, '2025-06-06 10:59:00', '2025-06-05 16:42:50', '2025-06-06 11:17:52');
INSERT INTO `robots` VALUES (3, '机器人-003', 94.8348, 'charging', 10, '2025-05-29 16:42:50', '2025-06-05 16:42:50', '2025-06-06 11:17:52');
INSERT INTO `robots` VALUES (4, '机器人-004', 86.8624, 'charging', 5, '2025-05-21 16:42:50', '2025-06-05 16:42:50', '2025-06-06 11:17:52');
INSERT INTO `robots` VALUES (5, '机器人-005', 70.832, 'idle', NULL, '2025-06-06 10:45:25', '2025-06-05 16:42:50', '2025-06-06 10:45:25');
INSERT INTO `robots` VALUES (6, '机器人-006', 74.227, 'idle', NULL, '2025-06-06 10:45:26', '2025-06-05 16:42:50', '2025-06-06 10:45:26');
INSERT INTO `robots` VALUES (7, '机器人-007', 60.0989, 'error', NULL, '2025-05-12 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (8, '机器人-008', 100, 'idle', NULL, '2025-06-06 10:45:27', '2025-06-05 16:42:50', '2025-06-06 10:45:27');
INSERT INTO `robots` VALUES (9, '机器人-009', 88.3582, 'idle', NULL, '2025-05-07 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (10, '机器人-010', 71.722, 'idle', NULL, '2025-05-08 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (11, '机器人-011', 20.9485, 'working', NULL, '2025-05-10 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (12, '机器人-012', 88.0767, 'idle', NULL, '2025-05-17 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (13, '机器人-013', 78.3898, 'idle', NULL, '2025-05-28 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (14, '机器人-014', 25.489, 'idle', NULL, '2025-06-06 10:45:30', '2025-06-05 16:42:50', '2025-06-06 10:45:30');
INSERT INTO `robots` VALUES (15, '机器人-015', 92.8106, 'idle', NULL, '2025-05-25 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (16, '机器人-016', 67.9996, 'idle', NULL, '2025-05-23 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (17, '机器人-017', 61.5867, 'working', NULL, '2025-05-16 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (18, '机器人-018', 99.1921, 'idle', NULL, '2025-05-22 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (19, '机器人-019', 99.7879, 'idle', NULL, '2025-05-20 16:42:50', '2025-06-05 16:42:50', '2025-06-05 16:42:50');
INSERT INTO `robots` VALUES (20, '机器人-020', 100, 'idle', NULL, '2025-06-06 10:45:21', '2025-06-05 16:42:50', '2025-06-06 10:45:21');

-- ----------------------------
-- Table structure for system_alerts
-- ----------------------------
DROP TABLE IF EXISTS `system_alerts`;
CREATE TABLE `system_alerts`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` datetime NULL DEFAULT NULL,
  `type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `is_read` tinyint(1) NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_alerts
-- ----------------------------
INSERT INTO `system_alerts` VALUES (1, '2025-05-24 07:51:40', '错误', '系统检测到网络波动', 1, '2025-05-24 07:51:40');
INSERT INTO `system_alerts` VALUES (2, '2025-05-25 00:10:40', '信息', '机器人 #42 电量过低', 1, '2025-05-25 00:10:40');
INSERT INTO `system_alerts` VALUES (3, '2025-05-23 08:00:40', '错误', '系统更新可用', 0, '2025-05-23 08:00:40');
INSERT INTO `system_alerts` VALUES (4, '2025-05-26 07:23:40', '信息', '机器人 #48 电量过低', 1, '2025-05-26 07:23:40');
INSERT INTO `system_alerts` VALUES (5, '2025-05-25 19:19:40', '错误', '系统检测到网络波动', 1, '2025-05-25 19:19:40');
INSERT INTO `system_alerts` VALUES (6, '2025-05-25 19:15:40', '信息', '充电站 #11 充电效率低于阈值', 1, '2025-05-25 19:15:40');
INSERT INTO `system_alerts` VALUES (7, '2025-05-29 05:11:40', '信息', '机器人 #33 充电异常', 0, '2025-05-29 05:11:40');
INSERT INTO `system_alerts` VALUES (8, '2025-05-25 22:25:40', '警告', '数据库备份完成', 1, '2025-05-25 22:25:40');
INSERT INTO `system_alerts` VALUES (9, '2025-05-26 22:41:40', '信息', '机器人 #26 完成充电', 1, '2025-05-26 22:41:40');
INSERT INTO `system_alerts` VALUES (10, '2025-05-28 13:17:40', '信息', '机器人 #5 充电异常', 0, '2025-05-28 13:17:40');

-- ----------------------------
-- Table structure for system_logs
-- ----------------------------
DROP TABLE IF EXISTS `system_logs`;
CREATE TABLE `system_logs`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NULL DEFAULT NULL,
  `action` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `details` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `system_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_logs
-- ----------------------------
INSERT INTO `system_logs` VALUES (1, 1, '导出报表', NULL, '2025-05-09 21:15:40');
INSERT INTO `system_logs` VALUES (2, 1, '删除充电站 #10', '永久删除记录', '2025-05-13 04:40:40');
INSERT INTO `system_logs` VALUES (3, 2, '备份数据库', NULL, '2025-05-29 01:07:40');
INSERT INTO `system_logs` VALUES (4, 1, '登录系统', 'IP地址: 23.48.209.63', '2025-05-18 05:46:40');
INSERT INTO `system_logs` VALUES (5, 2, '查看机器人列表', NULL, '2025-05-02 20:33:40');
INSERT INTO `system_logs` VALUES (6, 2, '导出报表', NULL, '2025-05-12 22:47:40');
INSERT INTO `system_logs` VALUES (7, 1, '导出报表', NULL, '2025-05-19 11:27:40');
INSERT INTO `system_logs` VALUES (8, 2, '重启服务', NULL, '2025-05-12 18:31:40');
INSERT INTO `system_logs` VALUES (9, NULL, '查看机器人列表', NULL, '2025-04-30 05:16:40');
INSERT INTO `system_logs` VALUES (10, 1, '查看订单详情 #42', NULL, '2025-04-30 06:35:40');
INSERT INTO `system_logs` VALUES (11, 2, '删除充电站 #6', '永久删除记录', '2025-05-12 16:45:40');
INSERT INTO `system_logs` VALUES (12, 2, '删除充电站 #10', '永久删除记录', '2025-05-01 09:20:40');
INSERT INTO `system_logs` VALUES (13, 2, '删除充电站 #11', '永久删除记录', '2025-05-08 02:26:40');
INSERT INTO `system_logs` VALUES (14, 2, '删除充电站 #8', '永久删除记录', '2025-05-10 22:00:40');
INSERT INTO `system_logs` VALUES (15, 2, '删除充电站 #4', '永久删除记录', '2025-05-09 17:18:40');
INSERT INTO `system_logs` VALUES (16, 2, '查看订单详情 #32', NULL, '2025-05-16 22:26:40');
INSERT INTO `system_logs` VALUES (17, 2, '重启服务', NULL, '2025-05-19 09:55:40');
INSERT INTO `system_logs` VALUES (18, 2, '添加充电站', '操作时间: 2025-05-26 18:51:02', '2025-04-29 01:19:40');
INSERT INTO `system_logs` VALUES (19, 2, '登录系统', 'IP地址: 117.80.50.169', '2025-05-27 07:20:40');
INSERT INTO `system_logs` VALUES (20, 2, '导出报表', NULL, '2025-04-29 20:34:40');

-- ----------------------------
-- Table structure for system_settings
-- ----------------------------
DROP TABLE IF EXISTS `system_settings`;
CREATE TABLE `system_settings`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `setting_value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `updated_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `setting_key`(`setting_key` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_settings
-- ----------------------------
INSERT INTO `system_settings` VALUES (1, 'system_name', '货仓机器人激光充电和能效管理云平台', '系统名称，显示在界面顶部', '2025-05-29 14:11:40');
INSERT INTO `system_settings` VALUES (2, 'mqtt_server', 'localhost', 'MQTT服务器地址，用于与充电站和机器人通信', '2025-05-29 14:11:40');
INSERT INTO `system_settings` VALUES (3, 'mqtt_port', '1883', 'MQTT服务器端口，标准端口为1883', '2025-05-29 14:11:40');
INSERT INTO `system_settings` VALUES (4, 'refresh_interval', '5', '数据刷新间隔（秒），控制前端自动刷新数据的频率', '2025-05-29 14:11:40');
INSERT INTO `system_settings` VALUES (5, 'alert_threshold', '20', '告警阈值（百分比），当充电效率低于此值时触发告警', '2025-05-29 14:11:40');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `role` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `created_at` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (1, 'admin', 'scrypt:32768:8:1$2bQOPt3Ru4Bd1GRR$7336be0fd7a6f81527d85c96f12cd3650b32b2cd9571924ec7156e8f1c547e326a583bc03bc7eac091319d941a0a6234c73ae0576b90d1f565b62d3af3439aaa', 'admin', '2025-06-05 16:42:50');
INSERT INTO `users` VALUES (2, 'user123', 'scrypt:32768:8:1$2bQOPt3Ru4Bd1GRR$7336be0fd7a6f81527d85c96f12cd3650b32b2cd9571924ec7156e8f1c547e326a583bc03bc7eac091319d941a0a6234c73ae0576b90d1f565b62d3af3439aaa', 'user', '2025-06-06 18:28:03');

SET FOREIGN_KEY_CHECKS = 1;
