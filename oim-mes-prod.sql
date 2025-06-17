/*
 Navicat Premium Data Transfer

 Source Server         : 傲雷
 Source Server Type    : MySQL
 Source Server Version : 80025 (8.0.25)
 Source Host           : rm-wz92v0p5r77n91210wo.mysql.rds.aliyuncs.com:3306
 Source Schema         : oim-mes-prod

 Target Server Type    : MySQL
 Target Server Version : 80025 (8.0.25)
 File Encoding         : 65001

 Date: 08/06/2025 02:46:42
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for abnormal_management_rework
-- ----------------------------
DROP TABLE IF EXISTS `abnormal_management_rework`;
CREATE TABLE `abnormal_management_rework` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bill_no` varchar(30) DEFAULT NULL COMMENT '工单号',
  `material_code` varchar(50) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) DEFAULT NULL COMMENT '物料名称',
  `rework_qty` int DEFAULT NULL COMMENT '返工数量',
  `complete_qty` int DEFAULT NULL COMMENT '完成数量',
  `rework_status` tinyint DEFAULT '0' COMMENT '状态 0-未开单 1-已开单 2-进行中 3-已完成',
  `rework_reason` text COMMENT '返工原因',
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='不良品管理-返工';

-- ----------------------------
-- Table structure for ads_group_strategy_indicators_desc
-- ----------------------------
DROP TABLE IF EXISTS `ads_group_strategy_indicators_desc`;
CREATE TABLE `ads_group_strategy_indicators_desc` (
  `index_encode` varchar(100) NOT NULL COMMENT '指标编码',
  `index_desc` text COMMENT '指标描述',
  PRIMARY KEY (`index_encode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='PBC指标描述';

-- ----------------------------
-- Table structure for ads_group_strategy_indicators_progress
-- ----------------------------
DROP TABLE IF EXISTS `ads_group_strategy_indicators_progress`;
CREATE TABLE `ads_group_strategy_indicators_progress` (
  `year_time` varchar(20) NOT NULL COMMENT '年份',
  `index_encode` varchar(100) NOT NULL COMMENT '指标编码',
  `index_value` text COMMENT '指标值',
  `dept_id` varchar(50) DEFAULT NULL COMMENT '部门ID',
  `dept_name` varchar(100) DEFAULT NULL COMMENT '部门名称',
  `update_ds` varchar(20) NOT NULL COMMENT '更新日期',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`year_time`,`index_encode`,`update_ds`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='PBC指标汇总';

-- ----------------------------
-- Table structure for bar_code_bind
-- ----------------------------
DROP TABLE IF EXISTS `bar_code_bind`;
CREATE TABLE `bar_code_bind` (
  `id` bigint NOT NULL,
  `rule_id` bigint DEFAULT NULL COMMENT '条码规则ID',
  `object_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '绑定对象',
  `object_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '对象名称',
  `object_type` tinyint DEFAULT NULL COMMENT '对象类型 0-组织 1-产品',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `un_object_code_rule_id` (`rule_id`,`object_code`) USING BTREE,
  KEY `index_object_code` (`object_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='条码规则绑定对象';

-- ----------------------------
-- Table structure for bar_code_expression
-- ----------------------------
DROP TABLE IF EXISTS `bar_code_expression`;
CREATE TABLE `bar_code_expression` (
  `id` bigint NOT NULL,
  `expression_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '表达式名称',
  `expression_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '表达式CODE',
  `expression_value` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '表达式VALUE',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='规则表达式';

-- ----------------------------
-- Table structure for bar_code_history
-- ----------------------------
DROP TABLE IF EXISTS `bar_code_history`;
CREATE TABLE `bar_code_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `rule_id` bigint DEFAULT NULL,
  `bar_code` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '条码',
  `rule_type_id` bigint DEFAULT NULL COMMENT '规则类型ID',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_bar_code` (`rule_id`,`bar_code`,`rule_type_id`) USING BTREE,
  KEY `idx_ruleid_createtime` (`rule_id`,`create_time`)
) ENGINE=InnoDB AUTO_INCREMENT=1931418416363827204 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='生成条码记录';

-- ----------------------------
-- Table structure for bar_code_month_code
-- ----------------------------
DROP TABLE IF EXISTS `bar_code_month_code`;
CREATE TABLE `bar_code_month_code` (
  `id` bigint NOT NULL,
  `month_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '月份代码',
  `month` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '月',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_month` (`month`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='月份代码';

-- ----------------------------
-- Table structure for bar_code_reset
-- ----------------------------
DROP TABLE IF EXISTS `bar_code_reset`;
CREATE TABLE `bar_code_reset` (
  `id` bigint NOT NULL,
  `reset_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '复位名称',
  `reset_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '复位方式CODE',
  `sys_inlay` tinyint(1) DEFAULT NULL COMMENT '系统内置   0：是  1：否',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_reset_code` (`reset_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='复位方式';

-- ----------------------------
-- Table structure for bar_code_rule
-- ----------------------------
DROP TABLE IF EXISTS `bar_code_rule`;
CREATE TABLE `bar_code_rule` (
  `id` bigint NOT NULL COMMENT 'id',
  `rule_type_id` bigint DEFAULT NULL COMMENT '规则类型ID',
  `rule_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '规则编码',
  `rule_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '规则名称',
  `rule_prefix` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '规则前缀',
  `rule_suffix` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '规则后缀',
  `min_sequence` int DEFAULT NULL COMMENT '最小序列号',
  `max_sequence` int DEFAULT NULL COMMENT '最大序列号',
  `sequence_length` int DEFAULT NULL COMMENT '序列号长度',
  `current_sequence` int DEFAULT NULL COMMENT '当前序列号',
  `increment_by` int DEFAULT '1' COMMENT '递增数量 默认为1',
  `rule_sample` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '样例',
  `reset` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '复位方式',
  `is_default` tinyint(1) DEFAULT '1' COMMENT '默认  0:是 1:否',
  `last_sequence` int DEFAULT NULL COMMENT '最近一次生成序列号',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_rule_code` (`rule_code`) USING BTREE,
  UNIQUE KEY `idx_uk_prefix` (`rule_prefix`,`rule_suffix`,`sequence_length`,`rule_type_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='条码规则';

-- ----------------------------
-- Table structure for bar_code_type
-- ----------------------------
DROP TABLE IF EXISTS `bar_code_type`;
CREATE TABLE `bar_code_type` (
  `id` bigint NOT NULL,
  `type_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '类型名称',
  `type_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '类型编码',
  `type_flag` tinyint(1) DEFAULT NULL COMMENT '类型标识 0-组织  1-产品',
  `sys_inlay` tinyint(1) DEFAULT '0' COMMENT '系统内置   0：是  1：否',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='条码类型';

-- ----------------------------
-- Table structure for bar_code_year_code
-- ----------------------------
DROP TABLE IF EXISTS `bar_code_year_code`;
CREATE TABLE `bar_code_year_code` (
  `id` bigint NOT NULL,
  `year_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '年份代码',
  `year` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '年',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_year` (`year`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='年份代码';

-- ----------------------------
-- Table structure for base_assembly_line_info
-- ----------------------------
DROP TABLE IF EXISTS `base_assembly_line_info`;
CREATE TABLE `base_assembly_line_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `assembly_line_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别代码',
  `assembly_line_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '线别',
  `begin_time` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '开始时间',
  `end_time` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '结束时间',
  `assembly_line_effective` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别有效期',
  `resource_id` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '资源id',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_assembly_line_code` (`assembly_line_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1924361554688696324 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='线别列表';

-- ----------------------------
-- Table structure for base_attendance_record
-- ----------------------------
DROP TABLE IF EXISTS `base_attendance_record`;
CREATE TABLE `base_attendance_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `clock_in_time` datetime DEFAULT NULL COMMENT '打卡时间',
  `device_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '设备编号',
  `user_no` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '员工工号',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `clock_in_time_idx` (`clock_in_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1931413420515749896 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='临时工考勤记录';

-- ----------------------------
-- Table structure for base_bom_material_info
-- ----------------------------
DROP TABLE IF EXISTS `base_bom_material_info`;
CREATE TABLE `base_bom_material_info` (
  `id` bigint NOT NULL,
  `bom_code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'bom 编码',
  `bom_material_code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'bom物料编码',
  `qty` decimal(10,3) DEFAULT '0.000' COMMENT '数量',
  `unit` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '' COMMENT '单位',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '1001' COMMENT '租户编码',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='bom物料信息信息';

-- ----------------------------
-- Table structure for base_container_capacity
-- ----------------------------
DROP TABLE IF EXISTS `base_container_capacity`;
CREATE TABLE `base_container_capacity` (
  `id` bigint NOT NULL,
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `capacity` bigint DEFAULT NULL COMMENT '不同物料的容器容量',
  `container_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '容器类型名称',
  `container_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '容器编码',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_uk_material_container_code` (`material_code`,`container_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='物料绑定不同容器：容器的容量';

-- ----------------------------
-- Table structure for base_ctrl_process
-- ----------------------------
DROP TABLE IF EXISTS `base_ctrl_process`;
CREATE TABLE `base_ctrl_process` (
  `id` bigint NOT NULL,
  `assemble_process` tinyint DEFAULT '0' COMMENT '组装扫描工序验证 0-关闭 1-开启',
  `fqc_process` tinyint DEFAULT '0' COMMENT 'FQC扫描验证 0-关闭 1-开启',
  `package_process` tinyint DEFAULT '0' COMMENT '称重包装扫描验证 0-关闭 1-开启',
  `rework_process` tinyint DEFAULT '1' COMMENT '验证返工单物料是否一致 0-关闭 1-开启',
  `supplier_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商名称',
  `supplier_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商id',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_process_supplier_id` (`supplier_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='工序控制表';

-- ----------------------------
-- Table structure for base_dict_data
-- ----------------------------
DROP TABLE IF EXISTS `base_dict_data`;
CREATE TABLE `base_dict_data` (
  `id` bigint NOT NULL COMMENT 'id序号',
  `dict_type_id` bigint DEFAULT NULL COMMENT '字典类型id',
  `dict_type` varchar(50) DEFAULT NULL COMMENT '字典类型',
  `dict_label` varchar(50) DEFAULT NULL COMMENT '数据标签',
  `dict_value` varchar(500) DEFAULT NULL COMMENT '字典数据',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `idx_dict_type` (`dict_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='数据字典';

-- ----------------------------
-- Table structure for base_dict_type
-- ----------------------------
DROP TABLE IF EXISTS `base_dict_type`;
CREATE TABLE `base_dict_type` (
  `id` bigint NOT NULL COMMENT '字典类型id',
  `dict_type` varchar(50) DEFAULT NULL COMMENT '字典类型',
  `dict_name` varchar(50) DEFAULT NULL COMMENT '字典名称',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_dict_type` (`dict_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='字典类型';

-- ----------------------------
-- Table structure for base_factory_info
-- ----------------------------
DROP TABLE IF EXISTS `base_factory_info`;
CREATE TABLE `base_factory_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `factory_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '工厂代码',
  `factory_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '工厂名称',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_factory_code` (`factory_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1924361037392601092 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工厂信息';

-- ----------------------------
-- Table structure for base_factory_worker
-- ----------------------------
DROP TABLE IF EXISTS `base_factory_worker`;
CREATE TABLE `base_factory_worker` (
  `id` bigint NOT NULL,
  `job_number` varchar(32) NOT NULL DEFAULT '' COMMENT '工号',
  `worker_name` varchar(64) NOT NULL DEFAULT '' COMMENT '名称',
  `factory_code` varchar(32) NOT NULL DEFAULT '' COMMENT '工厂编号',
  `factory_nme` varchar(200) NOT NULL DEFAULT '' COMMENT '工厂名称',
  `workshop_name` varchar(64) NOT NULL DEFAULT '' COMMENT '车间名称',
  `workshop_id` bigint NOT NULL DEFAULT '0' COMMENT '车间ID',
  `line_code` varchar(64) NOT NULL DEFAULT '' COMMENT '线别编码',
  `line_name` varchar(64) NOT NULL DEFAULT '' COMMENT '线别名称',
  `creator` bigint NOT NULL DEFAULT '0' COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint NOT NULL DEFAULT '0' COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) NOT NULL DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工厂工人信息';

-- ----------------------------
-- Table structure for base_laser_drawing
-- ----------------------------
DROP TABLE IF EXISTS `base_laser_drawing`;
CREATE TABLE `base_laser_drawing` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '机型名称',
  `drawing_type` varchar(20) DEFAULT NULL COMMENT '图纸类别',
  `drawing_refer_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '图纸参照',
  `original_drawing_url` varchar(500) DEFAULT NULL COMMENT '原图纸',
  `cad_drawing_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'CAD图纸',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `idx_material_code` (`material_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1930878013264850948 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='镭雕图纸';

-- ----------------------------
-- Table structure for base_laser_info
-- ----------------------------
DROP TABLE IF EXISTS `base_laser_info`;
CREATE TABLE `base_laser_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `laser_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '镭雕机名称',
  `laser_command` varchar(30) DEFAULT NULL COMMENT '镭雕机指令',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1687019654587723779 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='镭雕机';

-- ----------------------------
-- Table structure for base_material_detail_list
-- ----------------------------
DROP TABLE IF EXISTS `base_material_detail_list`;
CREATE TABLE `base_material_detail_list` (
  `id` bigint NOT NULL,
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '父项物料编码',
  `posnr` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目号',
  `postp` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '项目类别 L=库存物料 N=其他',
  `idnrk` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '组件',
  `menge` decimal(10,3) DEFAULT NULL COMMENT '数量',
  `meins` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '单位',
  `ausch` decimal(5,2) DEFAULT NULL COMMENT '组件报废率',
  `itsob` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '特殊采购 跳号物料=50',
  `dumps` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '虚拟项目',
  `alpgr` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备选项目组',
  `alprf` int DEFAULT NULL COMMENT '优先级',
  `alpst` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '策略',
  `ewahr` decimal(5,2) DEFAULT NULL COMMENT '使用概率',
  `lgort` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '存储地点',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_matnr_posnr` (`matnr`,`posnr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='SAP BOM明细';

-- ----------------------------
-- Table structure for base_material_group
-- ----------------------------
DROP TABLE IF EXISTS `base_material_group`;
CREATE TABLE `base_material_group` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `material_group` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料组',
  `category_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料类别编码',
  `category_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料类别名称',
  `material_desc` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料组描述',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `index_group` (`material_group`) USING BTREE,
  KEY `index_code` (`category_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=327 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='物料组数据';

-- ----------------------------
-- Table structure for base_material_info
-- ----------------------------
DROP TABLE IF EXISTS `base_material_info`;
CREATE TABLE `base_material_info` (
  `id` bigint NOT NULL,
  `material_code` varchar(40) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) DEFAULT NULL COMMENT '物料名称',
  `material_name_en` varchar(200) DEFAULT NULL COMMENT '物料名称（英文）',
  `specification_model` varchar(255) DEFAULT NULL COMMENT '物料规格',
  `specification_model_en` varchar(255) DEFAULT NULL COMMENT '物料规格（英文）',
  `complete_material_name` varchar(255) DEFAULT NULL COMMENT '物料完整中文名称',
  `complete_material_name_en` varchar(255) DEFAULT NULL COMMENT '物料完整英文名称',
  `material_type` varchar(5) DEFAULT NULL COMMENT '物料类型 Z000-成品，Z001-主机，Z002-半成品，Z003-原料，Z005-宣传品，Z006-电子料，Z008-辅料',
  `mbrsh` varchar(128) DEFAULT NULL COMMENT '行业领域 M:傲雷集团',
  `meins` varchar(128) DEFAULT NULL COMMENT '基本计量单位',
  `cost` decimal(10,2) DEFAULT '0.00' COMMENT '成本价格',
  `peinh` int DEFAULT '0' COMMENT '价格单位',
  `matkl` varchar(128) DEFAULT NULL COMMENT '物料组',
  `old_material_code` varchar(40) DEFAULT NULL COMMENT '旧物料编码',
  `extwg` varchar(18) DEFAULT NULL COMMENT '外部物料组',
  `spart` varchar(2) DEFAULT NULL COMMENT '产品组',
  `mstae` varchar(128) DEFAULT NULL COMMENT '跨工厂的物料状态',
  `mstde` varchar(12) DEFAULT NULL COMMENT '有效起始期',
  `mtpos_mara` varchar(4) DEFAULT NULL COMMENT '普通项目类别',
  `brgew` decimal(10,3) DEFAULT NULL COMMENT '毛重',
  `gewei` varchar(3) DEFAULT NULL COMMENT '毛重单位',
  `ntgew` decimal(10,3) DEFAULT NULL COMMENT '净重',
  `volum` decimal(10,3) DEFAULT NULL COMMENT '体积',
  `voleh` varchar(3) DEFAULT NULL COMMENT '体积单位',
  `groes` varchar(32) DEFAULT NULL COMMENT '大小/量纲',
  `laeng` decimal(10,3) DEFAULT NULL COMMENT '长度',
  `breit` decimal(10,3) DEFAULT NULL COMMENT '宽度',
  `hoehe` decimal(10,3) DEFAULT NULL COMMENT '高度',
  `meabm` varchar(3) DEFAULT NULL COMMENT '长宽高计量单位',
  `ean11` varchar(18) DEFAULT NULL COMMENT 'EAN/UPC码',
  `numtp` varchar(3) DEFAULT NULL COMMENT 'EAN类别',
  `werks` varchar(4) DEFAULT NULL COMMENT '工厂代码',
  `xchpf` varchar(2) DEFAULT NULL COMMENT '是否批次管理',
  `ekgrp` varchar(128) DEFAULT NULL COMMENT '采购组',
  `webaz` decimal(10,0) DEFAULT NULL COMMENT '收货处理时间',
  `beskz` varchar(2) DEFAULT NULL COMMENT '采购类型 E:制造 F:采购 X:均可',
  `sobsl` varchar(3) DEFAULT NULL COMMENT '特殊采购类',
  `lgpro` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产存储地点',
  `lgfsb` varchar(4) DEFAULT NULL COMMENT '外购存储地点',
  `ersda` varchar(15) DEFAULT NULL COMMENT '创建日期',
  `ertim` varchar(10) DEFAULT NULL COMMENT '创建时间',
  `laeda` varchar(15) DEFAULT NULL COMMENT '修改日期',
  `latim` varchar(10) DEFAULT NULL COMMENT '修改时间',
  `urgency_material_bom` bit(1) DEFAULT b'0' COMMENT '是否紧急BOM(0:否 1:是)',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT NULL COMMENT '租户编码',
  `material_mpq` decimal(16,0) NOT NULL DEFAULT '0' COMMENT '最小单位值',
  `matkl_name` varchar(250) DEFAULT NULL COMMENT '物料组名称',
  `plan_delivery_day` int NOT NULL DEFAULT '0' COMMENT '计划交货时间(天)',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_matnr` (`material_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='物料基础数据';

-- ----------------------------
-- Table structure for base_material_info_2
-- ----------------------------
DROP TABLE IF EXISTS `base_material_info_2`;
CREATE TABLE `base_material_info_2` (
  `id` bigint NOT NULL,
  `material_code` varchar(40) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) DEFAULT NULL COMMENT '物料名称',
  `material_name_en` varchar(200) DEFAULT NULL COMMENT '物料名称（英文）',
  `specification_model` varchar(255) DEFAULT NULL COMMENT '物料规格',
  `specification_model_en` varchar(255) DEFAULT NULL COMMENT '物料规格（英文）',
  `complete_material_name` varchar(255) DEFAULT NULL COMMENT '物料完整中文名称',
  `complete_material_name_en` varchar(255) DEFAULT NULL COMMENT '物料完整英文名称',
  `material_type` varchar(5) DEFAULT NULL COMMENT '物料类型 Z000-成品，Z001-主机，Z002-半成品，Z003-原料，Z005-宣传品，Z006-电子料，Z008-辅料',
  `mbrsh` varchar(2) DEFAULT NULL COMMENT '行业领域 M:傲雷集团',
  `meins` varchar(3) DEFAULT NULL COMMENT '基本计量单位',
  `cost` decimal(10,2) DEFAULT '0.00' COMMENT '成本价格',
  `peinh` int DEFAULT '0' COMMENT '价格单位',
  `matkl` varchar(9) DEFAULT NULL COMMENT '物料组',
  `old_material_code` varchar(40) DEFAULT NULL COMMENT '旧物料编码',
  `extwg` varchar(18) DEFAULT NULL COMMENT '外部物料组',
  `spart` varchar(2) DEFAULT NULL COMMENT '产品组',
  `mstae` varchar(2) DEFAULT NULL COMMENT '跨工厂的物料状态',
  `mstde` varchar(12) DEFAULT NULL COMMENT '有效起始期',
  `mtpos_mara` varchar(4) DEFAULT NULL COMMENT '普通项目类别',
  `brgew` decimal(10,3) DEFAULT NULL COMMENT '毛重',
  `gewei` varchar(3) DEFAULT NULL COMMENT '毛重单位',
  `ntgew` decimal(10,3) DEFAULT NULL COMMENT '净重',
  `volum` decimal(10,3) DEFAULT NULL COMMENT '体积',
  `voleh` varchar(3) DEFAULT NULL COMMENT '体积单位',
  `groes` varchar(32) DEFAULT NULL COMMENT '大小/量纲',
  `laeng` decimal(10,3) DEFAULT NULL COMMENT '长度',
  `breit` decimal(10,3) DEFAULT NULL COMMENT '宽度',
  `hoehe` decimal(10,3) DEFAULT NULL COMMENT '高度',
  `meabm` varchar(3) DEFAULT NULL COMMENT '长宽高计量单位',
  `ean11` varchar(18) DEFAULT NULL COMMENT 'EAN/UPC码',
  `numtp` varchar(3) DEFAULT NULL COMMENT 'EAN类别',
  `werks` varchar(4) DEFAULT NULL COMMENT '工厂代码',
  `xchpf` varchar(2) DEFAULT NULL COMMENT '是否批次管理',
  `ekgrp` varchar(3) DEFAULT NULL COMMENT '采购组',
  `webaz` decimal(10,0) DEFAULT NULL COMMENT '收货处理时间',
  `beskz` varchar(2) DEFAULT NULL COMMENT '采购类型 E:制造 F:采购 X:均可',
  `sobsl` varchar(3) DEFAULT NULL COMMENT '特殊采购类',
  `lgpro` varchar(4) DEFAULT NULL COMMENT '生产存储地点',
  `lgfsb` varchar(4) DEFAULT NULL COMMENT '外购存储地点',
  `ersda` varchar(15) DEFAULT NULL COMMENT '创建日期',
  `ertim` varchar(10) DEFAULT NULL COMMENT '创建时间',
  `laeda` varchar(15) DEFAULT NULL COMMENT '修改日期',
  `latim` varchar(10) DEFAULT NULL COMMENT '修改时间',
  `urgency_material_bom` bit(1) DEFAULT b'0' COMMENT '是否紧急BOM(0:否 1:是)',
  `matkl_name` varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料组名称',
  `material_mpq` decimal(16,4) DEFAULT '0.0000' COMMENT '最小单位值',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_matnr` (`material_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='物料基础数据';

-- ----------------------------
-- Table structure for base_material_label
-- ----------------------------
DROP TABLE IF EXISTS `base_material_label`;
CREATE TABLE `base_material_label` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_code` varchar(50) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `structure_chart_url` varchar(255) DEFAULT NULL COMMENT '产品结构图',
  `supplier_logo_url` varchar(255) DEFAULT NULL COMMENT '供应商logo',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_material_code` (`material_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1849805009701089283 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='物料标签';

-- ----------------------------
-- Table structure for base_material_list
-- ----------------------------
DROP TABLE IF EXISTS `base_material_list`;
CREATE TABLE `base_material_list` (
  `id` bigint NOT NULL,
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `werks` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂',
  `stlan` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'BOM用途 固定为1',
  `stlal` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备选物料清单',
  `stlty` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'BOM类型 M=生产标准BOM',
  `stlnr` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料单号',
  `datuv` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '有效期',
  `bmeng` decimal(10,3) DEFAULT NULL COMMENT '基本数量',
  `bmein` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基本数量单位',
  `stlst` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料清单状态',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_matnr_stlal` (`matnr`,`stlal`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='SAP BOM主表';

-- ----------------------------
-- Table structure for base_oa_general_enum
-- ----------------------------
DROP TABLE IF EXISTS `base_oa_general_enum`;
CREATE TABLE `base_oa_general_enum` (
  `id` bigint NOT NULL,
  `master_data_type` varchar(64) NOT NULL DEFAULT '' COMMENT '数据类型，标明当前行属于那个主数据',
  `data_code` varchar(128) NOT NULL DEFAULT '' COMMENT '编号',
  `data_name` varchar(64) NOT NULL DEFAULT '' COMMENT '编号对应的名称',
  `oa_status` tinyint NOT NULL DEFAULT '0' COMMENT 'OA数据状态；0启用1禁用',
  `creator` bigint NOT NULL DEFAULT '0' COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint NOT NULL DEFAULT '0' COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) NOT NULL DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='OA主数据枚举表';

-- ----------------------------
-- Table structure for base_produce_container
-- ----------------------------
DROP TABLE IF EXISTS `base_produce_container`;
CREATE TABLE `base_produce_container` (
  `id` bigint NOT NULL,
  `container_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '容器编码',
  `container_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '容器名称',
  `container_unit` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '容器单位',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_container_code` (`container_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='基础数据：容器类型表';

-- ----------------------------
-- Table structure for base_produce_shift
-- ----------------------------
DROP TABLE IF EXISTS `base_produce_shift`;
CREATE TABLE `base_produce_shift` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `shift_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '班制名称',
  `shift_description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '班制说明',
  `valid_time` decimal(4,2) DEFAULT NULL COMMENT '上班时间',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_shift_name` (`shift_name`)
) ENGINE=InnoDB AUTO_INCREMENT=1916474231096856580 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产班制信息';

-- ----------------------------
-- Table structure for base_produce_shift_detail
-- ----------------------------
DROP TABLE IF EXISTS `base_produce_shift_detail`;
CREATE TABLE `base_produce_shift_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `shift_id` bigint DEFAULT NULL COMMENT '班制id',
  `shift_detail_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '班次名称',
  `begin_time` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '开始时间',
  `end_time` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '结束时间',
  `serial` int NOT NULL COMMENT '序号',
  `is_cross_day` tinyint DEFAULT NULL COMMENT '是否跨天',
  `shift_detail_description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '描述',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1916474231134605316 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产班次';

-- ----------------------------
-- Table structure for base_product_make_big
-- ----------------------------
DROP TABLE IF EXISTS `base_product_make_big`;
CREATE TABLE `base_product_make_big` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料名称',
  `process_url` varchar(100) DEFAULT NULL COMMENT '工艺流程图',
  `fixture_list_url` varchar(100) DEFAULT NULL COMMENT '治具清单',
  `fixture_drawing_url` varchar(100) DEFAULT NULL COMMENT '治具图纸',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1930803744224800771 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品制造包';

-- ----------------------------
-- Table structure for base_production_threshold
-- ----------------------------
DROP TABLE IF EXISTS `base_production_threshold`;
CREATE TABLE `base_production_threshold` (
  `id` bigint NOT NULL,
  `threshold` int DEFAULT NULL COMMENT '阈值',
  `min_value` float(21,4) DEFAULT NULL COMMENT '产品重量最小值（单位：g）',
  `max_value` float(21,4) DEFAULT NULL COMMENT '产品重量最大值（单位：g）',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL,
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `update_name` varchar(30) DEFAULT NULL,
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_threshold_min_value` (`min_value`),
  KEY `idx_threshold_max_value` (`max_value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='产品重量阈值表';

-- ----------------------------
-- Table structure for base_rejects_code
-- ----------------------------
DROP TABLE IF EXISTS `base_rejects_code`;
CREATE TABLE `base_rejects_code` (
  `id` bigint NOT NULL COMMENT '主键ID',
  `rejects_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良代码编码',
  `rejects_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良代码名称',
  `bad_category` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '类别： 失败品 F 缺陷品 D 返修品 R',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '描述',
  `status` tinyint DEFAULT NULL COMMENT '状态 0-启用 1-禁用',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  PRIMARY KEY (`id`) USING BTREE,
  KEY ```idx_rejects_code` (`rejects_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='不良代码表';

-- ----------------------------
-- Table structure for base_rejects_type
-- ----------------------------
DROP TABLE IF EXISTS `base_rejects_type`;
CREATE TABLE `base_rejects_type` (
  `id` bigint NOT NULL,
  `level_one_type` varchar(2) DEFAULT NULL COMMENT '一级不良类别 I-来料不良 P-成品反馈不良 Z-制程不良',
  `level_two_type` varchar(3) DEFAULT NULL COMMENT '二级不良类别 W-外观不良 A-安全类不良 G-功能类不良 K-可靠性不良',
  `rejects_type_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良代码类型名称',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '描述',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='不良代码类型表';

-- ----------------------------
-- Table structure for base_rejects_type_code
-- ----------------------------
DROP TABLE IF EXISTS `base_rejects_type_code`;
CREATE TABLE `base_rejects_type_code` (
  `id` bigint NOT NULL,
  `rejects_code_id` bigint DEFAULT NULL COMMENT '不良代码主键',
  `rejects_type_id` bigint DEFAULT NULL COMMENT '不良代码类型主键',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_rejects_code_id` (`rejects_code_id`) USING BTREE,
  KEY `idx_rejects_type_id` (`rejects_type_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='不良代码类型对应不良代码的中间表';

-- ----------------------------
-- Table structure for base_rejects_type_procedure
-- ----------------------------
DROP TABLE IF EXISTS `base_rejects_type_procedure`;
CREATE TABLE `base_rejects_type_procedure` (
  `id` bigint NOT NULL,
  `rejects_type_id` bigint DEFAULT NULL COMMENT '不良代码类型主键',
  `procedure_id` bigint DEFAULT NULL COMMENT '工序主键',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_rejects_type_id` (`rejects_type_id`) USING BTREE,
  KEY `idx_procedure_id` (`procedure_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='不良代码类型对应工序的中间表';

-- ----------------------------
-- Table structure for base_work_process
-- ----------------------------
DROP TABLE IF EXISTS `base_work_process`;
CREATE TABLE `base_work_process` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `factory_code` varchar(4) DEFAULT '2000' COMMENT '工厂编码',
  `work_process_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '工序名称',
  `work_process_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序编码',
  `work_process_type_id` bigint DEFAULT NULL COMMENT '工序类型id',
  `work_process_status` tinyint DEFAULT '0' COMMENT '工序状态',
  `resource_type_id` bigint DEFAULT NULL COMMENT '资源类型id',
  `default_resource_id_binding` bigint DEFAULT NULL COMMENT '工序默认绑定资源id',
  `is_collection_workstation` tinyint DEFAULT '0' COMMENT '是否采集工位',
  `is_current_version` tinyint DEFAULT '0' COMMENT '是否当前版本',
  `work_process_description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序描述',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_work_process_name` (`work_process_name`),
  UNIQUE KEY `idx_uk_work_process_code` (`work_process_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1785557770728173571 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工序信息';

-- ----------------------------
-- Table structure for base_work_process_type
-- ----------------------------
DROP TABLE IF EXISTS `base_work_process_type`;
CREATE TABLE `base_work_process_type` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `factory_code` varchar(4) DEFAULT '2000' COMMENT '工厂编码',
  `work_process_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '工序类型',
  `work_process_type_description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序类型描述',
  `workstation_id` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工位id',
  `assignable_workstation` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '可分配工位',
  `assigned_workstation` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '已分配工位',
  `process_type_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序编码',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_work_process_type` (`work_process_type`)
) ENGINE=InnoDB AUTO_INCREMENT=1830872079370272771 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工序类型';

-- ----------------------------
-- Table structure for base_workshop_info
-- ----------------------------
DROP TABLE IF EXISTS `base_workshop_info`;
CREATE TABLE `base_workshop_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `workshop_code` varchar(100) DEFAULT NULL COMMENT '车间编码',
  `workshop_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '车间名称',
  `factory_id` bigint DEFAULT NULL COMMENT '工厂id',
  `shift_id` bigint DEFAULT NULL COMMENT '班制id',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_workshop_name` (`workshop_name`)
) ENGINE=InnoDB AUTO_INCREMENT=1924361874638594051 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='车间信息';

-- ----------------------------
-- Table structure for base_workshop_line
-- ----------------------------
DROP TABLE IF EXISTS `base_workshop_line`;
CREATE TABLE `base_workshop_line` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `workshop_id` bigint DEFAULT NULL COMMENT '车间ID',
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编码',
  `line_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '线别名称',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_workshop_code` (`workshop_id`,`line_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1930879174613102596 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='线别信息';

-- ----------------------------
-- Table structure for base_workshop_user
-- ----------------------------
DROP TABLE IF EXISTS `base_workshop_user`;
CREATE TABLE `base_workshop_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_no` varchar(20) DEFAULT NULL COMMENT '员工工号',
  `user_name` varchar(50) DEFAULT NULL COMMENT '员工名称',
  `workshop_id` varchar(300) DEFAULT NULL COMMENT '车间ID',
  `user_type` tinyint(1) DEFAULT '1' COMMENT '人员类型 1:普通  2:管理',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_user_no` (`user_no`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1930539845685858308 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='车间人员权限';

-- ----------------------------
-- Table structure for bms_test_report
-- ----------------------------
DROP TABLE IF EXISTS `bms_test_report`;
CREATE TABLE `bms_test_report` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `test_type` varchar(100) DEFAULT NULL COMMENT '产品车型',
  `sn` varchar(30) DEFAULT NULL COMMENT '产品条码',
  `equipment_no` varchar(255) DEFAULT NULL COMMENT '设备编号',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `consume_time` varchar(15) DEFAULT NULL COMMENT '测试耗时',
  `test_result` varchar(10) DEFAULT NULL COMMENT '测试结果 0-不通过 1-通过',
  `details` json DEFAULT NULL COMMENT '测试项目',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='BMS检测报告';

-- ----------------------------
-- Table structure for feedback_demand_defect
-- ----------------------------
DROP TABLE IF EXISTS `feedback_demand_defect`;
CREATE TABLE `feedback_demand_defect` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `page_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '页面名称',
  `problem_description` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '问题描述(现状说明)',
  `reason_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '原因分析(0:操作问题 1:系统问题)',
  `solve_time` datetime DEFAULT NULL COMMENT '解决时间',
  `solve_way` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '解决方案',
  `picture_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '图片名称',
  `priority` tinyint DEFAULT NULL COMMENT '优先级 1:一般 2:紧急 3:非常紧急',
  `completion_status` tinyint DEFAULT NULL COMMENT '完成状态: 0-未完成 1-已完成 2-测试完成 3-已验证',
  `json_files` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '文件信息',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '记录人',
  `user_id` varchar(10) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '记录人工号',
  `create_name` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '记录人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '1001' COMMENT '租户编码',
  `real_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '处理人姓名',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1923310451700228099 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='需求和问题反馈';

-- ----------------------------
-- Table structure for feedback_demand_defect_picture
-- ----------------------------
DROP TABLE IF EXISTS `feedback_demand_defect_picture`;
CREATE TABLE `feedback_demand_defect_picture` (
  `id` bigint NOT NULL,
  `demand_bug_id` bigint DEFAULT NULL COMMENT '需求和问题id',
  `file_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '文件名称',
  `file_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '文件地址',
  `file_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '文件类型',
  `file_size` double(20,2) DEFAULT NULL COMMENT '文件大小',
  `file_sort` tinyint DEFAULT NULL COMMENT '文件排序',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(255) DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_name` varchar(30) DEFAULT NULL COMMENT '更新名称',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='需求和问题图片';

-- ----------------------------
-- Table structure for feedback_demand_defect_resolve
-- ----------------------------
DROP TABLE IF EXISTS `feedback_demand_defect_resolve`;
CREATE TABLE `feedback_demand_defect_resolve` (
  `id` bigint NOT NULL,
  `demand_bug_id` bigint DEFAULT NULL,
  `user_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '处理人工号',
  `real_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '处理人姓名',
  `dept_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '部门编码',
  `dept_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '部门名称',
  `position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '职位名称',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人名称',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人名称',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '租户编码'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='需求与问题处理人';

-- ----------------------------
-- Table structure for gpf_color_info
-- ----------------------------
DROP TABLE IF EXISTS `gpf_color_info`;
CREATE TABLE `gpf_color_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `color_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '葡萄颜色编码',
  `color_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '葡萄颜色名称',
  `score_min` int DEFAULT NULL COMMENT '分数最小值',
  `score_max` int DEFAULT NULL COMMENT '分数最大值',
  `relation` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '关系',
  `criteria_assessment` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '考核标准描述',
  `rank_sort` int DEFAULT NULL COMMENT '排序号',
  `is_default_color` tinyint DEFAULT '0' COMMENT '是否默认颜色: 0-否 1-是',
  `is_valid` tinyint DEFAULT '1' COMMENT '是否有效: 0-无效 1-有效',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1397473826929876995 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='葡萄颜色信息';

-- ----------------------------
-- Table structure for gpf_criteria_assessment_info
-- ----------------------------
DROP TABLE IF EXISTS `gpf_criteria_assessment_info`;
CREATE TABLE `gpf_criteria_assessment_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `item_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '考核编码',
  `item_name` varchar(255) DEFAULT NULL COMMENT '考核细则',
  `score` int DEFAULT NULL COMMENT '评分',
  `assess_range_type` tinyint DEFAULT NULL COMMENT '考核范围 - 1:业绩 2:行为 3:其他',
  `department_id` bigint DEFAULT NULL COMMENT '部门id',
  `rank_sort` int DEFAULT NULL COMMENT '排序',
  `assess_cycle` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '周期',
  `is_enable` tinyint DEFAULT '1' COMMENT '是否启用 0-不启用 1-启用',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1930501019575767044 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='考核标准';

-- ----------------------------
-- Table structure for gpf_critical_event
-- ----------------------------
DROP TABLE IF EXISTS `gpf_critical_event`;
CREATE TABLE `gpf_critical_event` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `staff_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '员工工号',
  `staff_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '员工姓名',
  `header_icon` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '员工头像',
  `position` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '角色',
  `dept_id` bigint DEFAULT NULL COMMENT '部门id',
  `group_id` bigint DEFAULT NULL COMMENT '班组id',
  `group_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '班组名称',
  `assessment_date` date DEFAULT NULL,
  `assess_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '评估人编号',
  `assess_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '评估人姓名',
  `assess_date` datetime DEFAULT NULL,
  `assess_status` tinyint DEFAULT '1' COMMENT '0-不可考核 1-可考核 2-延迟评估 3-修改 4-已考核 5-已确认 6-不可修改',
  `check_status` tinyint DEFAULT '0' COMMENT '员工确认状态： 0-未确认 1-已确认',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `modify_status` tinyint DEFAULT '0' COMMENT '修改状态：0-未修改 1-已修改',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_staff_no` (`staff_no`,`staff_name`,`position`,`group_id`,`group_name`,`assessment_date`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1391654920731143386 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='关键事件';

-- ----------------------------
-- Table structure for gpf_critical_event_assessment_relation
-- ----------------------------
DROP TABLE IF EXISTS `gpf_critical_event_assessment_relation`;
CREATE TABLE `gpf_critical_event_assessment_relation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `critical_event_id` bigint DEFAULT NULL COMMENT '关键事件id',
  `assessment_id` bigint DEFAULT NULL COMMENT '考核标准id',
  `remark` varchar(1000) DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `inx_uk_critical_event_id_assessment_id` (`critical_event_id`,`assessment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1931201974150328324 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='关键事件与考核标准中间表';

-- ----------------------------
-- Table structure for gpf_dept_assessment_relation
-- ----------------------------
DROP TABLE IF EXISTS `gpf_dept_assessment_relation`;
CREATE TABLE `gpf_dept_assessment_relation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `dept_id` bigint DEFAULT NULL COMMENT '部门id',
  `assess_range_type` tinyint DEFAULT NULL COMMENT '考核范围类型',
  `assess_range` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '考核范围',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `create_name` varchar(30) DEFAULT NULL COMMENT '创建人名称',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `update_name` varchar(30) DEFAULT NULL COMMENT '更新人名称',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='部门与考核范围关系';

-- ----------------------------
-- Table structure for gpf_employee_record
-- ----------------------------
DROP TABLE IF EXISTS `gpf_employee_record`;
CREATE TABLE `gpf_employee_record` (
  `id` bigint DEFAULT NULL,
  `italent_user_id` bigint DEFAULT NULL,
  `user_id` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `head_photo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '用户头像url',
  `cost_center_code` varchar(50) DEFAULT NULL COMMENT '成本中心代码',
  `employee_status` tinyint DEFAULT NULL,
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `creator` bigint DEFAULT NULL,
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL,
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  UNIQUE KEY `gpf_employee_record_italent_user_id_uindex` (`italent_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='员工任职信息';

-- ----------------------------
-- Table structure for jit_bill_priority
-- ----------------------------
DROP TABLE IF EXISTS `jit_bill_priority`;
CREATE TABLE `jit_bill_priority` (
  `id` bigint NOT NULL COMMENT 'ID',
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `stock_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备料单号',
  `priority` int DEFAULT '1000' COMMENT '优先级',
  `required_time` datetime DEFAULT NULL COMMENT '需求时间',
  `process_type` tinyint DEFAULT '3' COMMENT '工序类型 1-组装 2-包装 3-全部',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人ID',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `update_name` varchar(30) DEFAULT NULL,
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_stock_no_process_type` (`stock_no`,`process_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='备料单优先级';

-- ----------------------------
-- Table structure for jit_wo_prepares_materials
-- ----------------------------
DROP TABLE IF EXISTS `jit_wo_prepares_materials`;
CREATE TABLE `jit_wo_prepares_materials` (
  `id` bigint NOT NULL,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `stock_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备料单号',
  `progress_status` tinyint DEFAULT '0' COMMENT '备料状态 0:未备料 1-备料中 2-备料完成	',
  `check_progress` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备料进度',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `update_name` varchar(30) DEFAULT NULL COMMENT '更新人',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` bigint DEFAULT '1001' COMMENT '租户编码',
  `process_type` tinyint DEFAULT '3' COMMENT '工序类型 1-组装 2-包装 3-全部',
  `completion_time` datetime DEFAULT NULL COMMENT '完成时间',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_prepares_stock_no` (`stock_no`,`process_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='备料主表';

-- ----------------------------
-- Table structure for jit_wo_prepares_materials_detail
-- ----------------------------
DROP TABLE IF EXISTS `jit_wo_prepares_materials_detail`;
CREATE TABLE `jit_wo_prepares_materials_detail` (
  `id` bigint NOT NULL,
  `material_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `stock_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备料单号',
  `supplier_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商id',
  `process_type` tinyint DEFAULT '3' COMMENT '工序类型 1-组装 2-包装 3-全部',
  `actual_qty` int DEFAULT NULL COMMENT '实际领料数量',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `update_name` varchar(30) DEFAULT NULL COMMENT '更新人名称',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_detail_stock_no_process` (`stock_no`,`material_code`,`process_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='备料检料详情表';

-- ----------------------------
-- Table structure for mail_buyer_contact_relate
-- ----------------------------
DROP TABLE IF EXISTS `mail_buyer_contact_relate`;
CREATE TABLE `mail_buyer_contact_relate` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `recipients_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '收件人工号',
  `recipients_name` varchar(30) DEFAULT NULL COMMENT '收件人姓名',
  `recipients_email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '收件人邮箱',
  `supplier_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商编码',
  `supplier_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商名称',
  `buyer_code` varchar(30) DEFAULT NULL COMMENT '采购员工号',
  `buyer_name` varchar(30) DEFAULT NULL COMMENT '采购员名称',
  `template_code` varchar(30) DEFAULT NULL COMMENT '邮件类型',
  `template_name` varchar(60) DEFAULT NULL COMMENT '邮件类型名称',
  `factory_code` varchar(30) DEFAULT NULL COMMENT '工厂编码',
  `mobile_phone` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '手机号码',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1852284701850403143 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='收件人关联';

-- ----------------------------
-- Table structure for mail_contact_info
-- ----------------------------
DROP TABLE IF EXISTS `mail_contact_info`;
CREATE TABLE `mail_contact_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `recipients_no` varchar(10) DEFAULT NULL COMMENT '收件人工号',
  `recipients_name` varchar(30) DEFAULT NULL COMMENT '收件人姓名',
  `recipients_email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '收件人邮箱',
  `supplier_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商编码',
  `supplier_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商名称',
  `mobile_phone` varchar(30) DEFAULT NULL COMMENT '手机号码',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=347 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='发件联系人信息';

-- ----------------------------
-- Table structure for mail_recipients_info
-- ----------------------------
DROP TABLE IF EXISTS `mail_recipients_info`;
CREATE TABLE `mail_recipients_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `recipients_no` varchar(10) DEFAULT NULL COMMENT '收件人工号',
  `recipients_name` varchar(30) DEFAULT NULL COMMENT '收件人姓名',
  `recipients_email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '收件人邮箱',
  `organize_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '组织代码',
  `organize_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '组织名称',
  `buyer_code` varchar(30) DEFAULT NULL COMMENT '采购员工号',
  `buyer_name` varchar(30) DEFAULT NULL COMMENT '采购员名称',
  `priority` int DEFAULT '0' COMMENT '优先级',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `mail_unique_index` (`organize_code`,`buyer_code`,`recipients_email`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1928058289113255939 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='发件人信息';

-- ----------------------------
-- Table structure for mail_send_record
-- ----------------------------
DROP TABLE IF EXISTS `mail_send_record`;
CREATE TABLE `mail_send_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bill_no` varchar(50) DEFAULT NULL COMMENT '上游单号',
  `template_name` varchar(20) DEFAULT NULL COMMENT '模板名称',
  `email_title` varchar(50) DEFAULT NULL COMMENT '邮件标题',
  `email_body` text COMMENT '邮件内容-HTML格式',
  `email_type` varchar(20) DEFAULT NULL COMMENT '邮件类型',
  `sender_email` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '发件人邮箱',
  `recipients_email` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '收件人邮箱',
  `trigger_action` varchar(20) DEFAULT NULL COMMENT '触发动作',
  `send_status` int DEFAULT NULL COMMENT '1:失败 2:成功',
  `fail_cause` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '失败原因',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1931397011257651204 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='邮件发送记录';

-- ----------------------------
-- Table structure for mail_sender_info
-- ----------------------------
DROP TABLE IF EXISTS `mail_sender_info`;
CREATE TABLE `mail_sender_info` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sender_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '发件人姓名',
  `sender_no` varchar(10) DEFAULT NULL COMMENT '发件人工号',
  `sender_email` varchar(50) DEFAULT NULL COMMENT '发件人邮箱',
  `sender_password` varchar(50) DEFAULT NULL COMMENT '发件人邮箱密码',
  `verify_status` bit(1) DEFAULT b'0' COMMENT '验证状态 (0-未验证/1-已验证)',
  `organize_code` varchar(50) DEFAULT NULL COMMENT '组织代码',
  `organize_name` varchar(50) DEFAULT NULL COMMENT '组织名称',
  `sender_type` tinyint NOT NULL DEFAULT '0' COMMENT '采购类型(0:资源开发1:采购跟单)',
  `priority` int DEFAULT '0' COMMENT '优先级',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1925017641681068036 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='发件人信息';

-- ----------------------------
-- Table structure for mail_template
-- ----------------------------
DROP TABLE IF EXISTS `mail_template`;
CREATE TABLE `mail_template` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `template_name` varchar(20) DEFAULT NULL COMMENT '模板名称',
  `template_code` varchar(20) DEFAULT NULL COMMENT '模板编码',
  `email_title` varchar(50) DEFAULT NULL COMMENT '邮件标题',
  `email_body` text COMMENT '邮件内容-HTML格式',
  `email_type` varchar(20) DEFAULT NULL COMMENT '邮件类型',
  `sender_email` varchar(50) DEFAULT NULL COMMENT '发件人邮箱',
  `recipients_email` varchar(50) DEFAULT NULL COMMENT '收件人邮箱',
  `trigger_action` varchar(20) DEFAULT NULL COMMENT '触发动作',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_email_type` (`template_code`,`email_type`)
) ENGINE=InnoDB AUTO_INCREMENT=1806946345735241736 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='邮件模板';

-- ----------------------------
-- Table structure for material_weight_push_record
-- ----------------------------
DROP TABLE IF EXISTS `material_weight_push_record`;
CREATE TABLE `material_weight_push_record` (
  `id` bigint NOT NULL,
  `material_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '复位方式CODE',
  `material_name` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '复位名称',
  `sampling_qty` int DEFAULT '0' COMMENT '抽样数量',
  `sampling_sn` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '抽样SN',
  `gross_weight` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '毛重',
  `net_weight` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '净重',
  `push_status` tinyint(1) DEFAULT NULL COMMENT '推送状态 0:推送失败 1:推送成功',
  `errer_msg` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '错误信息',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_material_code` (`material_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='复位方式';

-- ----------------------------
-- Table structure for prod_aux_fixture_info
-- ----------------------------
DROP TABLE IF EXISTS `prod_aux_fixture_info`;
CREATE TABLE `prod_aux_fixture_info` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `fixture_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '治具编码',
  `fixture_name` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '治具名称',
  `quantity` int DEFAULT '0' COMMENT '数量',
  `unit` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单位',
  `available_stock` int DEFAULT '0' COMMENT '可用数量',
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '文件名称',
  `file_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '文件地址',
  `remark` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '修改人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  `factory_code` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `aux_material_code_index` (`fixture_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1917097101598642180 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='治具基础数据表';

-- ----------------------------
-- Table structure for prod_aux_fixture_record
-- ----------------------------
DROP TABLE IF EXISTS `prod_aux_fixture_record`;
CREATE TABLE `prod_aux_fixture_record` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `fixture_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '治具编码',
  `fixture_name` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '治具名称',
  `operate_date` datetime DEFAULT NULL COMMENT '操作日期',
  `operate_type` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '进出类型 (I:入库 O:出库)',
  `quantity` int DEFAULT NULL COMMENT '数量',
  `unit` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单位',
  `receive_id` bigint DEFAULT NULL COMMENT '领用人ID',
  `remark` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '修改人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  `receive_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '领用人姓名',
  `factory_code` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂编码',
  PRIMARY KEY (`id`),
  KEY `aux_material_code_index` (`fixture_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1584895511895814146 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='治具进出记录表';

-- ----------------------------
-- Table structure for prod_aux_material_info
-- ----------------------------
DROP TABLE IF EXISTS `prod_aux_material_info`;
CREATE TABLE `prod_aux_material_info` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `aux_material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '辅料编码',
  `aux_material_name` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '辅料名称',
  `specification` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '规格',
  `init_stock` int DEFAULT '0' COMMENT '初始库存',
  `available_stock` int DEFAULT '0' COMMENT '当前可用库存',
  `unit` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单位',
  `price` decimal(12,2) DEFAULT '0.00' COMMENT '单价',
  `amount` decimal(12,2) DEFAULT '0.00' COMMENT '结存金额',
  `remark` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '修改人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  `warn_stock` int DEFAULT '0' COMMENT '预警库存',
  `old_aux_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `aux_material_code_index` (`aux_material_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1834164852252983300 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='辅料基础数据表';

-- ----------------------------
-- Table structure for prod_aux_material_record
-- ----------------------------
DROP TABLE IF EXISTS `prod_aux_material_record`;
CREATE TABLE `prod_aux_material_record` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `aux_material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '辅料编码',
  `aux_material_name` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '辅料名称',
  `operate_date` datetime DEFAULT NULL COMMENT '操作日期',
  `operate_type` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '进出类型 (I:入库 O:出库)',
  `specification` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '规格',
  `quantity` int DEFAULT NULL COMMENT '进出仓数量',
  `unit` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单位',
  `remark` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '修改人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  `receive_id` bigint DEFAULT NULL COMMENT '领用人',
  `receive_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '领用人姓名',
  `old_aux_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `aux_material_code_index` (`aux_material_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1818127747724513283 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='辅料日进出记录表';

-- ----------------------------
-- Table structure for prod_device_borrowing_record
-- ----------------------------
DROP TABLE IF EXISTS `prod_device_borrowing_record`;
CREATE TABLE `prod_device_borrowing_record` (
  `id` bigint NOT NULL,
  `device_code` varchar(64) NOT NULL COMMENT '设备编号',
  `device_category` tinyint NOT NULL DEFAULT '0' COMMENT '设备分类，与prod_device_info#device_category值一致',
  `borrowing_status` tinyint NOT NULL DEFAULT '0' COMMENT '借用状态；1借用，2归还',
  `operate_time` datetime DEFAULT NULL COMMENT '借用（归还）时间',
  `operator` varchar(32) NOT NULL COMMENT '借用（归还）人工号',
  `operator_name` varchar(32) NOT NULL COMMENT '借用（归还）人名称',
  `borrowing_workshop_name` varchar(64) NOT NULL DEFAULT '' COMMENT '借用车间名称',
  `borrowing_workshop_id` bigint NOT NULL DEFAULT '0' COMMENT '借用车间ID',
  `borrowing_line_code` varchar(64) NOT NULL DEFAULT '' COMMENT '借用线别编码',
  `borrowing_line_name` varchar(64) NOT NULL DEFAULT '' COMMENT '借用线别名称',
  `creator` bigint NOT NULL DEFAULT '0' COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint NOT NULL DEFAULT '0' COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) NOT NULL DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='设备借用记录';

-- ----------------------------
-- Table structure for prod_device_info
-- ----------------------------
DROP TABLE IF EXISTS `prod_device_info`;
CREATE TABLE `prod_device_info` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `factory_code` varchar(4) DEFAULT '2000' COMMENT '工厂编码',
  `device_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '设备编码',
  `device_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '设备名称',
  `device_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '设备类型',
  `important_grade` varchar(10) DEFAULT NULL COMMENT '分级(重要程度)',
  `producer` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '设备厂家',
  `time_buying` datetime DEFAULT NULL COMMENT '入厂时间',
  `department` varchar(30) DEFAULT NULL COMMENT '归属部门',
  `location` varchar(50) DEFAULT NULL COMMENT '位置',
  `online_status` tinyint DEFAULT '0' COMMENT '在线状态 0-闲置 1-占用',
  `remark` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '修改人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  `device_category` tinyint NOT NULL DEFAULT '0' COMMENT '设备分类；1测试设备，2气缸设备，3防水测试设备，4螺丝机设备，5自动点胶设备',
  `device_specification` varchar(200) NOT NULL DEFAULT '' COMMENT '设备规格',
  `device_photo` json DEFAULT NULL COMMENT '设备照片',
  `producer_phone` varchar(32) NOT NULL DEFAULT '' COMMENT '生产商电话',
  `device_sale_price` decimal(13,3) NOT NULL DEFAULT '0.000' COMMENT '设备销售单价',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_device_code` (`device_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1927638428769173508 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='设备列表';

-- ----------------------------
-- Table structure for prod_device_info_use_record
-- ----------------------------
DROP TABLE IF EXISTS `prod_device_info_use_record`;
CREATE TABLE `prod_device_info_use_record` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `device_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '设备编码',
  `device_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '设备名称',
  `device_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '设备类型',
  `boot_hours` decimal(6,2) DEFAULT NULL COMMENT '开机时长',
  `attendance_hours` decimal(6,2) DEFAULT '0.00' COMMENT '上班时长',
  `use_rate` decimal(5,2) DEFAULT NULL COMMENT '利用率(%)',
  `use_date` date DEFAULT NULL COMMENT '使用日期',
  `remark` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '修改人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `idx_device_code` (`device_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1826993021116608515 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='设备使用记录';

-- ----------------------------
-- Table structure for prod_device_usage_rate_report
-- ----------------------------
DROP TABLE IF EXISTS `prod_device_usage_rate_report`;
CREATE TABLE `prod_device_usage_rate_report` (
  `id` bigint NOT NULL,
  `device_category` tinyint NOT NULL DEFAULT '0' COMMENT '设备分类，与prod_device_info#device_category值一致',
  `use_qty` int NOT NULL DEFAULT '0' COMMENT '统计日期在用设备数量',
  `store_qty` int NOT NULL DEFAULT '0' COMMENT '统计日期库存设备数量',
  `usage_rate` decimal(13,3) NOT NULL DEFAULT '0.000' COMMENT '使用率（单位%）',
  `statistics_time` date NOT NULL COMMENT '统计日期',
  `statistics_attr` tinyint NOT NULL DEFAULT '0' COMMENT '统计属性；1日，2月，3年',
  `creator` bigint NOT NULL DEFAULT '0' COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint NOT NULL DEFAULT '0' COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) NOT NULL DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='设备日月年使用率报表';

-- ----------------------------
-- Table structure for production_first_article_inspection
-- ----------------------------
DROP TABLE IF EXISTS `production_first_article_inspection`;
CREATE TABLE `production_first_article_inspection` (
  `id` bigint NOT NULL,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '型号',
  `material_count` tinyint DEFAULT NULL COMMENT '送检产品数量',
  `radium_content_str` varchar(3000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '镭雕内容',
  `sn_json_str` varchar(3000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '送检产品序列号json字符串',
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `check_item_str` varchar(3000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '检查项目json字符串',
  `article_type` tinyint DEFAULT NULL COMMENT '检查类型：1- 组装首件 2-镭雕首件 3-包装首件',
  `confirm_status` tinyint DEFAULT NULL COMMENT '确认状态:1-OK 2-NG',
  `bar_code_scope` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单范围',
  `qty` int DEFAULT NULL COMMENT '工单数量',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='首件送检表';

-- ----------------------------
-- Table structure for production_first_article_inspection_detail
-- ----------------------------
DROP TABLE IF EXISTS `production_first_article_inspection_detail`;
CREATE TABLE `production_first_article_inspection_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `first_article_id` bigint DEFAULT NULL COMMENT '首件送检id',
  `article_type` tinyint DEFAULT NULL COMMENT '首件类型 1-组装首件 2-镭雕首件 3-包装首件',
  `sn` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'sn',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_article_type_sn` (`article_type`,`sn`)
) ENGINE=InnoDB AUTO_INCREMENT=25066 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='首件送检SN明细';

-- ----------------------------
-- Table structure for production_host_into_stock
-- ----------------------------
DROP TABLE IF EXISTS `production_host_into_stock`;
CREATE TABLE `production_host_into_stock` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bill_no` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `material_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `qty` int DEFAULT NULL COMMENT '入库数量',
  `meins` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基本计量单位',
  `werks` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂编码',
  `lgort` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '仓位',
  `material_voucher` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料凭证号',
  `posting_date` date DEFAULT NULL COMMENT '过账日期',
  `document_date` date DEFAULT NULL COMMENT '凭证日期',
  `submit_status` bit(1) DEFAULT b'0' COMMENT '提交状态 0:未提交  1:已提交',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  `stock_type` tinyint DEFAULT NULL COMMENT '入库类型 1:主机入库  2:成品入库',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1930916764103962628 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产主机入库';

-- ----------------------------
-- Table structure for production_into_stock_detail_record
-- ----------------------------
DROP TABLE IF EXISTS `production_into_stock_detail_record`;
CREATE TABLE `production_into_stock_detail_record` (
  `id` bigint NOT NULL,
  `into_stock_id` bigint DEFAULT NULL COMMENT '生产入库id',
  `sn` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编码',
  `workshop_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '车间名称',
  `white_package_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '白盒号',
  `big_package_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '大箱号',
  `be_accessories` tinyint DEFAULT NULL COMMENT '是否配件 0-否 1-是',
  `qty` int DEFAULT NULL COMMENT '数量',
  `bill_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-已删除',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '租户编码',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改日期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_white_package_no_sn` (`white_package_no`,`sn`),
  KEY `idx_bill_no` (`bill_no`) USING BTREE,
  KEY `idx_sn_delflag` (`sn`,`del_flag`),
  KEY `idx_into_stock_id` (`into_stock_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产入库明细';

-- ----------------------------
-- Table structure for production_into_stock_record
-- ----------------------------
DROP TABLE IF EXISTS `production_into_stock_record`;
CREATE TABLE `production_into_stock_record` (
  `id` bigint NOT NULL,
  `into_stock_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '入库单号',
  `bar_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '条码',
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编码',
  `workshop_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '车间名称',
  `big_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '大箱号',
  `white_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '白盒号',
  `material_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '料箱号',
  `material_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `material_source` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'SC' COMMENT '物料来源 SC:生产 CG:采购',
  `qty` int DEFAULT NULL COMMENT '入库数量',
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产工单号',
  `push_status` tinyint DEFAULT '0' COMMENT '推送状态 0-未推送 1-已推送',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改日期',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-已删除',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产入库单记录';

-- ----------------------------
-- Table structure for production_laser_carving_efficiency
-- ----------------------------
DROP TABLE IF EXISTS `production_laser_carving_efficiency`;
CREATE TABLE `production_laser_carving_efficiency` (
  `id` bigint NOT NULL,
  `device_code` varchar(32) DEFAULT NULL COMMENT '设备编号',
  `device_name` varchar(32) DEFAULT NULL COMMENT '设备名称',
  `work_time` datetime DEFAULT NULL COMMENT '生产日期',
  `total_qty` int DEFAULT '0' COMMENT '生产总数',
  `total_consume_time` decimal(10,2) DEFAULT '0.00' COMMENT '生产总工时，单位s',
  `plan_consume_time` int DEFAULT '0' COMMENT '计划工时，默认10h',
  `efficiency` decimal(6,2) DEFAULT '0.00' COMMENT '当天效率 = 生产总工时 / (计划时间 * 3600) * 100，计划时间默认为10h',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='雷雕生产效率统计';

-- ----------------------------
-- Table structure for production_laser_carving_task
-- ----------------------------
DROP TABLE IF EXISTS `production_laser_carving_task`;
CREATE TABLE `production_laser_carving_task` (
  `id` bigint NOT NULL,
  `production_task_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '生产任务号',
  `production_shift_id` bigint DEFAULT '0' COMMENT '生产班次ID',
  `production_shift_hour` decimal(4,2) DEFAULT NULL COMMENT '有效工时',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间ID',
  `process_type_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '工序类型编码',
  `process_type_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '工序类型名称',
  `bill_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '工单号',
  `bill_qty` int DEFAULT NULL COMMENT '工单数量',
  `production_date` date DEFAULT NULL COMMENT '生产日期',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料名称',
  `task_qty` int DEFAULT '0' COMMENT '任务总数量',
  `completed_qty` int DEFAULT '0' COMMENT '完成总数量',
  `task_status` tinyint(1) DEFAULT '1' COMMENT '任务状态 1:未开始 2:生产中 3:已完成 4:异常 5:已关闭 6:未完成 7:待清尾',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人名称',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人名称',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '1001' COMMENT '租户编码',
  `workshop_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '车间名称',
  `production_shift_name` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '生产班次名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='生产镭雕日计划';

-- ----------------------------
-- Table structure for production_laser_carving_task_details
-- ----------------------------
DROP TABLE IF EXISTS `production_laser_carving_task_details`;
CREATE TABLE `production_laser_carving_task_details` (
  `id` bigint NOT NULL,
  `production_task_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '0' COMMENT '生产任务号',
  `bill_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '工单号',
  `bill_qty` int DEFAULT NULL COMMENT '工单数量',
  `production_date` date DEFAULT NULL COMMENT '生产日期',
  `child_material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '部件编码',
  `child_material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '部件名称',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料名称',
  `task_qty` int DEFAULT '0' COMMENT '任务数量',
  `uph` int DEFAULT NULL COMMENT 'UPH',
  `completed_qty` int DEFAULT '0' COMMENT '完成数量',
  `priority` int DEFAULT '999' COMMENT '优先级',
  `task_status` tinyint(1) DEFAULT '1' COMMENT '任务状态 1:未开始 2:生产中 3:已完成 4:异常 5:已关闭 6:未完成 7:待清尾',
  `production_hours` decimal(8,2) DEFAULT '0.00' COMMENT '生产工时',
  `norm_man_hour` decimal(8,2) DEFAULT '0.00' COMMENT '标准工时',
  `employee_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '镭雕员工号',
  `employee_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '镭雕员名称',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人名称',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人名称',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '1001' COMMENT '租户编码',
  `device_code` varchar(32) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '机器编号',
  `device_name` varchar(32) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '机器名称',
  `real_completed_time` datetime DEFAULT NULL COMMENT '实际完成时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='生产镭雕分配';

-- ----------------------------
-- Table structure for production_master_carton_image
-- ----------------------------
DROP TABLE IF EXISTS `production_master_carton_image`;
CREATE TABLE `production_master_carton_image` (
  `id` bigint DEFAULT NULL COMMENT 'id',
  `carton_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '大箱号',
  `image` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '图片文件 base64',
  `machine_no` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '拍照设备号',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  UNIQUE KEY `uk_carton_no` (`carton_no`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='大箱图片';

-- ----------------------------
-- Table structure for production_material_allocation_batch
-- ----------------------------
DROP TABLE IF EXISTS `production_material_allocation_batch`;
CREATE TABLE `production_material_allocation_batch` (
  `id` bigint NOT NULL,
  `procedure_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序',
  `station_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工位编码',
  `station` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工位',
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单',
  `allocation_status` tinyint DEFAULT '0' COMMENT '物料配送状态 0-配送中，1-配送完成',
  `line_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编码',
  `creator` bigint DEFAULT NULL COMMENT '叫料员',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '叫料员名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_line_code_procedure_type` (`line_code`,`procedure_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='工位叫料送料批次表';

-- ----------------------------
-- Table structure for production_material_allocation_record
-- ----------------------------
DROP TABLE IF EXISTS `production_material_allocation_record`;
CREATE TABLE `production_material_allocation_record` (
  `id` bigint NOT NULL,
  `material_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `qty` int DEFAULT NULL COMMENT '物料数量',
  `allocation_status` tinyint DEFAULT '0' COMMENT '物料配送状态 0-配送中，1-配送完成',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '叫料员',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '叫料员名称',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `batch_no` bigint DEFAULT NULL COMMENT '批次id',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_allocation_batch_no` (`batch_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='工位叫料送料记录表';

-- ----------------------------
-- Table structure for production_order
-- ----------------------------
DROP TABLE IF EXISTS `production_order`;
CREATE TABLE `production_order` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '表id',
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `product_type` tinyint DEFAULT NULL COMMENT '产品类型 1主产品 2联产品 3副产品',
  `bill_type_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单据类型 WW:试产 WR:返工  WP:包装 WO:主机 WJ:前加工',
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `net_weight` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '重量',
  `weight_unitid` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '重量单位',
  `specification_model` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '规则',
  `qty` int DEFAULT NULL COMMENT '工单数量',
  `bomid` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'BOMID',
  `convey_date` datetime DEFAULT NULL COMMENT '下达日期',
  `start_date` datetime DEFAULT NULL COMMENT '开工日期',
  `plan_start_date` datetime DEFAULT NULL COMMENT '计划开工日期',
  `workshop_name` varchar(50) DEFAULT NULL COMMENT '车间名称',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间ID',
  `complete_date` datetime DEFAULT NULL COMMENT '完工时间',
  `status` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '订单状态 create:创建,issued:下达，start:开工，complete:完工，close:结案',
  `bill_type` tinyint DEFAULT NULL COMMENT '工单类型 0:生产工单  1:委外订单',
  `order_type` tinyint DEFAULT '0' COMMENT '订单类型 0:正常订单 1:返工单',
  `supplier_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商ID   仅委外订单',
  `host_stocked_qty` int DEFAULT '0' COMMENT '主机入库数量',
  `line_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '待分配线别' COMMENT '线别编码',
  `data_sources` tinyint DEFAULT '0' COMMENT '数据来源 0-外部获取 1-创建',
  `no_stocked_qty` int DEFAULT NULL COMMENT '未入库数量',
  `stocked_qty` int DEFAULT '0' COMMENT '入库数量',
  `picking_plaid` decimal(10,3) DEFAULT NULL COMMENT '领料套数',
  `picking_status` tinyint DEFAULT NULL COMMENT '领料状态 1:未领料 2:部分领料 3:全部领料 4:超额领料',
  `sort` int DEFAULT '999' COMMENT '排序',
  `packaging_progress` int DEFAULT '0' COMMENT '包装进度',
  `assemble_progress` int DEFAULT '0' COMMENT '组装进度',
  `fqc_progress` int DEFAULT '0' COMMENT 'FQC进度',
  `bar_code_scope` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '条码范围',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '描述',
  `start_working_status` tinyint DEFAULT '0' COMMENT '开工状态 0:未开工 1:已开工',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `old_bomid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `prototype_qty` int DEFAULT '0' COMMENT '样机数量',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_order_bill_no` (`bill_no`),
  KEY `idx_zs_assistant` (`line_code`) USING BTREE,
  KEY `idx_production_order_material_code` (`material_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1930924215675091672 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='生产订单';

-- ----------------------------
-- Table structure for production_order_bar_code
-- ----------------------------
DROP TABLE IF EXISTS `production_order_bar_code`;
CREATE TABLE `production_order_bar_code` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `production_order_qty` int DEFAULT NULL COMMENT '工单数量',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `delivery_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '发货单号',
  `delivery_time` datetime DEFAULT NULL COMMENT '发货时间',
  `delivery_user` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '发货用户',
  `carton_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '大箱号',
  `state_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '国家代码',
  `salesman` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '业务员',
  `customer_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '客户名称',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '生成人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生成人名称',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `laser_flag` bit(1) DEFAULT b'0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_sn` (`sn`) USING BTREE,
  KEY `idx_material_code` (`material_code`) USING BTREE,
  KEY `idx_material_name` (`material_name`) USING BTREE,
  KEY `idx_tenant_code` (`tenant_code`,`del_flag`),
  KEY `idx_create_date` (`create_time`) USING BTREE,
  KEY `idx_delivery_time` (`delivery_time`) USING BTREE,
  KEY `idx_bill_no` (`bill_no`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6756028468770612476 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='工单条码';

-- ----------------------------
-- Table structure for production_order_bar_code_batch
-- ----------------------------
DROP TABLE IF EXISTS `production_order_bar_code_batch`;
CREATE TABLE `production_order_bar_code_batch` (
  `id` bigint NOT NULL,
  `rule_id` bigint DEFAULT NULL COMMENT '规则ID',
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `last_sequence` int DEFAULT NULL COMMENT '最近一次生成序列号',
  `qty` int DEFAULT NULL COMMENT '数量',
  `current_sequence` int DEFAULT NULL COMMENT '当前生成的序列号',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` bigint DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_rule_id` (`rule_id`,`bill_no`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='批量生成序列号记录-用于释放序列号';

-- ----------------------------
-- Table structure for production_order_bar_code_history
-- ----------------------------
DROP TABLE IF EXISTS `production_order_bar_code_history`;
CREATE TABLE `production_order_bar_code_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `production_order_qty` int DEFAULT NULL COMMENT '工单数量',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `delivery_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '发货单号',
  `delivery_time` datetime DEFAULT NULL COMMENT '发货时间',
  `delivery_user` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '发货用户',
  `carton_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '大箱号',
  `state_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '国家代码',
  `salesman` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '业务员',
  `customer_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '客户名称',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '生成人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生成人名称',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `laser_flag` bit(1) DEFAULT b'0',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_sn` (`sn`) USING BTREE,
  KEY `idx_material_code` (`material_code`) USING BTREE,
  KEY `idx_material_name` (`material_name`) USING BTREE,
  KEY `idx_tenant_code` (`tenant_code`,`del_flag`),
  KEY `idx_create_date` (`create_time`) USING BTREE,
  KEY `idx_delivery_time` (`delivery_time`) USING BTREE,
  KEY `idx_bill_no` (`bill_no`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1756028468770446822 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='工单条码-归档数据（20250101）';

-- ----------------------------
-- Table structure for production_order_customized_code
-- ----------------------------
DROP TABLE IF EXISTS `production_order_customized_code`;
CREATE TABLE `production_order_customized_code` (
  `id` bigint NOT NULL,
  `customer_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '客户名称',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `material_specification` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料规格',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='芬兰客户有自定义序列号表';

-- ----------------------------
-- Table structure for production_order_detail_material
-- ----------------------------
DROP TABLE IF EXISTS `production_order_detail_material`;
CREATE TABLE `production_order_detail_material` (
  `id` bigint NOT NULL,
  `production_order_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Sap 生产订单号',
  `rspos` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '行项目',
  `vornr` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单工序号',
  `postp` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '项目类别 库存物资 L 其他 N',
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '子项物料编码',
  `matxt` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '子项物料描述',
  `mtart` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料类型 Z000 成品 Z001 裸机 Z002 半成品 Z003 原材料 Z005 宣传物料 Z006 电子料 Z008 辅料',
  `bdmng` decimal(10,3) DEFAULT NULL COMMENT '需求数量',
  `enmng` decimal(10,3) DEFAULT NULL COMMENT '已领数量',
  `nomng` decimal(10,3) DEFAULT NULL COMMENT '接口发料数量',
  `meins` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '计量单位 PCS',
  `lgort` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '存储位置',
  `sobkz` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '特殊库存标识',
  `lifnr` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商编码',
  `rgekz` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否反冲',
  `xloek` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否删除',
  `dumps` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否虚拟项目',
  `kzear` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否已发货',
  `alpgr` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备选项目组',
  `alprf` int DEFAULT NULL COMMENT '优先级',
  `alpst` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '策略',
  `ewahr` decimal(10,3) DEFAULT NULL COMMENT '使用概率',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `tenant_code` varchar(0) DEFAULT NULL COMMENT '租户编码',
  `ltxa1` varchar(20) DEFAULT NULL COMMENT '工序名称',
  `reserve1` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '散装',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_production_order_no_rspos` (`production_order_no`,`rspos`),
  KEY `index_material_code` (`matnr`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Sap 生产订单物料组件明细';

-- ----------------------------
-- Table structure for production_order_detail_process
-- ----------------------------
DROP TABLE IF EXISTS `production_order_detail_process`;
CREATE TABLE `production_order_detail_process` (
  `id` bigint NOT NULL,
  `production_order_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Sap 生产订单号',
  `vornr` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序编号',
  `arbpl` varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工作中心',
  `ltxa1` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序短文本',
  `bmsch` decimal(10,3) DEFAULT NULL COMMENT '基本数量',
  `meinh` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基本数量单位 PCS',
  `vgw01` decimal(10,3) DEFAULT NULL COMMENT '人工工时',
  `vge01` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '人工工时单位 H',
  `vgw02` decimal(10,3) DEFAULT NULL COMMENT '变动工时',
  `vge02` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '变动工时单位 H',
  `vgw03` decimal(10,3) DEFAULT NULL COMMENT '固定工时',
  `vge03` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '固定工时单位 H',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_date` datetime DEFAULT NULL COMMENT '创建时间',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_production_order_no_vornr` (`production_order_no`,`vornr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产订单工序明细';

-- ----------------------------
-- Table structure for production_order_host_storage_record
-- ----------------------------
DROP TABLE IF EXISTS `production_order_host_storage_record`;
CREATE TABLE `production_order_host_storage_record` (
  `id` bigint NOT NULL,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `qty` int DEFAULT NULL COMMENT '主机入库数量',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_bill_no` (`bill_no`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='生产订单主机入库数量';

-- ----------------------------
-- Table structure for production_order_period_analysis
-- ----------------------------
DROP TABLE IF EXISTS `production_order_period_analysis`;
CREATE TABLE `production_order_period_analysis` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `production_order_id` bigint DEFAULT NULL COMMENT '生产订单ID',
  `period_analysis` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '周期分析',
  `analysis_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '类型',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uq_production_order_id` (`production_order_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2846 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='生产周期分析';

-- ----------------------------
-- Table structure for production_order_sap
-- ----------------------------
DROP TABLE IF EXISTS `production_order_sap`;
CREATE TABLE `production_order_sap` (
  `id` bigint DEFAULT NULL,
  `aufnr` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `rsnum` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '预留号',
  `long_txt` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '订单备注',
  `posnr` int DEFAULT NULL COMMENT '行号',
  `erdat` date DEFAULT NULL COMMENT '创建日期',
  `erfzeit` time DEFAULT NULL COMMENT '创建时间',
  `aedat` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改日期',
  `aezeit` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改时间',
  `auart` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '订单类型 ZP01 标准订单 ZP02 试制订单 ZP03 返工订单 ZP04 改制订单',
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `matxt` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `istat` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '订单状态: I0001=CRTD 建立 I0002=REL 释放 I0043=锁定 已锁定 I0045=TECO 技术实现 I0046=CLSD 已结算 I0013=DLID--删除标记',
  `werks` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂',
  `gamng` double(22,0) DEFAULT NULL COMMENT '订单总数量',
  `wemng` double(22,0) DEFAULT NULL COMMENT '已经完成的收货数量',
  `gstrp` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '预计开工时间',
  `gltrp` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '预计完工时间',
  `gltri` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '实际完工时间',
  `elikz` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否收货完成',
  `lgort` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '收货地点',
  `creator` bigint DEFAULT NULL,
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int DEFAULT '1' COMMENT '版本号',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码',
  UNIQUE KEY `uk_aufnr` (`aufnr`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='SAP生产订单';

-- ----------------------------
-- Table structure for production_prototype_receive_record
-- ----------------------------
DROP TABLE IF EXISTS `production_prototype_receive_record`;
CREATE TABLE `production_prototype_receive_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bill_no` varchar(20) DEFAULT NULL COMMENT '生产订单号',
  `material_code` varchar(20) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `receive_qty` int DEFAULT NULL COMMENT '领用数量',
  `warehouse_voucher` varchar(20) DEFAULT NULL COMMENT '入库凭证',
  `receive_voucher` varchar(255) DEFAULT NULL COMMENT '领用凭证',
  `recruiter` varchar(30) DEFAULT NULL COMMENT '领用人',
  `receive_time` datetime DEFAULT NULL COMMENT '领用时间',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产样机领用记录';

-- ----------------------------
-- Table structure for production_receive_order
-- ----------------------------
DROP TABLE IF EXISTS `production_receive_order`;
CREATE TABLE `production_receive_order` (
  `id` bigint NOT NULL,
  `mblnr` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料凭证号',
  `mjahr` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '凭证年份',
  `bldat` date DEFAULT NULL COMMENT '凭证日期',
  `budat` date DEFAULT NULL COMMENT '过账日期',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_mblnr` (`mblnr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='SAP生产领料单';

-- ----------------------------
-- Table structure for production_receive_order_detail
-- ----------------------------
DROP TABLE IF EXISTS `production_receive_order_detail`;
CREATE TABLE `production_receive_order_detail` (
  `id` bigint NOT NULL,
  `mblnr` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料凭证号',
  `zeile` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '项目',
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `matxt` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `erfmg` decimal(10,3) DEFAULT NULL COMMENT '过账数量',
  `erfme` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单位',
  `werks` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂',
  `lgort` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '库位',
  `sobkz` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '特殊库位 K=寄售仓',
  `aufnr` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产订单',
  `mat_lifnr` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商编码',
  `mat_vendorname` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商名称',
  `bwart` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '移动类型',
  `charg` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '批次号',
  `return_flag` tinyint DEFAULT '0' COMMENT '退料标识 0-未退 1-已退',
  `return_qty` decimal(10,3) DEFAULT '0.000' COMMENT '退货数量',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_mblnr_zeile` (`mblnr`,`zeile`),
  KEY `idx_bill_no` (`aufnr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='SAP生产领料单明细';

-- ----------------------------
-- Table structure for production_rejected_material
-- ----------------------------
DROP TABLE IF EXISTS `production_rejected_material`;
CREATE TABLE `production_rejected_material` (
  `id` bigint NOT NULL,
  `return_bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '退料单据编码',
  `aufnr` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产订单号',
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `matxt` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `line_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `refdoc` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料凭证号',
  `erfmg` int DEFAULT '0' COMMENT '工单物料数量',
  `submit_status` int DEFAULT '0' COMMENT '提交状态 1:未提交 0:过账失败  2:已提交 3:过账成功',
  `request_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '流程ID',
  `request_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '流程编号',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `is_replenish` tinyint NOT NULL DEFAULT '1' COMMENT '是否生成补料单 0不生成  1生成',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产退料主表';

-- ----------------------------
-- Table structure for production_rejected_material_details
-- ----------------------------
DROP TABLE IF EXISTS `production_rejected_material_details`;
CREATE TABLE `production_rejected_material_details` (
  `id` bigint NOT NULL,
  `asp_material_id` bigint DEFAULT NULL COMMENT '退料表ID',
  `receive_order_detail_id` bigint DEFAULT NULL COMMENT '生产领料明细记录ID',
  `cost_price` decimal(20,8) DEFAULT '0.00000000' COMMENT '成本价',
  `aufnr` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产订单号',
  `rsnum` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '预留单号',
  `rspos` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '预留单行号',
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `matxt` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `related_material` varchar(20) DEFAULT NULL COMMENT '连带物料',
  `bldat` datetime DEFAULT NULL COMMENT '凭证日期',
  `budat` datetime DEFAULT NULL COMMENT '过账日期',
  `refdoc` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料凭证号',
  `erfmg` decimal(13,3) DEFAULT '0.000' COMMENT '退料数量',
  `erfme` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '补料单位',
  `return_type` int DEFAULT NULL COMMENT '退料类型 0:测试不良 1:作业不良 2:来料不良 3:良品退料 4:设计不良 5:作业不良（连带）6:来料不良（连带）',
  `bad_appearance` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良现象',
  `bad_description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良描述',
  `sobkz` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '特殊库存 VMI：K',
  `vendorname` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商编码',
  `werks` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂',
  `lgort` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '库位',
  `stock_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '仓库名称',
  `supplier_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商名称',
  `charg` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '批次号',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产退料详情表';

-- ----------------------------
-- Table structure for production_repair_record
-- ----------------------------
DROP TABLE IF EXISTS `production_repair_record`;
CREATE TABLE `production_repair_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `work_process_type` varchar(20) DEFAULT NULL COMMENT '工序类型',
  `workshop_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '车间名称',
  `line_name` varchar(20) DEFAULT NULL COMMENT '线别',
  `material_code` varchar(30) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) DEFAULT NULL COMMENT '物料名称',
  `rejects_name` varchar(20) DEFAULT NULL COMMENT '不良代码名称',
  `rejects_type_name` varchar(20) DEFAULT NULL COMMENT '不良代码类型',
  `rejects_describe` varchar(100) DEFAULT NULL COMMENT '不良原因',
  `repair_user` varchar(20) DEFAULT NULL COMMENT '维修员',
  `repair_time` datetime DEFAULT NULL COMMENT '修修时间',
  `repair_scheme` varchar(100) DEFAULT NULL COMMENT '维修方案',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  `repair_qty` int DEFAULT '1' COMMENT '维修数量',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1711911564032208899 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产维修记录';

-- ----------------------------
-- Table structure for production_replenish_material
-- ----------------------------
DROP TABLE IF EXISTS `production_replenish_material`;
CREATE TABLE `production_replenish_material` (
  `id` bigint NOT NULL,
  `return_bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '补料单号',
  `refdoc` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料凭证号',
  `aufnr` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产订单号',
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `matxt` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `line_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `erfmg` int DEFAULT '0' COMMENT '工单物料数量',
  `submit_status` int DEFAULT '0' COMMENT '过账状态  0,"未过账" 1,"过账成功" 2,"过账失败" 3,"部分过账"',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产补料表';

-- ----------------------------
-- Table structure for production_replenish_material_details
-- ----------------------------
DROP TABLE IF EXISTS `production_replenish_material_details`;
CREATE TABLE `production_replenish_material_details` (
  `id` bigint NOT NULL,
  `asp_material_id` bigint DEFAULT NULL COMMENT '补料表ID',
  `rsnum` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '预留单号',
  `rspos` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '预留单行号',
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `matxt` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `bldat` datetime DEFAULT NULL COMMENT '凭证日期',
  `budat` datetime DEFAULT NULL COMMENT '过账日期',
  `refdoc` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料凭证号',
  `erfmg` decimal(13,3) DEFAULT '0.000' COMMENT '退料数量',
  `erfme` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '补料单位',
  `return_type` int DEFAULT NULL COMMENT '补料类型 1:作业不良 2:来料不良 3:良品退料 4:设计不良',
  `bad_appearance` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良现象',
  `bad_description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良描述',
  `sobkz` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '特殊库存 VMI：K',
  `vendorname` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商编码',
  `werks` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂',
  `lgort` varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '库位',
  `stock_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '仓库名称',
  `supplier_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商名称',
  `charg` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '批次号',
  `submit_status` tinyint DEFAULT '0' COMMENT '过账状态 0:未过账 1:过账成功 2:过账失败',
  `push_error_msg` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '推送错误信息',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `print_status` tinyint(1) DEFAULT '0' COMMENT '打印状态 0:未打印 1:已打印',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产补料详情表';

-- ----------------------------
-- Table structure for production_sop
-- ----------------------------
DROP TABLE IF EXISTS `production_sop`;
CREATE TABLE `production_sop` (
  `id` bigint NOT NULL COMMENT 'id',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(255) DEFAULT NULL COMMENT '物料名称',
  `material_specification` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料规格',
  `work_process_type_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '制程工序类型code',
  `work_process_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '制程工序类型',
  `manpower` int DEFAULT NULL COMMENT '工位人数',
  `capacity` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '标准产能',
  `takt_time` varchar(6) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '节拍时间',
  `status` int DEFAULT NULL COMMENT '审核状态 0待审核  1已审核  2审核不通过 3删除待提交 4修改待提交 5保存待提交',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `material_code` (`material_code`,`work_process_type_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='sop基本信息表';

-- ----------------------------
-- Table structure for production_sop_record
-- ----------------------------
DROP TABLE IF EXISTS `production_sop_record`;
CREATE TABLE `production_sop_record` (
  `id` bigint NOT NULL COMMENT 'id',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(255) DEFAULT NULL COMMENT '物料名称',
  `material_specification` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料规格',
  `work_process_type_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '制程工序类型编码',
  `work_process_type` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '制程工序类型',
  `takt_time` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '节拍时间',
  `manpower` int DEFAULT NULL COMMENT '工位人数',
  `capacity` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '标准产能',
  `status` int DEFAULT NULL COMMENT '审核状态 0待审核  1已审核  2审核失败',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `station` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '工位信息json',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='sop列表历史记录表';

-- ----------------------------
-- Table structure for production_sop_station
-- ----------------------------
DROP TABLE IF EXISTS `production_sop_station`;
CREATE TABLE `production_sop_station` (
  `id` bigint NOT NULL COMMENT 'id',
  `sop_id` bigint DEFAULT NULL COMMENT '基本信息表ID',
  `station_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工位code',
  `station_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工位名称',
  `distribution_point` int DEFAULT NULL COMMENT '配送点',
  `static_logo` tinyint DEFAULT '0' COMMENT '静电工位标识 0否  1是',
  `crux_logo` tinyint DEFAULT '0' COMMENT '关键工位标识 0否  1是',
  `takt_time` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '节拍时间',
  `video_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '视频名称',
  `video_url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '视频地址',
  `station_picture_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工位图片名称',
  `station_picture_url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工位图片地址',
  `announcements` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '注意事项',
  `step_description` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '步骤描述',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `check_logo` tinyint DEFAULT '0' COMMENT '检验工位 0否  1是',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='sop工位信息表';

-- ----------------------------
-- Table structure for production_sop_station_ingredients
-- ----------------------------
DROP TABLE IF EXISTS `production_sop_station_ingredients`;
CREATE TABLE `production_sop_station_ingredients` (
  `id` bigint NOT NULL COMMENT 'id',
  `station_id` bigint NOT NULL COMMENT '工位信息表ID',
  `ingredients_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '编码',
  `ingredients_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '名称',
  `ingredients_number` decimal(6,2) DEFAULT NULL COMMENT '数量',
  `type` int DEFAULT NULL COMMENT '1辅料 2治具  3设备',
  `params` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '参数',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='sop工位辅料表';

-- ----------------------------
-- Table structure for production_sop_station_material
-- ----------------------------
DROP TABLE IF EXISTS `production_sop_station_material`;
CREATE TABLE `production_sop_station_material` (
  `id` bigint NOT NULL COMMENT 'id',
  `station_id` bigint NOT NULL COMMENT '工位信息表ID',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `number` int DEFAULT NULL COMMENT '物料数量',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='sop工位物料表';

-- ----------------------------
-- Table structure for production_sop_station_step
-- ----------------------------
DROP TABLE IF EXISTS `production_sop_station_step`;
CREATE TABLE `production_sop_station_step` (
  `id` bigint NOT NULL COMMENT 'id',
  `station_id` bigint NOT NULL COMMENT '工位信息表ID',
  `step_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '步骤名称',
  `step_picture_url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '步骤图片地址',
  `picture_sort` int DEFAULT NULL COMMENT '步骤图片排序',
  `step_description` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '步骤描述',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='sop工位步骤表';

-- ----------------------------
-- Table structure for production_standard_man_hour
-- ----------------------------
DROP TABLE IF EXISTS `production_standard_man_hour`;
CREATE TABLE `production_standard_man_hour` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `laser_carving_uph` double(10,2) DEFAULT NULL COMMENT '镭雕uph',
  `laser_carving_upph` double(10,2) DEFAULT NULL COMMENT '镭雕upph',
  `laser_carving_hour` double(10,2) DEFAULT NULL COMMENT '镭雕工时',
  `pre_elaboration_uph` double(10,2) DEFAULT NULL COMMENT '前加工uph',
  `pre_elaboration_upph` double(10,2) DEFAULT NULL COMMENT '前加工upph',
  `pre_elaboration_hour` double(10,2) DEFAULT NULL COMMENT '前加工工时',
  `assemble_uph` double(10,2) DEFAULT NULL COMMENT '组装uph',
  `assemble_upph` double(10,2) DEFAULT NULL COMMENT '组装upph',
  `assemble_hour` double(10,2) DEFAULT NULL COMMENT '组装工时',
  `packaging_uph` double(10,2) DEFAULT NULL COMMENT '包装uph',
  `packaging_upph` double(10,2) DEFAULT NULL COMMENT '包装upph',
  `packaging_hour` double(10,2) DEFAULT NULL COMMENT '包装工时',
  `mam_hour_total` double(10,2) DEFAULT NULL COMMENT '总工时',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `update_name` varchar(30) DEFAULT NULL COMMENT '更新人名称',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_man_hour_material_code` (`material_code`)
) ENGINE=InnoDB AUTO_INCREMENT=1930507321253285892 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='标准工时库';

-- ----------------------------
-- Table structure for production_standard_man_hour_detail
-- ----------------------------
DROP TABLE IF EXISTS `production_standard_man_hour_detail`;
CREATE TABLE `production_standard_man_hour_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `man_hour_id` bigint DEFAULT NULL COMMENT '标准工时总表主键',
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `process_type` tinyint NOT NULL COMMENT '工序类型 1-镭雕 2-前加工 3-组装 4-包装',
  `sort` tinyint DEFAULT NULL COMMENT '排序',
  `station_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工位',
  `manpower_count` double(10,2) DEFAULT NULL COMMENT '人力配置',
  `observation_man_hour_a` double(10,2) DEFAULT NULL COMMENT '观测工时1',
  `observation_man_hour_b` double(10,2) DEFAULT NULL COMMENT '观测工时2',
  `observation_man_hour_c` double(10,2) DEFAULT NULL COMMENT '观测工时3',
  `observation_man_hour_d` double(10,2) DEFAULT NULL COMMENT '观测工时4',
  `observation_man_hour_e` double(10,2) DEFAULT NULL COMMENT '观测工时5',
  `expand_rate` double(10,2) DEFAULT NULL COMMENT '放宽率',
  `station_man_hour` double(10,2) DEFAULT NULL COMMENT '工位标准工时',
  `unit_per_hour` double(10,2) DEFAULT NULL COMMENT '工位uph',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `update_name` varchar(30) DEFAULT NULL COMMENT '更新人名称',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_detail_man_hour_id` (`man_hour_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1930507321282646020 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='标准工时库详情';

-- ----------------------------
-- Table structure for production_submit_work_record
-- ----------------------------
DROP TABLE IF EXISTS `production_submit_work_record`;
CREATE TABLE `production_submit_work_record` (
  `id` bigint NOT NULL,
  `ltxa1` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '报工批次号',
  `aufnr` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产订单号',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间ID',
  `workshop_name` varchar(30) DEFAULT NULL COMMENT '车间名称',
  `line_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编码',
  `line_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别名称',
  `person_hours` int DEFAULT '0' COMMENT '人力',
  `bill_qty` decimal(10,3) DEFAULT NULL COMMENT '工单数量',
  `vornr` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序号',
  `process_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序名称',
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `matxt` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `budat` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '过账日期',
  `lmnga` decimal(10,3) DEFAULT NULL COMMENT '产量',
  `meinh` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '产量单位',
  `ausor` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '结清未清预留',
  `aueru` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '确认类型 部分确认: 自动最终确认:1 最后确认:X',
  `xmnga` decimal(10,3) DEFAULT NULL COMMENT '报废数量',
  `rmnga` decimal(10,3) DEFAULT NULL COMMENT '返工数量',
  `ism01` decimal(10,2) DEFAULT '0.00' COMMENT '人工工时',
  `ile01` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '人工工时单位',
  `ism02` decimal(10,2) DEFAULT NULL COMMENT '变动工时',
  `ile02` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '变动工时单位',
  `ism03` decimal(10,2) DEFAULT NULL COMMENT '固定工时',
  `ile03` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '固定工时单位',
  `endp` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否为最后一道工序 否:0 是:1',
  `erfmg` decimal(10,3) DEFAULT '0.000' COMMENT '入库数量',
  `erfme` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '入库单位',
  `bldat_mb` date DEFAULT NULL COMMENT '入库凭证日期',
  `budat_mb` date DEFAULT NULL COMMENT '入库过账日期',
  `werks` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂',
  `lgort` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '库位',
  `start_time` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '开始时间',
  `end_time` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '结束时间',
  `work_type` tinyint DEFAULT '1' COMMENT '报工类型 1:正常报工 2:异常报工',
  `duty_department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '责任部门',
  `abnormal_description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '异常描述',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0：未删除 1：已删除',
  `tenant_code` bigint DEFAULT '1001' COMMENT '租户编码',
  `variation_analysis` decimal(10,2) DEFAULT '0.00' COMMENT '差异分析',
  `work_status` bit(1) DEFAULT b'0' COMMENT '报工状态 0:未报工 1:已报工',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产报工记录';

-- ----------------------------
-- Table structure for production_task
-- ----------------------------
DROP TABLE IF EXISTS `production_task`;
CREATE TABLE `production_task` (
  `id` bigint NOT NULL,
  `production_shift_id` bigint DEFAULT NULL COMMENT '生产班次ID',
  `production_shift_hour` decimal(4,2) DEFAULT NULL COMMENT '班次工时',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间ID',
  `workshop_name` varchar(30) DEFAULT NULL COMMENT '车间名称',
  `assembly_line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编码',
  `assembly_line_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `process_type_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序类型编码',
  `work_process_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序类型',
  `workshop_section` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工段',
  `workshop_section_type` tinyint(1) DEFAULT NULL COMMENT '1：主工段  0：次工段',
  `production_task_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产任务号',
  `bill_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `bill_qty` int DEFAULT NULL COMMENT '工单数量',
  `bill_type` varchar(5) DEFAULT NULL COMMENT '订单类型（ZZ-自制 WW-委外）',
  `production_date` date DEFAULT NULL COMMENT '生产日期',
  `plan_start_time` datetime DEFAULT NULL COMMENT '计划开工时间',
  `plan_end_time` datetime DEFAULT NULL COMMENT '计划完工时间',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `task_qty` int DEFAULT NULL COMMENT '任务数量',
  `uph` int DEFAULT NULL COMMENT 'UPH',
  `completed_qty` int DEFAULT '0' COMMENT '完成数量',
  `priority` int DEFAULT '999' COMMENT '优先级',
  `task_status` tinyint(1) DEFAULT NULL COMMENT '任务状态 1:未开始 2:生产中 3:已完成 4:异常 5:已关闭 6:未完成 7:待清尾',
  `operation_code` varchar(50) DEFAULT NULL COMMENT '工作编号',
  `task_type` tinyint DEFAULT '1' COMMENT '任务类型 0-更新 1-新增',
  `production_hours` decimal(8,2) DEFAULT '0.00' COMMENT '生产工时',
  `remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `norm_man_hour` decimal(5,1) DEFAULT NULL COMMENT '标准工时',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `expected_usage_time` datetime DEFAULT NULL COMMENT '设备预期使用时间',
  `device_ready_status` tinyint NOT NULL DEFAULT '1' COMMENT '设备准备状态；1待备中，2已备齐',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_production_shift_id` (`production_shift_id`,`assembly_line_code`,`process_type_code`,`bill_no`,`production_date`,`workshop_section`,`production_task_no`),
  UNIQUE KEY `idx_uk_assembly_line_code` (`assembly_line_code`,`bill_no`,`production_date`,`work_process_type`,`tenant_code`,`workshop_section`,`production_task_no`,`workshop_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='生产任务';

-- ----------------------------
-- Table structure for production_task_board
-- ----------------------------
DROP TABLE IF EXISTS `production_task_board`;
CREATE TABLE `production_task_board` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `process_type_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序类型编码',
  `assembly_line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `production_date` date DEFAULT NULL COMMENT '生产日期',
  `remark` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_assembly_line_code` (`assembly_line_code`,`production_date`,`tenant_code`,`process_type_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='生产任务达成率看板备注';

-- ----------------------------
-- Table structure for production_task_hint
-- ----------------------------
DROP TABLE IF EXISTS `production_task_hint`;
CREATE TABLE `production_task_hint` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `production_task_id` bigint DEFAULT NULL COMMENT '生产任务ID',
  `user_id` bigint DEFAULT NULL COMMENT '用户ID',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uq_production_task_id` (`production_task_id`,`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=21317 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='生产任务完成弹框';

-- ----------------------------
-- Table structure for production_task_lost_time_record
-- ----------------------------
DROP TABLE IF EXISTS `production_task_lost_time_record`;
CREATE TABLE `production_task_lost_time_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `line_stop_flag` bit(1) DEFAULT NULL COMMENT '是否停线 0:否 1:是',
  `line_code` varchar(20) DEFAULT NULL COMMENT '线别编码',
  `line_name` varchar(20) DEFAULT NULL COMMENT '线别名称',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间ID',
  `workshop_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '车间名称',
  `process_type_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '工序类型编码',
  `work_process_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '工序类型',
  `department` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '责任部门',
  `production_date` date DEFAULT NULL COMMENT '生产日期',
  `exception_type` varchar(20) DEFAULT NULL COMMENT '异常原因',
  `factor` varchar(20) DEFAULT NULL COMMENT '损失类型',
  `manpower` int DEFAULT NULL COMMENT '投入人数',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `qty` int DEFAULT NULL COMMENT '生产数量',
  `uph` int DEFAULT NULL COMMENT 'UPH',
  `unit_lost_hours` decimal(6,2) DEFAULT NULL COMMENT '单位损失工时',
  `total_lost_hours` decimal(6,2) DEFAULT NULL COMMENT '总损失工时',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料名称',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  `submit_status` tinyint(1) DEFAULT NULL COMMENT '提交状态 1:未提交 2:已提交',
  `start_qty` int DEFAULT NULL COMMENT '开始时间生产数量',
  `end_qty` int DEFAULT NULL COMMENT '结束时间生产数量',
  `attachment_url` varchar(100) DEFAULT NULL COMMENT '附件地址',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1930896547411881987 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='制造损失工时记录';

-- ----------------------------
-- Table structure for production_task_report
-- ----------------------------
DROP TABLE IF EXISTS `production_task_report`;
CREATE TABLE `production_task_report` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `process_type_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序类型编码',
  `assembly_line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `production_date` date DEFAULT NULL COMMENT '生产日期',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `remark` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_assembly_line_code` (`assembly_line_code`,`production_date`,`tenant_code`,`process_type_code`,`material_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='生产任务达成率报表备注';

-- ----------------------------
-- Table structure for production_task_section
-- ----------------------------
DROP TABLE IF EXISTS `production_task_section`;
CREATE TABLE `production_task_section` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `workshop_section` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工段',
  `workshop_section_type` tinyint(1) DEFAULT '1' COMMENT '1：主工段  0：次工段',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `create_name` varchar(30) DEFAULT NULL COMMENT '创建人名称',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `update_name` varchar(30) DEFAULT NULL COMMENT '更新人名称',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1683316977010413572 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='生产任务工段';

-- ----------------------------
-- Table structure for production_wi_line
-- ----------------------------
DROP TABLE IF EXISTS `production_wi_line`;
CREATE TABLE `production_wi_line` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `wi_id` bigint DEFAULT NULL COMMENT 'WI标工ID',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间ID',
  `workshop_name` varchar(30) DEFAULT NULL COMMENT '车间名称',
  `line_code` varchar(30) DEFAULT NULL COMMENT '线别编码',
  `line_name` varchar(30) DEFAULT NULL COMMENT '线别名称',
  `line_code_priority` int DEFAULT NULL COMMENT '线别优先级',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_line_code` (`line_code`,`line_code_priority`,`wi_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1931288193290956803 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='工序线别';

-- ----------------------------
-- Table structure for production_wi_video
-- ----------------------------
DROP TABLE IF EXISTS `production_wi_video`;
CREATE TABLE `production_wi_video` (
  `id` bigint DEFAULT NULL COMMENT 'id',
  `wi_id` bigint DEFAULT NULL COMMENT 'WI标工ID',
  `file_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '文件名称',
  `file_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '文件地址',
  `file_type` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '文件类型',
  `file_size` double(20,2) DEFAULT NULL COMMENT '文件大小',
  `file_sort` tinyint DEFAULT NULL COMMENT '文件顺序'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for production_wi_worker
-- ----------------------------
DROP TABLE IF EXISTS `production_wi_worker`;
CREATE TABLE `production_wi_worker` (
  `id` bigint NOT NULL COMMENT 'id',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `material_specification` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料规格',
  `wi_type` tinyint DEFAULT NULL COMMENT '类型值 0:产品 1:PCBA',
  `manpower` int DEFAULT NULL COMMENT '标准人力',
  `work_process_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序类型',
  `work_process_no` varchar(20) DEFAULT NULL COMMENT '工序号',
  `line_code` varchar(300) DEFAULT NULL COMMENT '线别编码 多个用;分隔',
  `line_code_priority` int DEFAULT NULL COMMENT '优先级默',
  `workshop_name` varchar(30) DEFAULT NULL COMMENT '车间名称',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间ID',
  `capacity` int DEFAULT NULL COMMENT '产能（H）',
  `mean_value` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '人均值',
  `instruction_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '作业指导书名称',
  `instruction_url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '作业指导书文件地址',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `sip_url` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'SIP',
  `sip_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'SIP文件名称',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_material_code` (`material_code`,`work_process_type`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='WI及标工';

-- ----------------------------
-- Table structure for production_wi_worker_test
-- ----------------------------
DROP TABLE IF EXISTS `production_wi_worker_test`;
CREATE TABLE `production_wi_worker_test` (
  `id` bigint DEFAULT NULL COMMENT 'id',
  `material_code` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '物料名称',
  `material_specification` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料规格',
  `wi_type` tinyint DEFAULT NULL COMMENT '类型值 0:产品 1:PCBA',
  `manpower` int DEFAULT NULL COMMENT '标准人力',
  `work_process_type` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '工序类型',
  `work_process_no` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '工序号',
  `line_code` varchar(300) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '线别编码 多个，逗号分隔',
  `line_code_priority` int DEFAULT NULL COMMENT '优先级默',
  `workshop_name` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '车间名称',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间ID',
  `capacity` int DEFAULT NULL COMMENT '产能（H）',
  `mean_value` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '人均值',
  `instruction_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '作业指导书名称',
  `instruction_url` varchar(200) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '作业指导书文件地址',
  `remark` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) COLLATE utf8mb4_general_ci DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `sip_url` varchar(500) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'SIP',
  `sip_name` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT 'SIP文件名称',
  UNIQUE KEY `idx_uk_material_code` (`material_code`,`work_process_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='WI及标工（测试）';

-- ----------------------------
-- Table structure for push_sap_task
-- ----------------------------
DROP TABLE IF EXISTS `push_sap_task`;
CREATE TABLE `push_sap_task` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `batch_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '批次单号',
  `bill_number` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单据编号',
  `source` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '源头',
  `business_type` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '类型编码',
  `business_type_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '类型名称',
  `request_params` json DEFAULT NULL COMMENT '参数',
  `status` tinyint(1) DEFAULT '0' COMMENT '状态（0:推送中,1:成功,2:失败）',
  `response_params` json DEFAULT NULL COMMENT '返回参数',
  `remark` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除1-已删除',
  `tenant_code` varchar(30) DEFAULT NULL COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `index_bill_number` (`bill_number`)
) ENGINE=InnoDB AUTO_INCREMENT=1930965069345288195 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='推送SAP任务列表';

-- ----------------------------
-- Table structure for scada_accessories_scan_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_accessories_scan_record`;
CREATE TABLE `scada_accessories_scan_record` (
  `id` bigint NOT NULL,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产订单',
  `bill_qty` int DEFAULT NULL COMMENT '工单数量',
  `workshop_name` varchar(50) DEFAULT NULL COMMENT '车间名称',
  `line_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `material_source` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'SC' COMMENT '物料来源 SC:生产 CG:采购',
  `scan_date` datetime DEFAULT NULL COMMENT '扫描时间',
  `white_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '白盒号',
  `qty` int DEFAULT NULL COMMENT '数量',
  `send_inspect_status` tinyint DEFAULT '0' COMMENT '是否送检 0：未送检 1：已送检',
  `into_stock_status` tinyint DEFAULT '0' COMMENT '入库状态 0-未入库 1-已入库',
  `check_result` tinyint DEFAULT '1' COMMENT '质检结果 0-不合格 1-合格',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0：未删除 1：已删除',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `idx_into_stock_status_white_package_no` (`into_stock_status`,`white_package_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='配件扫描记录';

-- ----------------------------
-- Table structure for scada_aging_car_sn_relation
-- ----------------------------
DROP TABLE IF EXISTS `scada_aging_car_sn_relation`;
CREATE TABLE `scada_aging_car_sn_relation` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `inspect_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '送检单号',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间id',
  `line_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别代码',
  `aging_car_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '老化车编码',
  `aging_car_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '老化车名称',
  `bill_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `sn` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'SN',
  `inspect_status` tinyint DEFAULT NULL COMMENT '送检状态 0-未送检 1-已送检',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0：未删除 1：已删除',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `index_inspect_status` (`inspect_status`) USING BTREE,
  KEY `index_sn` (`sn`,`del_flag`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1930967958105059331 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='老化车与sn关系表';

-- ----------------------------
-- Table structure for scada_aging_test_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_aging_test_record`;
CREATE TABLE `scada_aging_test_record` (
  `id` bigint NOT NULL,
  `warehouse_id` bigint DEFAULT NULL COMMENT '库位id',
  `work_type` tinyint DEFAULT NULL COMMENT '充电/老化 1 充电 2老化 ',
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `end_status` tinyint DEFAULT '0' COMMENT '当前是否完成状态 0-未完成 1-完成',
  `duration` int DEFAULT NULL COMMENT '运行时长 单位分钟',
  `charge_times` tinyint DEFAULT '1' COMMENT '充电次数',
  `product_count` int DEFAULT NULL COMMENT '测试产品数量',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT NULL COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_aging_warehouse_id` (`warehouse_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='老化测试记录表';

-- ----------------------------
-- Table structure for scada_aging_warehouse_manage
-- ----------------------------
DROP TABLE IF EXISTS `scada_aging_warehouse_manage`;
CREATE TABLE `scada_aging_warehouse_manage` (
  `id` bigint NOT NULL,
  `workshop_id` bigint DEFAULT NULL COMMENT '车间id',
  `warehouse` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '库位',
  `warehouse_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '库位编码',
  `use_status` tinyint DEFAULT '0' COMMENT '占用状态 0:已释放 1:送检中 2:检验中',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `image_url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '图片地址',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT NULL COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='老化库位管理表';

-- ----------------------------
-- Table structure for scada_assemble_scan_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_assemble_scan_record`;
CREATE TABLE `scada_assemble_scan_record` (
  `id` bigint NOT NULL,
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产线号',
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `workshop_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '车间名称',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称（机型）',
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `bad_status` tinyint DEFAULT '0' COMMENT '0-良品 1-不良品 2-已维修',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_assemble_scan_sn` (`sn`) USING BTREE,
  KEY `idx_bill_no_line_code` (`bill_no`,`line_code`) USING BTREE,
  KEY `idx_assemble_create_date` (`create_time`),
  KEY `idx_linecode_tenantcode_createdate_materialcode` (`line_code`,`tenant_code`,`create_time`,`material_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='组装扫描数据记录表';

-- ----------------------------
-- Table structure for scada_ex_warehouse_oqc_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_ex_warehouse_oqc_record`;
CREATE TABLE `scada_ex_warehouse_oqc_record` (
  `id` bigint NOT NULL,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产工单号',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `material_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `order_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单据号',
  `bad_status` tinyint DEFAULT '0' COMMENT '不良状态 0-良品 1-不良品 2-已维修',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本号',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_order_no_sn` (`order_no`,`sn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='出库OQC扫描记录';

-- ----------------------------
-- Table structure for scada_fqc_scan_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_fqc_scan_record`;
CREATE TABLE `scada_fqc_scan_record` (
  `id` bigint NOT NULL,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `workshop_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '车间名称',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '产品名称',
  `bad_status` tinyint DEFAULT '0' COMMENT '0-良品 1-不良品 2-已维修',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_fqc_scan_sn` (`sn`) USING BTREE,
  KEY `idx_fqc_scan_bill_no` (`bill_no`),
  KEY `idx_fqc_create_date` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='FQC扫描记录表';

-- ----------------------------
-- Table structure for scada_hour
-- ----------------------------
DROP TABLE IF EXISTS `scada_hour`;
CREATE TABLE `scada_hour` (
  `id` bigint NOT NULL,
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编码',
  `process_type_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序编码',
  `hour` int DEFAULT NULL COMMENT '小时',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_uk_material_code` (`line_code`,`process_type_code`,`hour`) USING BTREE,
  KEY `idx_linecode_processtypecode_createtime` (`line_code`,`process_type_code`,`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='小时扫描时间';

-- ----------------------------
-- Table structure for scada_into_warehouse_oqc_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_into_warehouse_oqc_record`;
CREATE TABLE `scada_into_warehouse_oqc_record` (
  `id` bigint NOT NULL,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产工单号',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `material_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `order_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单据号',
  `bad_status` tinyint DEFAULT '0' COMMENT '不良状态 0-良品 1-不良品 2-已维修',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(100) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本号',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_order_no_sn` (`order_no`,`sn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='入库OQC扫描记录';

-- ----------------------------
-- Table structure for scada_oqc_send_inspect_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_oqc_send_inspect_record`;
CREATE TABLE `scada_oqc_send_inspect_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `workshop_name` varchar(50) DEFAULT NULL COMMENT '车间名称',
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编号',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `material_source` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'SC' COMMENT '物料来源 SC:生产 CG:采购',
  `big_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '外箱箱号',
  `white_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '白盒号',
  `material_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '料箱编号',
  `package_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '扫描类型',
  `order_line_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '订单行号',
  `send_inspect_status` tinyint DEFAULT '0' COMMENT '送检状态 0:未送检 1:已送检',
  `check_result` tinyint DEFAULT '1' COMMENT '检验结果 0-不合格 1-合格',
  `send_inspect_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '送检单号',
  `qty` int DEFAULT '1' COMMENT '送检数量',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本号',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_send_inspect_no_sn` (`send_inspect_no`,`sn`),
  KEY `idx_tenant_code_del_flag` (`tenant_code`,`del_flag`),
  KEY `idx_send_inspect_status` (`send_inspect_status`),
  KEY `idx_sn_send_inspect_status_check_result` (`sn`,`send_inspect_status`,`check_result`)
) ENGINE=InnoDB AUTO_INCREMENT=5526720 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='OQC送检记录';

-- ----------------------------
-- Table structure for scada_package_scan_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_package_scan_record`;
CREATE TABLE `scada_package_scan_record` (
  `id` bigint NOT NULL,
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `workshop_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '车间名称',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '产品名称',
  `material_weight` float(16,0) DEFAULT NULL COMMENT '产品重量(单位：g)',
  `big_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '外箱箱号',
  `white_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '白箱箱号',
  `material_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '料盒编号',
  `package_status` tinyint DEFAULT '0' COMMENT '(白盒，料盒)封箱状态 1-封箱 0-未封箱',
  `rework_status` tinyint DEFAULT '0' COMMENT '是否返工 0-不是 1-是返工',
  `quantity_per_case` int DEFAULT NULL COMMENT '每箱数量',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `version` int DEFAULT '1' COMMENT '版本',
  `package_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '包装类型 大箱 MasterSN，白盒CartonSN，料盒MaterialSN 无为None',
  `big_package_status` tinyint DEFAULT '0' COMMENT '大箱封箱状态 1-封箱 0-未封箱',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_package_scan_sn` (`sn`) USING BTREE,
  KEY `idx_package_white_no` (`white_package_no`) USING BTREE,
  KEY `idx_package_big_no` (`big_package_no`) USING BTREE,
  KEY `idx_package_create_date` (`create_time`),
  KEY `idx_package_material_no` (`material_package_no`) USING BTREE,
  KEY `idx_package_bill_no` (`bill_no`) USING BTREE,
  KEY `idx_package_line_code` (`line_code`),
  KEY `idx_material_code` (`material_code`) USING BTREE,
  KEY `idx_linecode_packagetype_tenantcode_delflag_packagestatus` (`line_code`,`package_type`,`tenant_code`,`del_flag`,`package_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='称重打包扫描记录表';

-- ----------------------------
-- Table structure for scada_repair_scan_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_repair_scan_record`;
CREATE TABLE `scada_repair_scan_record` (
  `id` bigint NOT NULL,
  `maintenance_plan` varchar(800) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '维修方案',
  `bad_cause` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良原因',
  `rejects_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良代码编码',
  `bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `line_code` varchar(20) DEFAULT NULL COMMENT '线别编码',
  `checker` varchar(20) DEFAULT NULL COMMENT '检验人',
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `supplier_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商id',
  `supplier_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商名字',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本号',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `bad_classify` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_repair_scan_sn` (`sn`) USING BTREE,
  KEY `idx_repair_bill_no` (`bill_no`) USING BTREE,
  KEY `idx_rejects_code` (`rejects_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='维修扫描记录表';

-- ----------------------------
-- Table structure for scada_shipment_scan_record
-- ----------------------------
DROP TABLE IF EXISTS `scada_shipment_scan_record`;
CREATE TABLE `scada_shipment_scan_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '线别编码',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '产品序列号',
  `third_party_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '第三方条码',
  `package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '外箱号',
  `order_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '订单号',
  `scan_type` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '扫描类型：W-整箱(白盒)扫描 B-整箱(大箱)扫描 S-单个产品扫描',
  `white_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '原来包装白盒的编号',
  `big_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '原来包装的大箱的编号',
  `material_package_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '原来包装的料盒的编号',
  `material_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料名称',
  `sealing_box_status` tinyint DEFAULT '0' COMMENT '封箱状态 1-封箱 0-未封',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT NULL COMMENT '版本',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(30) COLLATE utf8mb4_general_ci DEFAULT '1001' COMMENT '租户编码',
  `country` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '国家名称',
  `customer_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '客户编码',
  `salesman` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '业务员',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `sale_type` varchar(10) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '销售类型 B2C B2B',
  `sale_warehouse` varchar(30) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '销售仓库',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_shipment_big_package_no` (`big_package_no`),
  KEY `idx_shipment_white_package_no` (`white_package_no`),
  KEY `idx_shipment_sn` (`sn`),
  KEY `idx_shipment_package_no` (`package_no`),
  KEY `idx_uk_order_no_material` (`order_no`,`material_code`) USING BTREE,
  KEY `idx_shipment_material_no` (`material_package_no`),
  KEY `idx_create_date` (`create_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1931422746915598341 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT=' 出货记录表';

-- ----------------------------
-- Table structure for scada_sn_rejects_code
-- ----------------------------
DROP TABLE IF EXISTS `scada_sn_rejects_code`;
CREATE TABLE `scada_sn_rejects_code` (
  `id` bigint NOT NULL,
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '序列号',
  `line_code` varchar(20) DEFAULT NULL COMMENT '线别',
  `checker` varchar(20) DEFAULT NULL COMMENT '检验人',
  `scan_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '扫描类型 FQC ASSEMBLE',
  `rejects_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良代码编码',
  `repair_status` tinyint DEFAULT '0' COMMENT '0-待修 1-已修 2-已扫描待修',
  `record_id` bigint NOT NULL COMMENT '扫描记录id',
  `repair_id` bigint DEFAULT NULL COMMENT '维修表id',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本号',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_sn_rejects_code` (`sn`) USING BTREE,
  KEY `idx_rejects_code_sn` (`rejects_code`) USING BTREE,
  KEY `idx_sn_record_id` (`record_id`) USING BTREE,
  KEY `idx_rejects_create_date` (`create_time`),
  KEY `idx_repair_id` (`repair_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='维修扫描不良代码中间表';

-- ----------------------------
-- Table structure for sn_operating_record
-- ----------------------------
DROP TABLE IF EXISTS `sn_operating_record`;
CREATE TABLE `sn_operating_record` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `bill_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单号',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'SN',
  `work_process_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工序',
  `operation_status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'OK' COMMENT '操作状态  成功：OK  失败：FAILL',
  `operating` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '操作',
  `link_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `version` int DEFAULT '1' COMMENT '版本',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `tenant_code` varchar(20) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_bill_no` (`bill_no`) USING BTREE,
  KEY `idx_sn` (`sn`) USING BTREE,
  KEY `idx_work_process_name` (`work_process_name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1931340459708477443 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='SN操作记录';

-- ----------------------------
-- Table structure for sys_operate_log
-- ----------------------------
DROP TABLE IF EXISTS `sys_operate_log`;
CREATE TABLE `sys_operate_log` (
  `id` bigint NOT NULL,
  `operate_number` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '业务单号',
  `operate_module` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '功能模块',
  `interface_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '接口类型(admin:内部接口,inner:feign接口,external:外部接口)',
  `menu_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '模块编码',
  `menu_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '模块名称',
  `operate_type` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '操作类型',
  `operate_desc` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '操作描述',
  `req_type` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '请求方式',
  `status` tinyint(1) DEFAULT '0' COMMENT '0:成功,1:失败',
  `operate_ip` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Ip地址',
  `operate_url` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '请求url',
  `operate_method` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '操作方法',
  `operate_path` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '方法路径',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `index_operate_module` (`operate_module`) USING BTREE,
  KEY `index_menu_code` (`menu_code`) USING BTREE,
  KEY `index_operate_number` (`operate_number`) USING BTREE,
  KEY `index_create_time` (`create_time`) USING BTREE,
  KEY `index_operate_type` (`operate_type`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统操作日志';

-- ----------------------------
-- Table structure for sys_operate_log_text
-- ----------------------------
DROP TABLE IF EXISTS `sys_operate_log_text`;
CREATE TABLE `sys_operate_log_text` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键Id',
  `log_id` bigint DEFAULT NULL COMMENT '关联主表Id',
  `operate_number` varchar(50) DEFAULT NULL COMMENT '业务单号',
  `req_param` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '请求参数',
  `resp_param` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '返回参数',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_log_id` (`log_id`) USING BTREE,
  KEY `index_operate_number` (`operate_number`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1931422237945196548 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='系统操作日志大文件记录表';

-- ----------------------------
-- Table structure for wechat_user_notice_info
-- ----------------------------
DROP TABLE IF EXISTS `wechat_user_notice_info`;
CREATE TABLE `wechat_user_notice_info` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `wechat_type` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '通知类型',
  `wechat_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '通知模板编码,对应发送模板code',
  `wechat_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '通知名称',
  `wechat_users` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '推送的人员',
  `remark` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人名称',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `index_wechat_code` (`wechat_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1397889316463878148 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='企业微信用户发送通知';

-- ----------------------------
-- Table structure for wms_sn_operation_record_history
-- ----------------------------
DROP TABLE IF EXISTS `wms_sn_operation_record_history`;
CREATE TABLE `wms_sn_operation_record_history` (
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '产品条码',
  `country` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '国家',
  `order_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '销售订单号',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `create_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '操作员',
  `sale_warehouse` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '发货仓库',
  `sale_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '销售类型'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='sn操作记录表';

SET FOREIGN_KEY_CHECKS = 1;
