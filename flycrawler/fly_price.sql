/*
Navicat MySQL Data Transfer

Source Server         : 192.168.110.94
Source Server Version : 50722
Source Host           : 192.168.110.94:3306
Source Database       : spider_db

Target Server Type    : MYSQL
Target Server Version : 50722
File Encoding         : 65001

Date: 2018-05-23 19:48:03
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for fly_price
-- ----------------------------
DROP TABLE IF EXISTS `fly_price`;
CREATE TABLE `fly_price` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `airline` varchar(20) NOT NULL DEFAULT '',
  `save_date` datetime NOT NULL,
  `fromdis` varchar(20) NOT NULL,
  `todis` varchar(20) NOT NULL,
  `departingtime` varchar(40) NOT NULL,
  `price` decimal(8,2) DEFAULT NULL,
  `content` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8;
