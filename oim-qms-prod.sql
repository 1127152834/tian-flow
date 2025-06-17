/*
 Navicat Premium Data Transfer

 Source Server         : 傲雷
 Source Server Type    : MySQL
 Source Server Version : 80025 (8.0.25)
 Source Host           : rm-wz92v0p5r77n91210wo.mysql.rds.aliyuncs.com:3306
 Source Schema         : oim-qms-prod

 Target Server Type    : MySQL
 Target Server Version : 80025 (8.0.25)
 File Encoding         : 65001

 Date: 08/06/2025 02:46:59
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for outsource_qc_check_bill
-- ----------------------------
DROP TABLE IF EXISTS `outsource_qc_check_bill`;
CREATE TABLE `outsource_qc_check_bill` (
  `id` bigint NOT NULL,
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `specification_model` varchar(150) DEFAULT NULL COMMENT '规格型号',
  `unit` varchar(6) DEFAULT NULL COMMENT '计量单位',
  `material_qty` int DEFAULT '0' COMMENT '送检数量/待检数量',
  `scan_qty` int DEFAULT '0' COMMENT '已扫描数量',
  `sample_qty` int DEFAULT NULL COMMENT '抽样数量',
  `supplier_id` varchar(50) DEFAULT NULL COMMENT '供应商id',
  `supplier_name` varchar(50) DEFAULT '' COMMENT '供应商名称',
  `shop` varchar(50) DEFAULT NULL COMMENT '店铺',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 0:待审核 4:已检验 5:待出库 7:待检验 8:检验中',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果;0:不合格 1:合格',
  `checker` varchar(255) DEFAULT NULL COMMENT '检验人',
  `checker_job_number` varchar(255) DEFAULT NULL COMMENT '检验人工号',
  `check_remark` varchar(500) DEFAULT NULL COMMENT '检验备注',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `below_standard_cause` varchar(255) DEFAULT NULL COMMENT '不合格原因',
  `auditor` varchar(30) DEFAULT NULL COMMENT '审核人',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `audit_status` tinyint DEFAULT NULL COMMENT '审核状态 0:审核通过 1:审核不通过',
  `audit_remark` varchar(255) DEFAULT NULL COMMENT '审核备注',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `factory_code` varchar(6) DEFAULT '2000' COMMENT '工厂代码',
  `stock_location` varchar(6) DEFAULT NULL COMMENT '库存地点',
  `material_voucher` varchar(20) DEFAULT NULL COMMENT '物料凭证',
  `re_push` tinyint DEFAULT '1' COMMENT '是否需要重推 0-否 1-是',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='委外检验单';

-- ----------------------------
-- Table structure for outsource_qc_check_bill_detail
-- ----------------------------
DROP TABLE IF EXISTS `outsource_qc_check_bill_detail`;
CREATE TABLE `outsource_qc_check_bill_detail` (
  `id` bigint NOT NULL COMMENT 'ID',
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验单ID',
  `gsn` varchar(30) DEFAULT NULL COMMENT 'GSN或SN',
  `qty` int DEFAULT '1' COMMENT '数量',
  `check_status` tinyint DEFAULT '0' COMMENT '是否检验  0:未检验 1:已检验',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果 0:不合格 1:合格',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `purchase_no` varchar(255) DEFAULT NULL COMMENT '采购订单',
  `purchase_type` varchar(6) DEFAULT NULL COMMENT '订单类型',
  `order_line_code` varchar(30) DEFAULT '1' COMMENT '订单行号',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_check_bill_id_gsn` (`check_bill_id`,`gsn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='委外检验单明细';

-- ----------------------------
-- Table structure for outsource_return_check_bill
-- ----------------------------
DROP TABLE IF EXISTS `outsource_return_check_bill`;
CREATE TABLE `outsource_return_check_bill` (
  `id` bigint NOT NULL,
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `delivery_no` varchar(30) DEFAULT NULL COMMENT '送货单号',
  `receive_no` varchar(30) DEFAULT NULL COMMENT '收料单号',
  `purchase_type` varchar(5) DEFAULT 'Z002' COMMENT '采购类型',
  `purchase_no` varchar(30) DEFAULT NULL COMMENT '采购单号',
  `line_code` varchar(4) DEFAULT NULL COMMENT '采购单行号',
  `supplier_id` varchar(50) DEFAULT NULL COMMENT '供应商id',
  `supplier_name` varchar(50) DEFAULT NULL COMMENT '供应商名称',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `unit` varchar(6) DEFAULT NULL COMMENT '计量单位',
  `return_qty` int DEFAULT '0' COMMENT '退货数量',
  `return_reason` text COMMENT '退货原因',
  `factory_code` varchar(6) DEFAULT '2000' COMMENT '工厂代码',
  `stock_location` varchar(6) DEFAULT '1999' COMMENT '库存地点',
  `material_voucher` varchar(20) DEFAULT NULL COMMENT '收料凭证',
  `voucher_year` varchar(4) DEFAULT NULL COMMENT '收料凭证年份',
  `bill_status` tinyint DEFAULT '1' COMMENT '检验状态 1:待IQC确认 2:待SQE确认 3:已完结',
  `qc_check_name` varchar(30) DEFAULT NULL COMMENT 'QC确认人',
  `qc_check_time` datetime DEFAULT NULL COMMENT 'QC确认时间',
  `qc_check_result` tinyint DEFAULT '0' COMMENT 'QC确认结果 0:待确认 1:符合 2:不符合',
  `sqe_check_name` varchar(30) DEFAULT NULL COMMENT 'SQE确认人',
  `sqe_check_time` datetime DEFAULT NULL COMMENT 'SQE确认时间',
  `sqe_check_result` tinyint DEFAULT '0' COMMENT 'SQE确认结果 0:待确认 1:符合 2:不符合',
  `cost_center_code` varchar(20) DEFAULT NULL COMMENT '成本中心代码',
  `post_voucher` varchar(20) DEFAULT NULL COMMENT '过账凭证',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识(0-未删除/1-删除)',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='委外退货确认单';

-- ----------------------------
-- Table structure for oxsys_check_package_bill
-- ----------------------------
DROP TABLE IF EXISTS `oxsys_check_package_bill`;
CREATE TABLE `oxsys_check_package_bill` (
  `id` bigint NOT NULL,
  `sort` int DEFAULT '9999' COMMENT '排序',
  `urgency_flag` tinyint DEFAULT '0' COMMENT '是否紧急;0:正常  1:紧急',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `specification_model` varchar(150) DEFAULT NULL COMMENT '规格型号',
  `send_check_qty` int DEFAULT '0' COMMENT '送检数量',
  `standard_qty` int DEFAULT '0' COMMENT '合格数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `below_standard_cause` varchar(255) DEFAULT NULL COMMENT '不合格原因',
  `customer_code` varchar(20) DEFAULT NULL COMMENT '客户编码',
  `customer_name` varchar(30) DEFAULT NULL COMMENT '客户名称',
  `send_check_time` datetime DEFAULT NULL COMMENT '送检时间',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `predict_complete_time` datetime DEFAULT NULL COMMENT '预计完成时间',
  `bill_no` varchar(20) DEFAULT NULL COMMENT '关联生产订单',
  `batch_no` varchar(50) DEFAULT NULL COMMENT '批次号',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 4:已检验 7:待检验 8:检验中',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果;0:不合格 1:合格',
  `checker_job_number` varchar(255) DEFAULT NULL COMMENT '检验人工号',
  `checker` varchar(255) DEFAULT NULL COMMENT '检验人',
  `check_remark` varchar(500) DEFAULT NULL COMMENT '检验备注',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `factory_code` varchar(6) DEFAULT '2200' COMMENT '工厂代码',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(6) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='氧化厂检包列表';

-- ----------------------------
-- Table structure for oxsys_check_package_bill_detail
-- ----------------------------
DROP TABLE IF EXISTS `oxsys_check_package_bill_detail`;
CREATE TABLE `oxsys_check_package_bill_detail` (
  `id` bigint NOT NULL COMMENT 'ID',
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验单ID',
  `gsn` varchar(30) DEFAULT NULL COMMENT 'GSN',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint NOT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='氧化厂检包明细';

-- ----------------------------
-- Table structure for oxsys_iqc_check_bill
-- ----------------------------
DROP TABLE IF EXISTS `oxsys_iqc_check_bill`;
CREATE TABLE `oxsys_iqc_check_bill` (
  `id` bigint NOT NULL,
  `sort` int DEFAULT '9999' COMMENT '排序',
  `urgency_flag` tinyint DEFAULT '0' COMMENT '是否紧急;0:正常  1:紧急',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `material_source` varchar(2) DEFAULT 'CG' COMMENT '物料来源 SC:生产 CG:采购 XS:销售',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `specification_model` varchar(150) DEFAULT NULL COMMENT '规格型号',
  `send_check_qty` int DEFAULT '0' COMMENT '送检数量',
  `scan_qty` int DEFAULT '0' COMMENT '已扫描数量',
  `sample_qty` int DEFAULT '0' COMMENT '抽样数量',
  `standard_qty` int DEFAULT '0' COMMENT '合格数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `below_standard_cause` varchar(255) DEFAULT NULL COMMENT '不合格原因',
  `customer_code` varchar(20) DEFAULT NULL COMMENT '客户编码',
  `customer_name` varchar(30) DEFAULT NULL COMMENT '客户名称',
  `send_check_time` datetime DEFAULT NULL COMMENT '送检时间',
  `delivery_number` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '送货单号',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `predict_complete_time` datetime DEFAULT NULL COMMENT '预计完成时间',
  `bill_no` varchar(20) DEFAULT NULL COMMENT '关联生产订单',
  `batch_no` varchar(30) DEFAULT NULL COMMENT '清洗批次号',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 0:待审核 4:已检验 5:待出库 7:待检验 8:检验中',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果;0:不合格 1:合格',
  `checker_job_number` varchar(255) DEFAULT NULL COMMENT '检验人工号',
  `checker` varchar(255) DEFAULT NULL COMMENT '检验人',
  `check_remark` varchar(500) DEFAULT NULL COMMENT '检验备注',
  `auditor` varchar(30) DEFAULT NULL COMMENT '审核人',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `audit_status` tinyint DEFAULT NULL COMMENT '审核状态 0-审核通过 1-审核不通过',
  `audit_remark` text COMMENT '审核备注',
  `special_flag` tinyint DEFAULT '0' COMMENT '是否特采;0:否  1:是',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `factory_code` varchar(6) DEFAULT '2200' COMMENT '工厂代码',
  `inbound_status` tinyint DEFAULT '0' COMMENT '入库状态 0-未入库 1-已入库',
  `distribution_status` tinyint DEFAULT '0' COMMENT '发料状态 0-未发料 1-已发料',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(6) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  KEY `idx_check_bill_no` (`check_bill_no`),
  KEY `idx_check_status` (`check_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='氧化厂IQC检验单';

-- ----------------------------
-- Table structure for oxsys_iqc_check_bill_detail
-- ----------------------------
DROP TABLE IF EXISTS `oxsys_iqc_check_bill_detail`;
CREATE TABLE `oxsys_iqc_check_bill_detail` (
  `id` bigint NOT NULL COMMENT 'ID',
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验单ID',
  `gsn` varchar(30) DEFAULT NULL COMMENT 'GSN',
  `purchase_order_number` varchar(15) DEFAULT NULL COMMENT '采购单号',
  `line_code` int DEFAULT NULL COMMENT '采购单行号',
  `material_voucher` varchar(20) DEFAULT NULL COMMENT '收料凭证',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `qty` int DEFAULT '1' COMMENT '数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `check_status` tinyint DEFAULT '0' COMMENT '是否检验  0:未检验 1:已检验',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果 0:不合格 1:合格',
  `bad_flag` tinyint DEFAULT '0' COMMENT '是否不良标签 0-否 1-是',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint NOT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='氧化厂IQC检验单明细';

-- ----------------------------
-- Table structure for oxsys_oqc_check_bill
-- ----------------------------
DROP TABLE IF EXISTS `oxsys_oqc_check_bill`;
CREATE TABLE `oxsys_oqc_check_bill` (
  `id` bigint NOT NULL,
  `sort` int DEFAULT '9999' COMMENT '排序',
  `urgency_flag` tinyint DEFAULT '0' COMMENT '是否紧急;0:正常  1:紧急',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `specification_model` varchar(150) DEFAULT NULL COMMENT '规格型号',
  `send_check_qty` int DEFAULT '0' COMMENT '送检数量',
  `sample_qty` int DEFAULT '0' COMMENT '抽样数量',
  `standard_qty` int DEFAULT '0' COMMENT '合格数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `below_standard_cause` varchar(255) DEFAULT NULL COMMENT '不合格原因',
  `customer_code` varchar(20) DEFAULT NULL COMMENT '客户编码',
  `customer_name` varchar(30) DEFAULT NULL COMMENT '客户名称',
  `send_check_time` datetime DEFAULT NULL COMMENT '送检时间',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `predict_complete_time` datetime DEFAULT NULL COMMENT '预计完成时间',
  `bill_no` varchar(20) DEFAULT NULL COMMENT '关联生产订单',
  `batch_no` varchar(30) DEFAULT NULL COMMENT '批次号',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 4:已检验 7:待检验 8:检验中',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果 0:不合格 1:合格',
  `checker_job_number` varchar(255) DEFAULT NULL COMMENT '检验人工号',
  `checker` varchar(255) DEFAULT NULL COMMENT '检验人',
  `check_remark` varchar(500) DEFAULT NULL COMMENT '检验备注',
  `warehouse_status` tinyint DEFAULT '0' COMMENT '入库状态 0:未入库 1:已入库',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `factory_code` varchar(6) DEFAULT '2200' COMMENT '工厂代码',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(6) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='氧化厂OQC列表';

-- ----------------------------
-- Table structure for oxsys_oqc_check_bill_detail
-- ----------------------------
DROP TABLE IF EXISTS `oxsys_oqc_check_bill_detail`;
CREATE TABLE `oxsys_oqc_check_bill_detail` (
  `id` bigint NOT NULL COMMENT 'ID',
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验单ID',
  `gsn` varchar(30) DEFAULT NULL COMMENT 'GSN',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `check_qty` int DEFAULT '0' COMMENT '质检数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `check_status` tinyint DEFAULT '0' COMMENT '是否检验  0:未检验 1:已检验',
  `bad_flag` tinyint DEFAULT '0' COMMENT '是否不良标签 0-否 1-是',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint NOT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='氧化厂OQC检验明细';

-- ----------------------------
-- Table structure for qms_after_sales_check_bill
-- ----------------------------
DROP TABLE IF EXISTS `qms_after_sales_check_bill`;
CREATE TABLE `qms_after_sales_check_bill` (
  `id` bigint NOT NULL,
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `send_inspect_no` varchar(50) DEFAULT '' COMMENT 'mes送检单号',
  `check_project` tinyint NOT NULL COMMENT '质检类型 8:售后质检',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `material_qty` int DEFAULT '0' COMMENT '送检数量/待检数量',
  `scan_qty` int DEFAULT '0' COMMENT '扫描数量',
  `material_type` int DEFAULT '0' COMMENT '物料类型: 0成品 1配件',
  `unit` varchar(6) DEFAULT NULL COMMENT '计量单位',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `predict_complete_time` datetime DEFAULT NULL COMMENT '预计完成时间',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 0:待审核   4:已检验    7:待检验  8:检验中',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果;0:不合格 1:合格',
  `checker` varchar(30) DEFAULT NULL COMMENT '检验人',
  `check_remark` varchar(500) DEFAULT NULL COMMENT '检验备注',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `below_standard_cause` varchar(255) DEFAULT NULL COMMENT '不合格原因',
  `push_status` tinyint DEFAULT '0' COMMENT '推送oms状态 0-未推送 1-已推送 2-部分推送',
  `auditor` varchar(30) DEFAULT NULL COMMENT '审核人',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `audit_status` tinyint DEFAULT NULL COMMENT '审核状态 0:审核通过 1:审核不通过',
  `audit_remark` varchar(255) DEFAULT NULL COMMENT '审核备注',
  `json_file` json DEFAULT NULL COMMENT '文件url',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  KEY `idx_check_bill_no` (`check_bill_no`),
  KEY `idx_check_project` (`check_project`),
  KEY `idx_check_status` (`check_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='售后检验单';

-- ----------------------------
-- Table structure for qms_after_sales_check_bill_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_after_sales_check_bill_detail`;
CREATE TABLE `qms_after_sales_check_bill_detail` (
  `id` bigint NOT NULL,
  `check_bill_id` bigint DEFAULT NULL COMMENT '质检单id',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `gsn` varchar(30) DEFAULT NULL COMMENT '序列号/69码',
  `line_code` varchar(4) DEFAULT '10' COMMENT '行号',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `material_qty` int DEFAULT '0' COMMENT '送检数量/待检数量',
  `material_type` int DEFAULT '0' COMMENT '物料类型: 0成品 1配件',
  `unit` varchar(6) DEFAULT NULL COMMENT '计量单位',
  `check_status` tinyint DEFAULT '0' COMMENT '检验状态 0:未检验 1:已检验',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果 0-不合格 1-合格',
  `checker` varchar(30) DEFAULT NULL COMMENT '检验人',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `rejects_info` json DEFAULT NULL COMMENT '不良信息',
  `solution` tinyint DEFAULT NULL COMMENT '处理方案 1-报废 2-可售 3-不可对外销售',
  `push_status` tinyint DEFAULT '0' COMMENT '推送oms状态 0-未推送 1-已推送',
  `send_inspect_status` tinyint DEFAULT '0' COMMENT '送检状态 0-未送检 1-已送检',
  `push_order_no` varchar(100) DEFAULT NULL COMMENT '调拨单号',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_check_bill_id_gsn` (`check_bill_id`,`gsn`,`line_code`),
  KEY `idx_check_bill_no` (`check_bill_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='售后检验单明细';

-- ----------------------------
-- Table structure for qms_after_sales_maintain_bill
-- ----------------------------
DROP TABLE IF EXISTS `qms_after_sales_maintain_bill`;
CREATE TABLE `qms_after_sales_maintain_bill` (
  `id` bigint NOT NULL,
  `maintain_bill_no` varchar(50) DEFAULT '' COMMENT '维修单号',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `material_code` varchar(50) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `push_order_no` varchar(50) DEFAULT NULL COMMENT '过账单号',
  `push_status` tinyint DEFAULT '0' COMMENT '推送oms状态 0-未推送 1-已推送',
  `maintain_status` tinyint DEFAULT '0' COMMENT '维修状态 0:未维修 1:已维修 8:维修中',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `updater` bigint NOT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='售后维修单';

-- ----------------------------
-- Table structure for qms_after_sales_maintain_bill_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_after_sales_maintain_bill_detail`;
CREATE TABLE `qms_after_sales_maintain_bill_detail` (
  `id` bigint NOT NULL,
  `maintain_bill_id` bigint DEFAULT NULL COMMENT '维修单id',
  `gsn` varchar(30) DEFAULT NULL COMMENT 'SN/69码',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `material_qty` int DEFAULT '0' COMMENT '送检数量/待检数量',
  `unit` varchar(6) DEFAULT NULL COMMENT '计量单位',
  `rejects_info` json DEFAULT NULL COMMENT '不良信息',
  `maintain_status` tinyint DEFAULT '0' COMMENT '维修状态 0:未维修 1:已维修 8:维修中',
  `maintain_result` tinyint DEFAULT NULL COMMENT '维修结果;0:报废 1:修好',
  `maintenance_proposal` varchar(50) DEFAULT NULL COMMENT '维修方案',
  `maintenance_worker` varchar(30) DEFAULT NULL COMMENT '维修员',
  `maintain_time` datetime DEFAULT NULL COMMENT '维修时间',
  `remark` varchar(500) DEFAULT NULL COMMENT '备注',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `updater` bigint NOT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  KEY `idx_maintain_bill_id` (`maintain_bill_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='售后维修单明细';

-- ----------------------------
-- Table structure for qms_audit_user
-- ----------------------------
DROP TABLE IF EXISTS `qms_audit_user`;
CREATE TABLE `qms_audit_user` (
  `id` bigint NOT NULL COMMENT 'id',
  `oa_uset_id` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'OA用户ID',
  `user_name` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '用户名称',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='OA审核用户';

-- ----------------------------
-- Table structure for qms_bad_handle_bill
-- ----------------------------
DROP TABLE IF EXISTS `qms_bad_handle_bill`;
CREATE TABLE `qms_bad_handle_bill` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `unusual_bill_no` varchar(30) DEFAULT NULL COMMENT '品质异常单号',
  `record_date` datetime DEFAULT NULL COMMENT '记录日期',
  `material_code` varchar(30) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(150) DEFAULT NULL COMMENT '物料名称',
  `factory_code` varchar(6) DEFAULT '2000' COMMENT '工厂编码',
  `workshop_name` varchar(30) DEFAULT NULL COMMENT '车间名称',
  `bill_no` varchar(50) DEFAULT NULL COMMENT '生产/检验单号',
  `material_qty` int DEFAULT '0' COMMENT '生产/检验数量',
  `sample_qty` int DEFAULT '0' COMMENT '抽检数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不良数量',
  `defective_rate` double DEFAULT NULL COMMENT '不良率',
  `discovery_location` varchar(50) DEFAULT NULL COMMENT '发现地',
  `problem_description` text COMMENT '问题描述',
  `recorder` varchar(30) DEFAULT NULL COMMENT '记录人',
  `recorder_dept` varchar(50) DEFAULT NULL COMMENT '记录人部门',
  `file_list` json DEFAULT NULL COMMENT '附件',
  `temporary_measures` tinyint DEFAULT NULL COMMENT '临时措施（1-停线 2-换线生产 3-继续生产）',
  `temporary_plan` text COMMENT '临时方案',
  `freeze_stock_flag` bit(1) DEFAULT b'0' COMMENT '库存成品冻结（1-是 0-否）',
  `reason_analyze` tinyint DEFAULT NULL COMMENT '原因分析（1-来料 2-制程 3-设计 4-其它）',
  `reason_description` text COMMENT '原因描述',
  `reason_analyze_authenticator` varchar(30) DEFAULT NULL COMMENT '原因分析责任人',
  `reason_analyze_confirm_date` datetime DEFAULT NULL COMMENT '原因分析确认日期',
  `bad_processing_method` json DEFAULT NULL COMMENT '不良品处理方式',
  `policy_decision` text COMMENT '决策者意见',
  `decision_maker` varchar(30) DEFAULT NULL COMMENT '决策人',
  `permanent_measures` text COMMENT '永久措施',
  `permanent_measures_authenticator` varchar(30) DEFAULT NULL COMMENT '永久措施责任人',
  `permanent_measures_confirm_date` datetime DEFAULT NULL COMMENT '永久措施确认日期',
  `precaution` text COMMENT '预防措施',
  `precaution_authenticator` varchar(30) DEFAULT NULL COMMENT '预防措施责任人',
  `precaution_confirm_date` datetime DEFAULT NULL COMMENT '预防措施确认日期',
  `verify_qty` int DEFAULT '0' COMMENT '验证数量',
  `bad_confirm` text COMMENT '不良确认',
  `quality_engineer` varchar(30) DEFAULT NULL COMMENT '品质QE',
  `quality_manager` varchar(30) DEFAULT NULL COMMENT '品质经理',
  `be_closed` bit(1) DEFAULT b'0' COMMENT '是否关闭（1-是 0-否）',
  `bill_status` tinyint DEFAULT '0' COMMENT '单据状态 0-待提交 1-待审核 2-已审核 3-审核不通过',
  `request_id` varchar(30) DEFAULT NULL COMMENT 'OA流程id',
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
) ENGINE=InnoDB AUTO_INCREMENT=1930910697745821700 DEFAULT CHARSET=utf8mb3 COMMENT='品质异常处理单';

-- ----------------------------
-- Table structure for qms_bad_material_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_bad_material_record`;
CREATE TABLE `qms_bad_material_record` (
  `id` bigint NOT NULL COMMENT 'id',
  `check_project` tinyint DEFAULT NULL COMMENT '检验工序',
  `material_code` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `title` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '异常标题',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '异常描述',
  `file_url` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '附件路径',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(30) DEFAULT NULL COMMENT '创建人姓名',
  `updater` bigint NOT NULL COMMENT '修改人',
  `update_name` varchar(30) DEFAULT NULL COMMENT '修改人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='物料不良履历';

-- ----------------------------
-- Table structure for qms_base_collover_details
-- ----------------------------
DROP TABLE IF EXISTS `qms_base_collover_details`;
CREATE TABLE `qms_base_collover_details` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `status` int DEFAULT '0' COMMENT '状态 0-未归还 1-归还',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '领用人',
  `create_time` datetime DEFAULT NULL COMMENT '领用时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '归还时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  `prototype_id` bigint DEFAULT NULL COMMENT '主表ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1834045654065676291 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='领用明细';

-- ----------------------------
-- Table structure for qms_base_material_info
-- ----------------------------
DROP TABLE IF EXISTS `qms_base_material_info`;
CREATE TABLE `qms_base_material_info` (
  `id` bigint NOT NULL,
  `matnr` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `maktx` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `maktxen` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称（英文）',
  `cntxt` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料规格',
  `entxt` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料规格（英文）',
  `nbpz` varchar(255) DEFAULT NULL COMMENT '物料完整中文名称',
  `nbpze` varchar(255) DEFAULT NULL COMMENT '物料完整英文名称',
  `mtart` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料类型 Z000-成品，Z001-主机，Z002-半成品，Z003-原料，Z005-宣传品，Z006-电子料，Z008-辅料',
  `mbrsh` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '行业领域 M:傲雷集团',
  `meins` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '基本计量单位',
  `matkl` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料组',
  `bismt` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '旧物料编码',
  `extwg` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '外部物料组',
  `spart` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '产品组',
  `mstae` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '跨工厂的物料状态',
  `mstde` varchar(12) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '有效起始期',
  `mtpos_mara` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '普通项目类别',
  `brgew` decimal(10,3) DEFAULT NULL COMMENT '毛重',
  `gewei` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '毛重单位',
  `ntgew` decimal(10,3) DEFAULT NULL COMMENT '净重',
  `volum` decimal(10,3) DEFAULT NULL COMMENT '体积',
  `voleh` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '体积单位',
  `groes` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '大小/量纲',
  `laeng` decimal(10,3) DEFAULT NULL COMMENT '长度',
  `breit` decimal(10,3) DEFAULT NULL COMMENT '宽度',
  `hoehe` decimal(10,3) DEFAULT NULL COMMENT '高度',
  `meabm` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '长宽高计量单位',
  `ean11` varchar(18) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'EAN/UPC码',
  `numtp` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'EAN类别',
  `werks` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工厂代码',
  `xchpf` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '是否批次管理',
  `ekgrp` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '采购组',
  `webaz` decimal(10,0) DEFAULT NULL COMMENT '收货处理时间',
  `beskz` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '采购类型 E:制造 F:采购 X:均可',
  `sobsl` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '特殊采购类',
  `lgpro` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '生产存储地点',
  `lgfsb` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '外购存储地点',
  `ersda` varchar(15) DEFAULT NULL COMMENT '创建日期',
  `ertim` varchar(10) DEFAULT NULL COMMENT '创建时间',
  `laeda` varchar(15) DEFAULT NULL COMMENT '修改日期',
  `latim` varchar(10) DEFAULT NULL COMMENT '修改时间',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `enabled` bit(1) DEFAULT b'1',
  `version` int DEFAULT '1',
  `del_flag` bit(1) DEFAULT b'0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_matnr` (`matnr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='物料基础数据';

-- ----------------------------
-- Table structure for qms_base_prototype_management
-- ----------------------------
DROP TABLE IF EXISTS `qms_base_prototype_management`;
CREATE TABLE `qms_base_prototype_management` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `supplier_id` varchar(50) DEFAULT NULL COMMENT '供应商id',
  `supplier_name` varchar(50) DEFAULT '' COMMENT '供应商名称',
  `products` varchar(500) DEFAULT NULL COMMENT '成品',
  `storage_place` varchar(50) DEFAULT NULL COMMENT '存放地',
  `accepted_date` datetime DEFAULT NULL COMMENT '接受日期',
  `sample_type` varchar(100) DEFAULT NULL COMMENT '样品类型(1-质量标准样机 2-研发测试样机）',
  `material_type` varchar(100) DEFAULT NULL COMMENT '物料类型(IQC-IOC OQC-OQC)',
  `versions` varchar(100) DEFAULT NULL COMMENT '版本',
  `file_url` text COMMENT '文件地址',
  `file_name` text COMMENT '文件名称',
  `file_size` double(12,4) DEFAULT NULL COMMENT '文件大小',
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
  UNIQUE KEY `idx_uk_material_code_supplier_id_versions` (`material_code`,`supplier_id`,`versions`)
) ENGINE=InnoDB AUTO_INCREMENT=1731957122047992861 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='样机管理';

-- ----------------------------
-- Table structure for qms_base_training_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_base_training_record`;
CREATE TABLE `qms_base_training_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `project_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '项目名称',
  `start_time` datetime DEFAULT NULL COMMENT '培训开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '培训结束时间',
  `duration` decimal(10,0) DEFAULT NULL COMMENT '培训时长',
  `place_for_training` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '培训地点',
  `user_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '员工名称',
  `user_no` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '员工工号',
  `department` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '部门',
  `training_status` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '毕业状态',
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
) ENGINE=InnoDB AUTO_INCREMENT=1931396314711732234 DEFAULT CHARSET=utf8mb3 COMMENT='员工培训记录';

-- ----------------------------
-- Table structure for qms_check_aql
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_aql`;
CREATE TABLE `qms_check_aql` (
  `id` bigint NOT NULL COMMENT 'id',
  `code` varchar(32) DEFAULT NULL COMMENT '字码',
  `aql` varchar(10) DEFAULT NULL COMMENT 'AQL',
  `sample_qty` int DEFAULT NULL COMMENT '抽样数量',
  `ac` int DEFAULT '0' COMMENT '允收数量(AC)',
  `re` int DEFAULT '0' COMMENT '拒收数量(Re)',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  KEY `idx_code` (`code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='抽样方案 ';

-- ----------------------------
-- Table structure for qms_check_attributes
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_attributes`;
CREATE TABLE `qms_check_attributes` (
  `id` bigint NOT NULL COMMENT 'id',
  `category_id` bigint DEFAULT NULL COMMENT '类目ID',
  `attributes` varchar(128) DEFAULT NULL COMMENT '属性',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  KEY `idx_category_id` (`category_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='检验属性';

-- ----------------------------
-- Table structure for qms_check_below_standard_cause
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_below_standard_cause`;
CREATE TABLE `qms_check_below_standard_cause` (
  `id` bigint DEFAULT NULL COMMENT 'ID',
  `below_standard_cause` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不合格原因名称',
  `check_project` tinyint DEFAULT NULL COMMENT '检验项目 0:IQC质检  1:主机质检 2:包装首件质检 3:IPQC巡检 4:FQC质检  5:入库前OQC 6:出库前OQC 7:镭雕质检 8:老化质检 9:5S巡检',
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '描述',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='不合格原因';

-- ----------------------------
-- Table structure for qms_check_category
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_category`;
CREATE TABLE `qms_check_category` (
  `id` bigint NOT NULL COMMENT 'id',
  `pid` bigint DEFAULT '0' COMMENT '上级ID',
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '名称',
  `level` int DEFAULT '1' COMMENT '级别',
  `leaf_flag` bit(1) DEFAULT b'1' COMMENT '是否叶子结点 0-否 1-是',
  `result_type` tinyint DEFAULT NULL COMMENT '检验结果类型: 0下拉框 1 文本框 2复选框',
  `create_user` varchar(32) DEFAULT NULL COMMENT '创建人',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  KEY `idx_pid` (`pid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='检验类目';

-- ----------------------------
-- Table structure for qms_check_file
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_file`;
CREATE TABLE `qms_check_file` (
  `id` bigint NOT NULL COMMENT 'ID',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `specification_model` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料规格',
  `supplier_id` varchar(10) DEFAULT NULL COMMENT '供应商编码',
  `supplier_name` varchar(100) DEFAULT NULL COMMENT '供应商名称',
  `check_project` tinyint DEFAULT NULL COMMENT '检验项目 0:IQC质检  1:主机质检 2:包装首件质检 3:IPQC巡检 4:FQC质检  5:入库前OQC 6:出库前OQC 7:镭雕质检 8:老化质检 9:5S巡检',
  `fIle_type` tinyint DEFAULT NULL COMMENT '文件类型 0:样品承认书  1:SIP文件   2:镭雕图纸',
  `file_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '文件地址',
  `file_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '文件名称',
  `file_size` double(12,4) DEFAULT NULL COMMENT '文件大小',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `exempt_check` bit(1) DEFAULT b'0' COMMENT '是否免检 0 否 1是',
  `create_name` varchar(50) DEFAULT NULL COMMENT '创建人名称',
  `creator` bigint NOT NULL COMMENT '创建人',
  `update_name` varchar(50) DEFAULT NULL COMMENT '更新人名称',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='检验文件';

-- ----------------------------
-- Table structure for qms_check_info
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_info`;
CREATE TABLE `qms_check_info` (
  `id` bigint NOT NULL COMMENT 'id',
  `ref_id` bigint DEFAULT NULL COMMENT '关联ID（质检单明细id或质检单id）',
  `check_title_id` bigint DEFAULT NULL COMMENT '检验标题ID',
  `check_type` tinyint DEFAULT NULL COMMENT '检验类型',
  `level_name1` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '级别名称',
  `level_name2` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '级别名称',
  `level_name3` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '级别名称',
  `last_category_id` bigint DEFAULT NULL COMMENT '末级分类ID',
  `attribute_value` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '属性值',
  `aql` varchar(20) DEFAULT NULL COMMENT 'AQL标准',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `type` tinyint DEFAULT NULL COMMENT '缺陷类别 0 CR 1MA 2 MI',
  `determine` tinyint(1) DEFAULT '1' COMMENT '判定 0不合格 1合格',
  `rejects_codes` json DEFAULT NULL COMMENT '不良代码',
  `description` varchar(1000) DEFAULT NULL COMMENT '异常描述 ',
  `result_type` tinyint DEFAULT NULL COMMENT '检验结果类型: 0下拉框 1 文本框 2复选框',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `qms_check_info_ref_id_check_title_id_last_category_id_uindex` (`ref_id`,`check_title_id`,`last_category_id`),
  KEY `idx_ref_id` (`ref_id`) USING BTREE,
  KEY `idx_last_category_id` (`last_category_id`) USING BTREE,
  KEY `idx_check_title_id` (`check_title_id`) USING BTREE,
  KEY `qms_check_info_ref_id_check_title_id_last_category_id_index` (`ref_id`,`check_title_id`,`last_category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='检验信息';

-- ----------------------------
-- Table structure for qms_check_level
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_level`;
CREATE TABLE `qms_check_level` (
  `id` bigint NOT NULL COMMENT 'id',
  `sampling_plan_id` bigint DEFAULT NULL COMMENT '抽样id',
  `level` tinyint DEFAULT NULL COMMENT '检验水平;1:特殊（S-1);2:特殊（S-2）3:特殊（S-3）4:特殊（S-4）5:一般（Ⅰ）6:一般（Ⅱ）7一般（Ⅲ）',
  `code` varchar(32) DEFAULT NULL COMMENT '字码',
  `sample_qty` int DEFAULT NULL COMMENT '抽样数量',
  `batch_size` tinyint DEFAULT NULL COMMENT '批量大小;0:2～8  1:9～15 2:16～25 3:26～50 4:51～90 5:91～150 6:151～280 7:281～500 8:501～1200 9:1201～3200',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='抽样方案 ';

-- ----------------------------
-- Table structure for qms_check_measure
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_measure`;
CREATE TABLE `qms_check_measure` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_code` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '物料名称',
  `measure_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '尺寸名称',
  `aql` varchar(20) DEFAULT NULL COMMENT 'AQL',
  `measure_norm` decimal(6,2) DEFAULT NULL COMMENT '尺寸标准',
  `upper_limit` decimal(6,2) DEFAULT NULL COMMENT '尺寸上限',
  `lower_limit` decimal(6,2) DEFAULT NULL COMMENT '尺寸下限',
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1931266685548113927 DEFAULT CHARSET=utf8mb3 COMMENT='检验尺寸';

-- ----------------------------
-- Table structure for qms_check_measure_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_measure_record`;
CREATE TABLE `qms_check_measure_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验单ID',
  `material_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `measure_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '尺寸名称',
  `aql` varchar(20) DEFAULT NULL COMMENT 'AQL',
  `measure_norm` decimal(6,2) DEFAULT NULL COMMENT '尺寸标准',
  `upper_limit` decimal(6,2) DEFAULT NULL COMMENT '尺寸上限',
  `lower_limit` decimal(6,2) DEFAULT NULL COMMENT '尺寸下限',
  `measure` varchar(500) DEFAULT NULL COMMENT '尺寸',
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
  `determine` tinyint(1) DEFAULT NULL COMMENT '判定 0不合格 1合格',
  `description` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '异常描述',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  PRIMARY KEY (`id`),
  KEY `material_code_IDX` (`material_code`,`check_bill_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1931288651030081539 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='检验尺寸记录';

-- ----------------------------
-- Table structure for qms_check_plan
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_plan`;
CREATE TABLE `qms_check_plan` (
  `id` bigint NOT NULL COMMENT 'id',
  `name` varchar(32) DEFAULT NULL COMMENT '质检方案名称',
  `material_code` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci COMMENT '物料编码',
  `check_project` tinyint DEFAULT NULL COMMENT '质检项目',
  `sampling_plan_id` bigint DEFAULT NULL COMMENT '抽样方案ID',
  `sampling_plan_type` tinyint DEFAULT NULL COMMENT '抽样方案类型 0:AQL抽检 1:按比例抽检 2:全检',
  `remarks` varchar(128) DEFAULT NULL COMMENT '备注',
  `create_user` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人',
  `category_ids` varchar(2000) DEFAULT NULL COMMENT '关联的分类id',
  `category_json` text COMMENT '关联的分类,json格式',
  `default_flag` bit(1) DEFAULT b'0' COMMENT '是否默认 0：否    1：是',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='质检方案';

-- ----------------------------
-- Table structure for qms_check_plan_material
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_plan_material`;
CREATE TABLE `qms_check_plan_material` (
  `id` bigint NOT NULL COMMENT 'id',
  `check_plan_id` bigint DEFAULT NULL COMMENT '质检方案ID',
  `check_project` tinyint DEFAULT NULL COMMENT '质检项目',
  `material_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `supplier_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商名称',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  KEY `idx_check_plan_id` (`check_plan_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='质检方案（物料）';

-- ----------------------------
-- Table structure for qms_check_sap_post_recode
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_sap_post_recode`;
CREATE TABLE `qms_check_sap_post_recode` (
  `id` bigint NOT NULL,
  `check_bill_id` bigint DEFAULT NULL COMMENT '质检单id',
  `check_bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '质检单编号',
  `material_voucher` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '过账凭证',
  `check_project` tinyint DEFAULT NULL COMMENT '质检类型',
  `post_type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '过账类型 122-质检不合格 553-实验报废',
  `be_write_off` tinyint DEFAULT '0' COMMENT '是否冲销 0-未冲销 1-已冲销',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用（0-未启用/1-已启用）',
  `version` int DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0：未删除 1：已删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='质检过账记录';

-- ----------------------------
-- Table structure for qms_check_statistics
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_statistics`;
CREATE TABLE `qms_check_statistics` (
  `id` bigint NOT NULL COMMENT 'id',
  `type` tinyint DEFAULT NULL COMMENT '类型:1待检统计 2 已检统计 3质检质量统计 4 不合格原因统计',
  `check_project` tinyint DEFAULT NULL COMMENT '检验项目; 1:主机  2:包装 3:巡检  4:FQC  7:镭雕 ',
  `line_code` varchar(32) DEFAULT NULL COMMENT '线别编码',
  `supplier_name` varchar(128) DEFAULT NULL COMMENT '供应商名称',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `specs_model` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '规格型号',
  `sample_qty` int DEFAULT '1' COMMENT '抽样数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `below_standard_rate` decimal(10,2) DEFAULT '0.00' COMMENT '不合格率',
  `below_standard_cause` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '不合格原因',
  `creator` bigint NOT NULL DEFAULT '0' COMMENT '创建人',
  `updater` bigint NOT NULL DEFAULT '0' COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='质检统计';

-- ----------------------------
-- Table structure for qms_check_title
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_title`;
CREATE TABLE `qms_check_title` (
  `id` bigint NOT NULL COMMENT 'id',
  `ref_id` bigint DEFAULT NULL COMMENT '外键关联ID（质检单id）',
  `check_plan_id` bigint DEFAULT NULL COMMENT '方案ID',
  `sampling_plan_id` bigint DEFAULT NULL COMMENT '抽样方案ID',
  `sampling_plan_type` tinyint DEFAULT '0' COMMENT '抽样方案类型',
  `level` tinyint DEFAULT NULL COMMENT '检验水平;1:特殊（S-1);2:特殊（S-2）3:特殊（S-3）4:特殊（S-4）5:一般（Ⅰ）6:一般（Ⅱ）7一般（Ⅲ）',
  `title1` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '标题1',
  `title2` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '标题2',
  `title3` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '标题3',
  `attributes_title` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '属性标题',
  `aql_title` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '质检方案标题',
  `sample_qty` int DEFAULT NULL COMMENT '抽样数量',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  KEY `idx_ref_id` (`ref_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='质检方案';

-- ----------------------------
-- Table structure for qms_check_tool
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_tool`;
CREATE TABLE `qms_check_tool` (
  `id` bigint DEFAULT NULL COMMENT 'ID',
  `check_project` tinyint DEFAULT NULL COMMENT '检验项目',
  `material_code` varchar(50) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  KEY `idx_material_code` (`material_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='检验工具';

-- ----------------------------
-- Table structure for qms_check_tool_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_check_tool_detail`;
CREATE TABLE `qms_check_tool_detail` (
  `id` bigint DEFAULT NULL COMMENT 'ID',
  `check_tool_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `tool_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工具名称',
  `tool_specification` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工具规格',
  `tool_location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工具存放地',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  KEY `idx_check_tool_id` (`check_tool_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='检验工具明细';

-- ----------------------------
-- Table structure for qms_consume_check_detail_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_consume_check_detail_record`;
CREATE TABLE `qms_consume_check_detail_record` (
  `id` bigint NOT NULL,
  `consume_check_id` bigint DEFAULT NULL COMMENT '老化送检单id',
  `bill_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '工单编号',
  `barcode_scope` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '条码范围',
  `bill_qty` int DEFAULT NULL COMMENT '工单数量',
  `line_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编码',
  `sn` varchar(50) DEFAULT NULL COMMENT '产品序列号',
  `material_code` varchar(50) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) DEFAULT NULL COMMENT '物料名称',
  `check_result` tinyint DEFAULT '1' COMMENT '质检结果 0-不合格 1-合格',
  `rejects_codes` json DEFAULT NULL COMMENT '不良代码',
  `remark` varchar(255) DEFAULT NULL COMMENT '不合格备注',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL COMMENT '创建时间',
  `update_time` datetime NOT NULL COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用（0-未启用/1-已启用）',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_consume_check_id_sn` (`consume_check_id`,`sn`),
  KEY `idx_sn` (`sn`),
  KEY `idx_material_code_material_name` (`material_code`,`material_name`),
  KEY `idx_bill_no` (`bill_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='老化质检记录';

-- ----------------------------
-- Table structure for qms_consume_check_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_consume_check_record`;
CREATE TABLE `qms_consume_check_record` (
  `id` bigint NOT NULL COMMENT 'ID',
  `inspect_no` varchar(30) DEFAULT NULL COMMENT '送检单号',
  `material_qty` int DEFAULT NULL COMMENT '送检数量',
  `send_inspect_time` datetime DEFAULT NULL COMMENT '送检时间',
  `check_qty` int DEFAULT NULL COMMENT '老化数量',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `operation_hours` int DEFAULT NULL COMMENT '运行时间',
  `operation_end_time` datetime DEFAULT NULL COMMENT '运行结束时间',
  `checker` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '检验人',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果;0:不合格 1:合格',
  `auditor` varchar(50) DEFAULT NULL COMMENT '审核人',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `audit_remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '审核备注',
  `consume_car_code` varchar(20) DEFAULT NULL COMMENT '老化车编码',
  `consume_car_name` varchar(20) DEFAULT NULL COMMENT '老化车名称',
  `workshop_name` varchar(50) DEFAULT NULL COMMENT '车间名称',
  `line_code` varchar(10) DEFAULT NULL COMMENT '线别编码',
  `check_status` tinyint DEFAULT NULL COMMENT '检验状态;0:待老化: 1 :充电中 2:充电完成  3:老化中 4:老化完成 5:待审核 6:审核不通过 7:已检验;',
  `special_flag` tinyint DEFAULT '0' COMMENT '是否特采;0:否  1:是',
  `standard_qty` int DEFAULT '0' COMMENT '合格数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `below_standard_cause` varchar(255) DEFAULT NULL COMMENT '不合格原因',
  `file_url` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '附件地址',
  `file_name` varchar(50) DEFAULT NULL COMMENT '附件名称',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `send_inspect_status` int DEFAULT '0' COMMENT '送检状态 0-未送检 1-已送检',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_inspect_no` (`inspect_no`),
  KEY `idx_send_inspect_status` (`send_inspect_status`),
  KEY `idx_check_result` (`check_result`),
  KEY `idx_check_status` (`check_status`),
  KEY `idx_check_end_time` (`check_end_time`),
  KEY `idx_create_time` (`create_time`),
  KEY `idx_check_start_time` (`check_start_time`),
  KEY `idx_send_inspect_status_check_start_time` (`send_inspect_status`,`check_start_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='老化质检记录';

-- ----------------------------
-- Table structure for qms_cost_center_return_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_cost_center_return_detail`;
CREATE TABLE `qms_cost_center_return_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `return_record_id` bigint DEFAULT NULL COMMENT '退料记录id',
  `material_code` varchar(20) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `material_specification` varchar(255) DEFAULT NULL COMMENT '物料规格',
  `qty` int DEFAULT '1' COMMENT '数量',
  `factory_code` varchar(10) DEFAULT NULL COMMENT '工厂代码',
  `stock_location` varchar(10) DEFAULT NULL COMMENT '库存地点',
  `warehouse_approval_personnel` varchar(30) DEFAULT NULL COMMENT '仓库审批人员',
  `need_date` varchar(30) DEFAULT NULL COMMENT '需求日期',
  `supplier` varchar(50) DEFAULT NULL COMMENT '供应商',
  `description_info` text COMMENT '描述信息',
  `shop_name` varchar(50) DEFAULT NULL COMMENT '店铺名称',
  `receiver` varchar(50) DEFAULT NULL COMMENT '收货方',
  `receive_address` varchar(255) DEFAULT NULL COMMENT '收货地址',
  `unit` varchar(10) DEFAULT NULL COMMENT '计量单位',
  `check_status` tinyint DEFAULT '0' COMMENT '检验状态 0-未检验 1-已检验',
  `qualified_qty` int DEFAULT '0' COMMENT '良品数量',
  `inner_sale_qty` int DEFAULT '0' COMMENT '可内售数量',
  `wait_repair_qty` int DEFAULT '0' COMMENT '换配件可出库数量',
  `scrapped_qty` int DEFAULT '0' COMMENT '报废数量',
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1928285286279172099 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='成本中心退料明细';

-- ----------------------------
-- Table structure for qms_cost_center_return_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_cost_center_return_record`;
CREATE TABLE `qms_cost_center_return_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `inventory_doc_no` varchar(50) DEFAULT NULL COMMENT '标准库存单据号',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `check_project` int DEFAULT NULL COMMENT '检验类型 0-IQC 5-OQC',
  `material_code` varchar(30) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(150) DEFAULT NULL COMMENT '物料名称',
  `qty` int DEFAULT '0' COMMENT '检验数量',
  `req_date` varchar(30) DEFAULT NULL COMMENT '申请日期',
  `applicant_id` varchar(30) DEFAULT NULL COMMENT '申请人id',
  `applicant` varchar(20) DEFAULT NULL COMMENT '申请人',
  `applicant_dept_id` varchar(30) DEFAULT NULL COMMENT '申请部门id',
  `applicant_dept` varchar(20) DEFAULT NULL COMMENT '申请部门',
  `bill_date` varchar(30) DEFAULT NULL COMMENT '单据日期',
  `factory_code` varchar(10) DEFAULT NULL COMMENT '工厂代码',
  `move_type` varchar(10) DEFAULT NULL COMMENT '移动类型',
  `receive_type` varchar(10) DEFAULT NULL COMMENT '领用类型',
  `department` varchar(20) DEFAULT NULL COMMENT '一级部门',
  `general_ledger_account` varchar(20) DEFAULT NULL COMMENT '总账科目',
  `order_no` varchar(30) DEFAULT NULL COMMENT '内部订单号',
  `cost_center` varchar(20) DEFAULT NULL COMMENT '成本中心',
  `strategic_project` varchar(100) DEFAULT NULL COMMENT ' 战略项目',
  `shipping_reason` text COMMENT '发料原因',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 0-待审核 4-已检验 7-待检验 8-检验中',
  `checker` varchar(20) DEFAULT NULL COMMENT '检验人',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `related_request_id` varchar(15) DEFAULT NULL COMMENT '相关流程id',
  `related_request_no` varchar(100) DEFAULT NULL COMMENT '相关流程编号',
  `oa_request_id` varchar(15) DEFAULT NULL COMMENT 'OA流程id',
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
) ENGINE=InnoDB AUTO_INCREMENT=1928285286258200579 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='成本中心退料记录';

-- ----------------------------
-- Table structure for qms_eight_report_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_eight_report_detail`;
CREATE TABLE `qms_eight_report_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `code` varchar(60) NOT NULL COMMENT '报告编码',
  `category_code` int NOT NULL DEFAULT '0' COMMENT '类别编码',
  `category_name` varchar(60) DEFAULT NULL COMMENT '类别名称',
  `user_code` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '用户编码',
  `name` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '名称',
  `supplier_id` varchar(30) DEFAULT NULL COMMENT '供应商编码',
  `source_name` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '描述信息',
  `dept_no` varchar(40) DEFAULT NULL COMMENT '部门编码',
  `description` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '介绍说明',
  `group_role` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '小组角色(0:内部整改 1:供应商整改)',
  `telephone` varchar(30) DEFAULT NULL COMMENT '电话',
  `email` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '邮箱',
  `quantity` int NOT NULL DEFAULT '0' COMMENT '数量',
  `proportion` decimal(11,2) NOT NULL DEFAULT '0.00' COMMENT '占比',
  `operate_date` datetime DEFAULT NULL COMMENT '日期',
  `notice_status` tinyint NOT NULL DEFAULT '0' COMMENT '是否推送通知(0:未推送 1:已推送)',
  `status` int DEFAULT NULL COMMENT '状态',
  `conclusion` varchar(1000) DEFAULT NULL COMMENT '结论',
  `remark` varchar(200) DEFAULT NULL COMMENT '备注',
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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1931268761527267331 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='8D报告明细信息';

-- ----------------------------
-- Table structure for qms_eight_report_info
-- ----------------------------
DROP TABLE IF EXISTS `qms_eight_report_info`;
CREATE TABLE `qms_eight_report_info` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `code` varchar(60) NOT NULL COMMENT '报告编码',
  `name` varchar(100) NOT NULL COMMENT '报告名称',
  `supplier_id` varchar(30) DEFAULT NULL COMMENT '供应商编码',
  `supplier_name` varchar(100) DEFAULT NULL COMMENT '供应商名称',
  `supplier_account` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商账号',
  `material_code` varchar(60) NOT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `status` int NOT NULL DEFAULT '0' COMMENT '报告状态',
  `report_type` tinyint NOT NULL DEFAULT '0' COMMENT '报告类型(0:内部整改 1:供应商整改)',
  `json_files` json DEFAULT NULL COMMENT '报告地址',
  `number` int NOT NULL DEFAULT '0' COMMENT '次数',
  `batch_no` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '批次编号',
  `source` varchar(10) NOT NULL COMMENT '问题来源',
  `source_order` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '来源单号',
  `occur_date` date DEFAULT NULL COMMENT '发生日期',
  `expect_date` datetime DEFAULT NULL COMMENT '期望完成日期',
  `actual_date` datetime DEFAULT NULL COMMENT '实际完成日期',
  `problem_desc` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '问题描述',
  `remark` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '创建人名称',
  `updater` bigint DEFAULT NULL COMMENT '更新人',
  `update_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '更新人名称',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `tenant_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1930460965009592324 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='8D报告主表信息';

-- ----------------------------
-- Table structure for qms_fqc_check_detail_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_fqc_check_detail_record`;
CREATE TABLE `qms_fqc_check_detail_record` (
  `id` bigint NOT NULL,
  `fqc_check_id` bigint DEFAULT NULL COMMENT 'fqc检检单id',
  `consume_check_id` bigint DEFAULT NULL COMMENT '老化质检id',
  `bill_no` varchar(30) DEFAULT NULL COMMENT '工单编号',
  `inspect_no` varchar(30) DEFAULT NULL COMMENT '送检单号',
  `line_code` varchar(20) DEFAULT NULL COMMENT '生产线别',
  `sn` varchar(50) DEFAULT NULL COMMENT '产品序列号',
  `material_code` varchar(50) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) DEFAULT NULL COMMENT '物料名称',
  `checker` varchar(20) DEFAULT NULL COMMENT '检验人',
  `check_time` datetime DEFAULT NULL COMMENT '检验时间',
  `check_result` tinyint DEFAULT NULL COMMENT '质检结果 0-不合格 1-合格',
  `generate_inspect_no` tinyint DEFAULT '0' COMMENT '是否生成质检记录 0：否 1：是',
  `rejects_codes` json DEFAULT NULL COMMENT '不良代码',
  `remark` varchar(255) DEFAULT NULL COMMENT '不合格备注',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL COMMENT '创建时间',
  `update_time` datetime NOT NULL COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用（0-未启用/1-已启用）',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `file_url` varchar(1000) DEFAULT NULL COMMENT '附件地址',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_consume_check_id_sn` (`consume_check_id`,`sn`),
  KEY `idx_sn` (`sn`),
  KEY `idx_bill_no_generate_inspect_no_check_result` (`bill_no`,`generate_inspect_no`,`check_result`),
  KEY `idx_fqc_check_id` (`fqc_check_id`),
  KEY `idx_inspect_no` (`inspect_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='FQC质检明细记录';

-- ----------------------------
-- Table structure for qms_fqc_check_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_fqc_check_record`;
CREATE TABLE `qms_fqc_check_record` (
  `id` bigint NOT NULL COMMENT 'ID',
  `inspect_no` varchar(30) DEFAULT NULL COMMENT '送检单号',
  `bill_no` varchar(50) DEFAULT NULL COMMENT '单据编号',
  `material_code` varchar(50) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) DEFAULT NULL COMMENT '物料名称',
  `barcode_scope` varchar(100) DEFAULT NULL COMMENT '条码范围',
  `material_qty` int DEFAULT NULL COMMENT '送检数量',
  `send_inspect_time` datetime DEFAULT NULL COMMENT '送检时间',
  `bill_qty` int DEFAULT NULL COMMENT '工单数量',
  `workshop_name` varchar(30) DEFAULT NULL COMMENT '车间名称',
  `line_code` varchar(255) DEFAULT NULL COMMENT '线别编码',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `checker` varchar(20) DEFAULT NULL COMMENT '检验人',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果;0:不合格 1:合格',
  `auditor` varchar(20) DEFAULT NULL COMMENT '审核人',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `audit_remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '审核备注',
  `check_status` tinyint DEFAULT NULL COMMENT '检验状态;0:待检验: 1:检验中 2:待审核 3:审核不合格 4:已检验',
  `special_flag` tinyint DEFAULT NULL COMMENT '是否特采;0:否  1:是',
  `standard_qty` int DEFAULT NULL COMMENT '合格数量',
  `below_standard_qty` int DEFAULT NULL COMMENT '不合格数量',
  `below_standard_cause` varchar(255) DEFAULT NULL COMMENT '不合格原因',
  `file_url` varchar(3000) DEFAULT NULL COMMENT '附件地址',
  `file_name` varchar(500) DEFAULT NULL COMMENT '附件名称',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  KEY `idx_inspectno_delflag` (`inspect_no`,`del_flag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='FQC质检记录';

-- ----------------------------
-- Table structure for qms_fqc_wait_check_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_fqc_wait_check_record`;
CREATE TABLE `qms_fqc_wait_check_record` (
  `id` bigint NOT NULL COMMENT 'ID',
  `consume_check_id` bigint DEFAULT NULL COMMENT '老化质检id',
  `inspect_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '送检单号',
  `bill_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '单据编号',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `material_qty` int DEFAULT NULL COMMENT '送检数量',
  `send_inspect_time` datetime DEFAULT NULL COMMENT '送检时间',
  `bill_qty` int DEFAULT NULL COMMENT '工单数量',
  `line_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '线别编码',
  `check_status` tinyint DEFAULT NULL COMMENT '检验状态;0:待检验: 1:检验中 2:待审核 3:审核不合格 4:已检验',
  `remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `workshop_name` varchar(30) DEFAULT NULL COMMENT '车间名称',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `idx_uk_consume_check_id_bill_no` (`consume_check_id`,`bill_no`),
  KEY `idx_bill_no` (`bill_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='FQC待检验记录';

-- ----------------------------
-- Table structure for qms_material_size_measure_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_material_size_measure_detail`;
CREATE TABLE `qms_material_size_measure_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `measure_record_id` bigint DEFAULT NULL COMMENT '测量记录id',
  `product_id` bigint DEFAULT NULL COMMENT '测量序号',
  `measure_time` datetime DEFAULT NULL COMMENT '测量时间',
  `measure_result` varchar(10) DEFAULT NULL COMMENT '测试结果 OK/NG',
  `measure_detail_json` json DEFAULT NULL COMMENT '测量结果明细',
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_measure_record_id_product_id` (`measure_record_id`,`product_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1930826781114511364 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='尺寸测量明细';

-- ----------------------------
-- Table structure for qms_material_size_measure_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_material_size_measure_record`;
CREATE TABLE `qms_material_size_measure_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `barcode` varchar(50) DEFAULT NULL COMMENT '条码',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `material_code` varchar(30) DEFAULT NULL COMMENT '物料编码',
  `process_name` varchar(30) DEFAULT NULL COMMENT '工序名',
  `machine_name` varchar(30) DEFAULT NULL COMMENT '机器名称',
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_barcode` (`barcode`)
) ENGINE=InnoDB AUTO_INCREMENT=1930809219152621572 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='尺寸测量记录';

-- ----------------------------
-- Table structure for qms_product_check_bill
-- ----------------------------
DROP TABLE IF EXISTS `qms_product_check_bill`;
CREATE TABLE `qms_product_check_bill` (
  `id` bigint NOT NULL COMMENT 'ID',
  `push_bill_id` bigint DEFAULT NULL COMMENT '推送数据ID',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `check_project` tinyint DEFAULT NULL COMMENT '检验项目; 1:主机  2:包装 3:巡检  4:FQC  7:镭雕 ',
  `bill_no` varchar(30) DEFAULT NULL COMMENT '单据编号',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `specification_model` varchar(255) DEFAULT NULL COMMENT '规格型号',
  `material_qty` int DEFAULT NULL COMMENT '送检数量',
  `barcode_scope` varchar(100) DEFAULT NULL COMMENT '条码范围',
  `sn` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '序列号',
  `bill_qty` int DEFAULT NULL COMMENT '工单数量',
  `workshop_id` bigint DEFAULT NULL COMMENT '车间id',
  `line_code` varchar(10) DEFAULT NULL COMMENT '线别编码',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `checker` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '检验人',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果;0:不合格 1:合格',
  `check_type` tinyint DEFAULT NULL COMMENT '检验方案;0:全检查 1:抽检',
  `auditer` varchar(50) DEFAULT NULL COMMENT '审核人',
  `audit_status` tinyint DEFAULT NULL COMMENT '审核状态 0:审核通过 1:审核不通过',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `audit_remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '审核备注',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 0:待审核   4:已检验    7:待检验  8:检验中',
  `initial_flag` tinyint DEFAULT NULL COMMENT '是否特采;0:否  1:是',
  `below_standard_qty` int DEFAULT NULL COMMENT '不合格数量',
  `below_standard_cause` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不合格原因',
  `laser_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '雕刻内容  用于镭雕质检',
  `laser_user` bigint DEFAULT NULL COMMENT '镭雕人     用于镭雕质检',
  `rejects_type_name` varchar(30) DEFAULT NULL COMMENT '不良代码类型',
  `rejects_describe` varchar(100) DEFAULT NULL COMMENT '不良代码描述',
  `rejects_codes` json DEFAULT NULL COMMENT '不良代码',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `file_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '附件名称',
  `file_url` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '附件地址',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `workshop_name` varchar(20) DEFAULT NULL COMMENT '车间名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品检验记录';

-- ----------------------------
-- Table structure for qms_product_check_bill_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_product_check_bill_detail`;
CREATE TABLE `qms_product_check_bill_detail` (
  `id` bigint NOT NULL COMMENT 'ID',
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验单ID',
  `check_project` tinyint DEFAULT NULL COMMENT '检验项目; 1:主机  2:包装 3:巡检  4:FQC  5:入库前OQC  6:出库前OQC  7:镭雕',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `sn` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'SN',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_sn` (`sn`,`check_project`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品检验单明细';

-- ----------------------------
-- Table structure for qms_product_defect_library
-- ----------------------------
DROP TABLE IF EXISTS `qms_product_defect_library`;
CREATE TABLE `qms_product_defect_library` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `business_dept` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '事业部',
  `product_model` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '产品型号',
  `question_category` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '问题类别',
  `question_type` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '问题种类',
  `defect_desc` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '缺陷描述',
  `exceptional_pictures` json DEFAULT NULL COMMENT '异常图片',
  `cause_type` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '根本原因分类',
  `cause_analysis` text CHARACTER SET utf8 COLLATE utf8_general_ci COMMENT '原因分析',
  `analysis_evidence` json DEFAULT NULL COMMENT '分析佐证',
  `improvement_measures` text CHARACTER SET utf8 COLLATE utf8_general_ci COMMENT '改进措施',
  `question_status` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '问题状态',
  `files` json DEFAULT NULL COMMENT '附件',
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
) ENGINE=InnoDB AUTO_INCREMENT=1914961105769873412 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品缺陷案例库';

-- ----------------------------
-- Table structure for qms_product_freeze_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_product_freeze_detail`;
CREATE TABLE `qms_product_freeze_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `freeze_record_id` bigint DEFAULT NULL COMMENT '冻结记录id',
  `warehouse_code` varchar(10) DEFAULT NULL COMMENT '库存编码',
  `warehouse_name` varchar(100) DEFAULT NULL COMMENT '仓库名称',
  `inventory_order_no` varchar(30) DEFAULT NULL COMMENT '库存单据号',
  `unfreeze_operator` varchar(30) DEFAULT NULL COMMENT '解除冻结操作人',
  `unfreeze_time` datetime DEFAULT NULL COMMENT '解除冻结时间',
  `freeze_status` tinyint DEFAULT '1' COMMENT '冻结状态 0-已解冻 1-已冻结',
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
) ENGINE=InnoDB AUTO_INCREMENT=1905808296531193869 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品冻结明细';

-- ----------------------------
-- Table structure for qms_product_freeze_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_product_freeze_record`;
CREATE TABLE `qms_product_freeze_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_code` varchar(20) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `freeze_operator` varchar(20) DEFAULT NULL COMMENT '冻结操作人',
  `freeze_time` datetime DEFAULT NULL COMMENT '冻结时间',
  `unfreeze_operator` varchar(20) DEFAULT NULL COMMENT '解除冻结操作人',
  `unfreeze_time` datetime DEFAULT NULL COMMENT '解除冻结时间',
  `freeze_status` tinyint DEFAULT '1' COMMENT '冻结状态 0-已解冻 1-已冻结 2-部分解冻',
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
) ENGINE=InnoDB AUTO_INCREMENT=1905808295142879234 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='产品冻结记录';

-- ----------------------------
-- Table structure for qms_push_failed_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_push_failed_record`;
CREATE TABLE `qms_push_failed_record` (
  `id` bigint NOT NULL,
  `check_project` tinyint DEFAULT NULL COMMENT '检验项目 0:IQC  5:入库前OQC  6:出库前OQC',
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验ID',
  `check_bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '检验单号',
  `material_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `material_qty` int NOT NULL DEFAULT '0' COMMENT '送检数量',
  `sample_qty` int DEFAULT NULL COMMENT '抽样数量',
  `below_standard_qty` int DEFAULT NULL COMMENT '不合格数量',
  `api_code` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'API 类型',
  `status` int DEFAULT '0' COMMENT '状态 : 0失败 1 成功',
  `reason` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '失败原因',
  `request_params` json DEFAULT NULL COMMENT '接口请求报文',
  `response_params` json DEFAULT NULL COMMENT '接口返回报文',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`,`material_qty`) USING BTREE,
  KEY `idx_check_bill_no` (`check_bill_no`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='下推失败记录';

-- ----------------------------
-- Table structure for qms_push_inner_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_push_inner_record`;
CREATE TABLE `qms_push_inner_record` (
  `id` bigint NOT NULL,
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验单ID',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `target_system` varchar(100) DEFAULT NULL COMMENT '目标系统',
  `status` tinyint DEFAULT '0' COMMENT '状态 : 0失败 1 成功',
  `request_params` json DEFAULT NULL COMMENT '接口请求报文',
  `response_params` json DEFAULT NULL COMMENT '接口返回报文',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='内部接口推送记录';

-- ----------------------------
-- Table structure for qms_qc_check_bill
-- ----------------------------
DROP TABLE IF EXISTS `qms_qc_check_bill`;
CREATE TABLE `qms_qc_check_bill` (
  `id` bigint NOT NULL,
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `inventory_doc_no` varchar(50) DEFAULT NULL COMMENT '标准库存单据号',
  `parent_check_bill_no` varchar(30) DEFAULT NULL COMMENT '父类检验单号',
  `check_project` tinyint DEFAULT NULL COMMENT '检验项目 0:IQC  5:入库前OQC  6:出库前OQC',
  `iqc_check_type` tinyint DEFAULT '1' COMMENT '1:正常检验 2:前置检验',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `specification_model` varchar(150) DEFAULT NULL COMMENT '规格型号',
  `unit` varchar(6) DEFAULT NULL COMMENT '计量单位',
  `material_qty` int DEFAULT '0' COMMENT '送检数量/待检数量',
  `material_source` varchar(2) DEFAULT 'CG' COMMENT '物料来源 生产:SC 采购:CG',
  `material_type` int DEFAULT '0' COMMENT '物料类型: 0成品 1配件',
  `material_status` int DEFAULT NULL COMMENT '物料状态 0-研发确认中 1-测试实验中',
  `scan_qty` int DEFAULT '0' COMMENT '已扫描数量',
  `sample_qty` int DEFAULT NULL COMMENT '抽样数量',
  `send_check_qty` int DEFAULT '0' COMMENT 'mes送检数量',
  `bill_no` varchar(50) DEFAULT NULL COMMENT '单号',
  `in_stock_time` datetime DEFAULT NULL COMMENT '入库时间',
  `workshop_name` varchar(50) DEFAULT NULL COMMENT '车间名称',
  `line_code` varchar(20) DEFAULT NULL COMMENT '线别编码',
  `delivery_no` varchar(50) DEFAULT NULL COMMENT '送货单号',
  `purchase_no` varchar(255) DEFAULT NULL COMMENT '采购单号',
  `purchase_type` varchar(6) DEFAULT NULL COMMENT '采购订单类型',
  `receiving_no` varchar(50) DEFAULT NULL COMMENT '收料单号',
  `vehicle_no` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '载具码',
  `sap_no` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'SAP 单号',
  `receiving_time` datetime DEFAULT NULL COMMENT '收料时间',
  `supplier_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商id',
  `supplier_name` varchar(50) DEFAULT '' COMMENT '供应商名称',
  `owner_id` varchar(50) DEFAULT NULL COMMENT '货主id',
  `owner_name` varchar(50) DEFAULT NULL COMMENT '货主名称',
  `shop` varchar(50) DEFAULT NULL COMMENT '店铺',
  `shop_name` varchar(200) DEFAULT NULL COMMENT '店铺名称',
  `flux_warehouse_code` varchar(10) DEFAULT NULL COMMENT '富勒仓库编码',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `first_check_end_time` datetime DEFAULT NULL COMMENT '首次检验结束时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 0:待审核 4:已检验 5:待出库 7:待检验 8:检验中',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果;0:不合格 1:合格',
  `checker` varchar(255) DEFAULT NULL COMMENT '检验人',
  `checker_job_number` varchar(255) DEFAULT NULL COMMENT '检验人工号',
  `check_remark` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '检验备注',
  `need_complete_date` datetime DEFAULT NULL COMMENT '需求完成时间',
  `predict_complete_date` datetime DEFAULT NULL COMMENT '预计完成时间',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `below_standard_cause` varchar(255) DEFAULT NULL COMMENT '不合格原因',
  `bad_property` varchar(100) DEFAULT NULL COMMENT '不良属性',
  `experiment_qty` int DEFAULT '0' COMMENT '实验数量',
  `cost_center` varchar(30) DEFAULT NULL COMMENT '成本中心',
  `prototype_qty` int DEFAULT '0' COMMENT '样机数量',
  `auditor` varchar(30) DEFAULT NULL COMMENT '审核人',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `audit_status` tinyint DEFAULT NULL COMMENT '审核状态 0:审核通过 1:审核不通过',
  `audit_remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '审核备注',
  `special_flag` tinyint DEFAULT '0' COMMENT '是否特采;0:否  1:是 2:7折特采',
  `file_url` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '附件地址',
  `file_name` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '附件名称',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `size_measure_file` json DEFAULT NULL COMMENT '尺寸检验文件',
  `bill_type` tinyint DEFAULT '0' COMMENT '单据类型  0:检验单 1:库存请检单',
  `urgency_flag` tinyint DEFAULT '0' COMMENT '是否紧急;0:正常  1:紧急',
  `sort` int DEFAULT '9999' COMMENT '排序',
  `applicant` varchar(255) DEFAULT NULL COMMENT '申请人',
  `apply_time` datetime DEFAULT NULL COMMENT '申请请检时间',
  `push_status` tinyint DEFAULT '0' COMMENT '推送金蝶状态 0:未推送 1:已推送 3:推送失败',
  `receive_detail_id` varchar(50) DEFAULT NULL COMMENT '金蝶收料单ID 下推金蝶使用',
  `asn_no` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'WMS入库单号',
  `factory_code` varchar(6) DEFAULT '2000' COMMENT '工厂代码',
  `stock_location` varchar(6) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '库存地点',
  `order_line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'WM订单行号',
  `material_voucher` varchar(20) DEFAULT NULL COMMENT '物料凭证',
  `oa_user_id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'OA 用户ID',
  `inv_age` int DEFAULT NULL COMMENT '库龄',
  `warehouse_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '仓库: WH01-东莞仓  WH02-美国仓',
  `recheck_reason` varchar(255) DEFAULT NULL COMMENT '重检原因',
  `un_frozen_flag` bit(1) DEFAULT NULL COMMENT '是否解冻 0-否 1-是',
  `organize_no` varchar(10) DEFAULT NULL COMMENT '采购组织',
  `purchase_group` varchar(20) DEFAULT NULL COMMENT '采购组',
  `need_experiment` tinyint DEFAULT '0' COMMENT '是否需要送测 0-不需要 1-需要',
  `batch_count` int DEFAULT '0' COMMENT '批次数量',
  `cumulative_quantity` int DEFAULT '0' COMMENT '累计送检数量',
  `experiment_result` tinyint DEFAULT NULL COMMENT '实验结果 0-不合格 1-合格',
  `sample_delivery_location` tinyint DEFAULT NULL COMMENT '样品收货地点 0-深圳 1-中山',
  `sample_sent_status` tinyint DEFAULT '0' COMMENT '样品寄出状态 0-未寄出 1-已寄出',
  `decision_result` tinyint DEFAULT NULL COMMENT '研发判定结果 0-不通过 1-通过',
  `trial_process_id` varchar(15) DEFAULT NULL COMMENT '试产流程id',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `send_inspect_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT 'mes送检单号',
  PRIMARY KEY (`id`),
  KEY `idx_check_bill_no` (`check_bill_no`) USING BTREE,
  KEY `idx_check_project` (`check_project`) USING BTREE,
  KEY `idx_check_status` (`check_status`) USING BTREE,
  KEY `idx_materialcode` (`material_code`),
  KEY `idx_qms_qc_check_bill_check_end_time` (`check_end_time`),
  KEY `idx_qms_qc_check_bill_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='IQC-OQC检验单';

-- ----------------------------
-- Table structure for qms_qc_check_bill_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_qc_check_bill_detail`;
CREATE TABLE `qms_qc_check_bill_detail` (
  `id` bigint NOT NULL COMMENT 'ID',
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验单ID',
  `material_code` varchar(32) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `gsn` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'GSN或SN',
  `qty` int DEFAULT '1' COMMENT '数量',
  `bill_type` tinyint DEFAULT '0' COMMENT '单据类型 0:检验单 1:库存请检单',
  `check_status` tinyint DEFAULT '0' COMMENT '是否检验  0:未检验 1:已检验',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果 0:不合格 1:合格',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `experiment_qty` int DEFAULT '0' COMMENT '实验数量',
  `bill_no` varchar(255) DEFAULT NULL COMMENT '订单号',
  `line_code` varchar(20) DEFAULT NULL COMMENT '线别编码',
  `order_line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '1' COMMENT '金蝶订单行号',
  `material_voucher` varchar(20) DEFAULT NULL COMMENT '物料凭证',
  `white_package_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '白盒号',
  `big_package_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '大箱号',
  `material_package_no` varchar(30) DEFAULT NULL COMMENT '料箱编号',
  `rejects_codes` json DEFAULT NULL COMMENT '不良代码',
  `shop_name` varchar(100) DEFAULT NULL COMMENT '入库店铺',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_check_bill_id_gsn` (`check_bill_id`,`gsn`),
  KEY `idx_gsn_below_standard_qty_experiment_qty` (`gsn`,`below_standard_qty`,`experiment_qty`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='IQC-OQC检验单明细';

-- ----------------------------
-- Table structure for qms_qc_check_bill_detail_relation
-- ----------------------------
DROP TABLE IF EXISTS `qms_qc_check_bill_detail_relation`;
CREATE TABLE `qms_qc_check_bill_detail_relation` (
  `id` bigint NOT NULL,
  `check_bill_id` bigint DEFAULT NULL COMMENT '质检单id',
  `new_gsn` varchar(50) DEFAULT NULL COMMENT '新条码',
  `gsn` varchar(50) DEFAULT NULL COMMENT '原条码',
  `material_code` varchar(50) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(200) DEFAULT NULL COMMENT '物料名称',
  `inspect_qty` int DEFAULT NULL COMMENT '质检数量',
  `standard_qty` int DEFAULT NULL COMMENT '合格数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `experiment_qty` int DEFAULT '0' COMMENT '实验数量',
  `purchase_no` varchar(255) DEFAULT NULL COMMENT '采购单号',
  `order_line_code` varchar(5) DEFAULT NULL COMMENT '采购单行号',
  `material_voucher` varchar(20) DEFAULT NULL COMMENT '收料凭证',
  `voucher_year` varchar(5) DEFAULT NULL COMMENT '凭证年度',
  `factory_code` varchar(6) DEFAULT NULL COMMENT '工厂代码',
  `stock_location` varchar(6) DEFAULT NULL COMMENT '库存地点',
  `purchase_type` varchar(6) DEFAULT NULL COMMENT '采购单类型',
  `supplier_id` varchar(50) DEFAULT NULL COMMENT '供应商id',
  `supplier_name` varchar(50) DEFAULT NULL COMMENT '供应商名称',
  `delivery_no` varchar(50) DEFAULT NULL COMMENT '送货单号',
  `receiving_no` varchar(50) DEFAULT NULL COMMENT '收料单号',
  `unit` varchar(6) DEFAULT NULL COMMENT '计量单位',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  KEY `idx_check_bill_id_new_gsn` (`check_bill_id`,`new_gsn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='质检单明细关联';

-- ----------------------------
-- Table structure for qms_quality_audit_records
-- ----------------------------
DROP TABLE IF EXISTS `qms_quality_audit_records`;
CREATE TABLE `qms_quality_audit_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `serial` int NOT NULL DEFAULT '1' COMMENT '序号',
  `reviewer` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '审核人',
  `audit_results` int DEFAULT NULL COMMENT '审核结果',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
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
  `job_number` varchar(30) DEFAULT NULL COMMENT '工号',
  `main_table_id` bigint DEFAULT NULL COMMENT '主表ID',
  `audit_idea` varchar(100) DEFAULT NULL COMMENT '审核意见',
  `dept_name` varchar(100) DEFAULT NULL COMMENT '部门',
  `position` varchar(100) DEFAULT NULL COMMENT '职位',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1930164773826564098 DEFAULT CHARSET=utf8mb3 COMMENT='审核记录';

-- ----------------------------
-- Table structure for qms_quality_countersignature_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_quality_countersignature_record`;
CREATE TABLE `qms_quality_countersignature_record` (
  `id` bigint NOT NULL,
  `serial` int NOT NULL DEFAULT '1' COMMENT '序号',
  `title` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '标题',
  `counter_signer` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '会签人',
  `countersigning_results` int DEFAULT NULL COMMENT '会签结果',
  `countersignature_opinions` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '会签意见',
  `signing_time` datetime DEFAULT NULL COMMENT '会签时间',
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
  `job_number` varchar(30) DEFAULT NULL COMMENT '工号',
  `main_table_id` bigint DEFAULT NULL COMMENT '主表ID',
  `dept_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '部门',
  `position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '职位',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='会签记录明细';

-- ----------------------------
-- Table structure for qms_quality_revision_history
-- ----------------------------
DROP TABLE IF EXISTS `qms_quality_revision_history`;
CREATE TABLE `qms_quality_revision_history` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `serial` int NOT NULL DEFAULT '1' COMMENT '序号',
  `revision_history` varchar(255) DEFAULT NULL COMMENT '文件修订记录',
  `version_number` varchar(60) DEFAULT NULL COMMENT '版本号',
  `producer_no` varchar(10) DEFAULT NULL COMMENT '编制人工号',
  `producer` varchar(20) DEFAULT NULL COMMENT '编制人',
  `production_date` date DEFAULT NULL COMMENT '编制日期',
  `remark` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '编制人',
  `create_name` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT NULL COMMENT '编制日期',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int DEFAULT '1' COMMENT '版本号',
  `tenant_code` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT '1001' COMMENT '租户编码',
  `job_number` bigint DEFAULT NULL COMMENT '工号',
  `main_table_id` bigint DEFAULT NULL COMMENT '主表ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1930165208201269250 DEFAULT CHARSET=utf8mb3 COMMENT='文件修订记录';

-- ----------------------------
-- Table structure for qms_quality_system_documents
-- ----------------------------
DROP TABLE IF EXISTS `qms_quality_system_documents`;
CREATE TABLE `qms_quality_system_documents` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `serial` int NOT NULL DEFAULT '1' COMMENT '序号',
  `document_number` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '文件编号',
  `file_name` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '文件名',
  `file_type` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '文件类型 1:一阶文件 2:二阶管理 3:三阶文件 4:四阶文件',
  `version_number` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '版本号',
  `revision_history` varchar(255) DEFAULT NULL COMMENT '修改内容',
  `personnel` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '会签人',
  `reviewer` varchar(1000) DEFAULT NULL COMMENT '审核人',
  `file_attachments` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '文件附件',
  `merge_file` varchar(1000) DEFAULT NULL COMMENT '合并后附件',
  `state` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '状态 1:待提交 2:会签中 3:审核中 4:审核完成 5:已取消 6:会签失败 7:审核失败',
  `creator_department` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '创建人部门',
  `producer_no` varchar(10) DEFAULT NULL COMMENT '编制人工号',
  `producer` varchar(20) DEFAULT NULL COMMENT '编制人',
  `production_date` date DEFAULT NULL COMMENT '编制日期',
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
  `job_number` varchar(50) DEFAULT NULL COMMENT '工号',
  `oa_request_id` varchar(100) DEFAULT NULL COMMENT 'oa流程id',
  `yes_no` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1931192504169017347 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='质量体系文件';

-- ----------------------------
-- Table structure for qms_recheck_wait_return_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_recheck_wait_return_record`;
CREATE TABLE `qms_recheck_wait_return_record` (
  `id` bigint NOT NULL,
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `check_project` int DEFAULT NULL COMMENT '检验项目 0-IQC 5-OQC',
  `bill_type` varchar(10) DEFAULT NULL COMMENT '订单类型',
  `supplier_no` varchar(10) DEFAULT NULL COMMENT '供应商编码',
  `supplier_name` varchar(100) DEFAULT NULL COMMENT '供应商名称',
  `purchase_organize` varchar(10) DEFAULT NULL COMMENT '采购组织代码',
  `factory_code` varchar(10) DEFAULT '2000' COMMENT '工厂代码',
  `stock_location` varchar(5) DEFAULT NULL COMMENT '退货库存地点',
  `special_stock_flag` varchar(5) DEFAULT NULL COMMENT '特殊库存标识',
  `purchase_group` varchar(5) DEFAULT NULL COMMENT '采购组',
  `material_code` varchar(20) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `material_source` varchar(4) DEFAULT NULL COMMENT '物料来源 SC:生产 CG:采购',
  `qty` int DEFAULT '1' COMMENT '数量',
  `push_status` int DEFAULT '0' COMMENT '推送状态 0：待推送 1：推送成功 5：推送失败',
  `request_param` text COMMENT '请求参数',
  `remark` varchar(255) DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_name` varchar(60) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_name` varchar(60) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识 0-未删除 1-已删除',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用 0-未启用 1-已启用',
  `version` int DEFAULT '1' COMMENT '版本',
  `tenant_code` varchar(30) DEFAULT '1001' COMMENT '租户编码',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_check_bill_no_material_code` (`check_bill_no`,`material_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='重检待退货记录';

-- ----------------------------
-- Table structure for qms_reliability_check_bill
-- ----------------------------
DROP TABLE IF EXISTS `qms_reliability_check_bill`;
CREATE TABLE `qms_reliability_check_bill` (
  `id` bigint NOT NULL COMMENT 'id',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '检验单号',
  `gsn` varchar(30) DEFAULT NULL COMMENT '关联条码',
  `material_code` varchar(20) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `supplier_id` varchar(20) DEFAULT NULL COMMENT '供应商编码',
  `supplier_name` varchar(100) DEFAULT NULL COMMENT '供应商名称',
  `predict_complete_time` datetime DEFAULT NULL COMMENT '预计完成日期',
  `send_inspect_qty` int DEFAULT '0' COMMENT '送检数量',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 0-待审核 4-已检验 7待检验 8-检验中',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果 0-不合格 1-合格',
  `check_remark` varchar(255) DEFAULT NULL COMMENT '检验备注',
  `checker` varchar(50) DEFAULT NULL COMMENT '检验人',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始日期',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `json_files` json DEFAULT NULL COMMENT '附件',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `updater` bigint NOT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_check_bill_no` (`check_bill_no`),
  UNIQUE KEY `idx_uk_gsn` (`gsn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='可靠性测试检验单';

-- ----------------------------
-- Table structure for qms_return_check_detail_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_return_check_detail_record`;
CREATE TABLE `qms_return_check_detail_record` (
  `id` bigint NOT NULL COMMENT 'ID',
  `check_bill_id` bigint DEFAULT NULL COMMENT '检验单ID',
  `material_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `material_type` tinyint DEFAULT NULL COMMENT '物料类型 0:成品 1:配件',
  `sn` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'GSN或SN',
  `qty` int DEFAULT '1' COMMENT '数量',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果 0:不合格 1:合格',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE KEY `uq_gsn` (`sn`,`check_bill_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='退货检验单明细';

-- ----------------------------
-- Table structure for qms_return_check_record
-- ----------------------------
DROP TABLE IF EXISTS `qms_return_check_record`;
CREATE TABLE `qms_return_check_record` (
  `id` bigint NOT NULL,
  `check_bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '检验单号',
  `qc_type` varchar(20) DEFAULT NULL COMMENT '单据类型',
  `material_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `specification_model` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '规格型号',
  `material_qty` int DEFAULT '0' COMMENT '送检数量',
  `unit` varchar(8) DEFAULT NULL COMMENT '计量单位',
  `shop` varchar(50) DEFAULT NULL COMMENT '店铺',
  `shop_name` varchar(200) DEFAULT NULL COMMENT '店铺名称',
  `flux_warehouse_code` varchar(10) DEFAULT NULL COMMENT '富勒仓库编码',
  `scan_qty` int DEFAULT '0' COMMENT '已扫描数量',
  `sample_qty` int DEFAULT NULL COMMENT '抽样数量',
  `factory` varchar(8) DEFAULT NULL COMMENT '工厂代码',
  `location` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '地点',
  `send_inspect_time` datetime DEFAULT NULL COMMENT '送检时间',
  `send_inspect_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '' COMMENT '送检单号',
  `check_start_time` datetime DEFAULT NULL COMMENT '检验开始时间',
  `check_end_time` datetime DEFAULT NULL COMMENT '检验结束时间',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 0:待审核   4:已检验    7:待检验  8:检验中',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果;0:不合格 1:合格 2:部分合格',
  `checker` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '检验人',
  `check_remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '检验备注',
  `predict_complete_date` datetime DEFAULT NULL COMMENT '预计完成时间',
  `below_standard_qty` int DEFAULT NULL COMMENT '不合格数量',
  `below_standard_cause` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不合格原因',
  `auditer` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '审核人',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `audit_status` tinyint DEFAULT NULL COMMENT '审核状态 0:审核通过 1:审核不通过',
  `audit_remark` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '审核备注',
  `file_url` varchar(1024) DEFAULT NULL COMMENT '附件地址',
  `file_name` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '附件名称',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `order_line_code` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'WM订单行号',
  `return_type` int NOT NULL DEFAULT '0' COMMENT '退货类型 : 0 退货 1采购',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='退货检验单';

-- ----------------------------
-- Table structure for qms_return_order
-- ----------------------------
DROP TABLE IF EXISTS `qms_return_order`;
CREATE TABLE `qms_return_order` (
  `id` bigint NOT NULL,
  `check_project` tinyint DEFAULT NULL COMMENT '检验项目 0:IQC  5:入库前OQC  6:出库前OQC',
  `return_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '退货单号',
  `material_voucher` varchar(100) DEFAULT NULL COMMENT '退货凭证',
  `purchase_no` varchar(255) DEFAULT NULL COMMENT '采购单号',
  `delivery_no` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '送货单号',
  `check_bill_no` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '检验单号',
  `supplier_id` varchar(15) DEFAULT NULL COMMENT '供应商编码',
  `supplier_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '供应商名称',
  `return_time` datetime DEFAULT NULL COMMENT '退货时间',
  `operator` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '操作人',
  `material_code` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `be_print` tinyint DEFAULT '0' COMMENT '是否打印 0-否 1-是',
  `print_qty` int DEFAULT '0' COMMENT '打印次数',
  `return_qty` int DEFAULT NULL COMMENT '退货数量',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci ROW_FORMAT=DYNAMIC COMMENT='退货单';

-- ----------------------------
-- Table structure for qms_sample_check_bill
-- ----------------------------
DROP TABLE IF EXISTS `qms_sample_check_bill`;
CREATE TABLE `qms_sample_check_bill` (
  `id` bigint NOT NULL COMMENT 'id',
  `check_bill_no` varchar(30) DEFAULT NULL COMMENT '样品检验单号',
  `sample_apply_no` varchar(30) DEFAULT NULL COMMENT '样品申请单号',
  `sample_admit_type` tinyint DEFAULT '1' COMMENT '样品承认类别 0-新开发物料 1-ECN变更 2-变更供应商 3-颜色革命 4-外购品',
  `priority` tinyint DEFAULT '1' COMMENT '优先级 0-正常 1-加急 2-紧急',
  `material_code` varchar(20) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(100) DEFAULT NULL COMMENT '物料名称',
  `material_type` int DEFAULT NULL COMMENT '产品类型 0-照明类 1-其他',
  `Sample_delivery_date` date DEFAULT NULL COMMENT '送样日期',
  `predict_complete_date` date DEFAULT NULL COMMENT '预计完成日期',
  `send_inspect_qty` int DEFAULT '0' COMMENT '送检数量',
  `below_standard_qty` int DEFAULT '0' COMMENT '不合格数量',
  `version_text` varchar(100) DEFAULT NULL COMMENT '版本描述',
  `supplier_id` varchar(20) DEFAULT NULL COMMENT '供应商id',
  `supplier_name` varchar(50) DEFAULT NULL COMMENT '供应商名称',
  `buyer` varchar(30) DEFAULT NULL COMMENT '采购员',
  `lead_engineer` varchar(30) DEFAULT NULL COMMENT '主导工程师',
  `temperature_humidity` varchar(100) DEFAULT NULL COMMENT '环境温湿度',
  `check_status` tinyint DEFAULT '7' COMMENT '检验状态 0-待审核 4-已检验 7待检验 8-检验中',
  `check_result` tinyint DEFAULT NULL COMMENT '检验结果 0-不合格 1-合格',
  `check_item_qty` int DEFAULT '0' COMMENT '测试项目数',
  `check_remark` varchar(255) DEFAULT NULL COMMENT '检验备注',
  `checker` varchar(50) DEFAULT NULL COMMENT '检验人',
  `check_start_date` date DEFAULT NULL COMMENT '检验开始日期',
  `check_end_date` date DEFAULT NULL COMMENT '检验结束日期',
  `approver_name` varchar(50) DEFAULT NULL COMMENT '核准人姓名',
  `json_file` json DEFAULT NULL COMMENT '送样文件',
  `check_report` json DEFAULT NULL COMMENT '样品检测报告',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `updater` bigint NOT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uk_sample_apply_no` (`sample_apply_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='样品检验单';

-- ----------------------------
-- Table structure for qms_sample_check_plan
-- ----------------------------
DROP TABLE IF EXISTS `qms_sample_check_plan`;
CREATE TABLE `qms_sample_check_plan` (
  `id` bigint NOT NULL COMMENT 'id',
  `plan_name` varchar(50) DEFAULT NULL COMMENT '方案名称',
  `default_flag` tinyint NOT NULL DEFAULT '0' COMMENT '默认方案 0-否 1-是',
  `material_code_list` json DEFAULT NULL COMMENT '物料列表',
  `check_template_file` json DEFAULT NULL COMMENT '检验模板文件',
  `creator` bigint NOT NULL COMMENT '创建人',
  `create_name` varchar(20) DEFAULT NULL COMMENT '创建人姓名',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater` bigint NOT NULL COMMENT '修改人',
  `update_name` varchar(20) DEFAULT NULL COMMENT '修改人姓名',
  `update_time` datetime DEFAULT NULL COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='样品检验方案';

-- ----------------------------
-- Table structure for qms_sampling_plan
-- ----------------------------
DROP TABLE IF EXISTS `qms_sampling_plan`;
CREATE TABLE `qms_sampling_plan` (
  `id` bigint NOT NULL COMMENT 'id',
  `name` varchar(32) DEFAULT NULL COMMENT '抽样方案名称',
  `type` tinyint DEFAULT NULL COMMENT '抽样标准;0:QAL全检1:按比例抽检2:全检',
  `batch_size` tinyint DEFAULT NULL COMMENT '批量大小;0:2～8  1:9～15 2:16～25 3:26～50 4:51～90 5:91～150 6:151～280 7:281～500 8:501～1200 9:1201～3200',
  `sample_qty` int DEFAULT '0' COMMENT '样本量',
  `acceptance_qty` int DEFAULT '0' COMMENT '允收数量(AC)',
  `reject_qty` int DEFAULT '0' COMMENT '拒收数量(Re)',
  `creator` bigint NOT NULL COMMENT '创建人',
  `updater` bigint NOT NULL COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='抽样方案';

-- ----------------------------
-- Table structure for qms_sip
-- ----------------------------
DROP TABLE IF EXISTS `qms_sip`;
CREATE TABLE `qms_sip` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_type` varchar(50) DEFAULT NULL COMMENT '文件类型',
  `material_list` json DEFAULT NULL COMMENT '物料列表',
  `material_code` varchar(30) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(150) DEFAULT NULL COMMENT '物料编码',
  `file_no` varchar(50) DEFAULT NULL COMMENT '文件编号',
  `file_name` varchar(200) DEFAULT NULL COMMENT '文件名称',
  `file_status` tinyint DEFAULT '0' COMMENT '文件状态 0-保存待提交 1-修改待提交 2-保存待审核 3-修改待审核 4-删除待审核 5-审核不通过 6-已审核 7-已受控',
  `default_flag` tinyint DEFAULT '0' COMMENT '是否默认SIP 0-否 1-是',
  `request_id` varchar(20) DEFAULT NULL COMMENT 'OA流程id',
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `qms_sip_material_code_uindex` (`material_code`),
  UNIQUE KEY `idx_uk_sip_file_no` (`file_no`)
) ENGINE=InnoDB AUTO_INCREMENT=1930470917912629252 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='质量检验指导书';

-- ----------------------------
-- Table structure for qms_sip_controlled
-- ----------------------------
DROP TABLE IF EXISTS `qms_sip_controlled`;
CREATE TABLE `qms_sip_controlled` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `material_list` json DEFAULT NULL COMMENT '物料列表',
  `material_code` varchar(30) DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(150) DEFAULT NULL COMMENT '物料编码',
  `file_no` varchar(50) DEFAULT NULL COMMENT '文件编号',
  `check_project` tinyint DEFAULT NULL COMMENT '检验类型',
  `process_no` varchar(50) DEFAULT NULL COMMENT '工序编码',
  `process_name` varchar(50) DEFAULT NULL COMMENT '工序名称',
  `sip_file` json DEFAULT NULL COMMENT 'SIP文件',
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
) ENGINE=InnoDB AUTO_INCREMENT=1931217710547742723 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='受控质量检验指导书';

-- ----------------------------
-- Table structure for qms_sip_process_detail
-- ----------------------------
DROP TABLE IF EXISTS `qms_sip_process_detail`;
CREATE TABLE `qms_sip_process_detail` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `sip_id` bigint DEFAULT NULL COMMENT 'sip文件id',
  `check_project` json DEFAULT NULL COMMENT '检验类型',
  `process_no` varchar(50) DEFAULT NULL COMMENT '工序编码',
  `process_name` varchar(50) DEFAULT NULL COMMENT '工序名称',
  `sip_file` json DEFAULT NULL COMMENT 'sip文件列表',
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
) ENGINE=InnoDB AUTO_INCREMENT=1930511650099007491 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='质量检验指导书工序明细';

-- ----------------------------
-- Table structure for qms_skill_configuration_details
-- ----------------------------
DROP TABLE IF EXISTS `qms_skill_configuration_details`;
CREATE TABLE `qms_skill_configuration_details` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `work_no` varchar(55) DEFAULT NULL COMMENT '工号',
  `skill_name` varchar(55) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '技能名称',
  `skill_type` varchar(55) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '技能类型',
  `skill_validity_period` datetime DEFAULT NULL COMMENT '技能有效期',
  `status` int DEFAULT NULL COMMENT '状态 0-禁用 1-启用',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='技能标签';

-- ----------------------------
-- Table structure for qms_skill_label
-- ----------------------------
DROP TABLE IF EXISTS `qms_skill_label`;
CREATE TABLE `qms_skill_label` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `skill_name` varchar(55) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '技能名称',
  `skill_type` varchar(55) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '技能类型',
  `skill_validity_period` int DEFAULT NULL COMMENT '技能有效期',
  `status` int DEFAULT NULL COMMENT '状态 0-禁用 1-启用',
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
  `date` varchar(50) DEFAULT NULL COMMENT '时间单位',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1817821208917499908 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='技能标签';

-- ----------------------------
-- Table structure for qms_skill_personnel_tag_configuration
-- ----------------------------
DROP TABLE IF EXISTS `qms_skill_personnel_tag_configuration`;
CREATE TABLE `qms_skill_personnel_tag_configuration` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `work_no` varchar(60) DEFAULT NULL COMMENT '工号',
  `name` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '姓名',
  `department` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '部门',
  `personnel_position` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '人员岗位',
  `skill_label` int DEFAULT NULL COMMENT '技能标签',
  `skill_label_detail` json DEFAULT NULL COMMENT '技能标签明细',
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
) ENGINE=InnoDB AUTO_INCREMENT=1900066003959042051 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='人员技能标签配置';

-- ----------------------------
-- Table structure for qms_skill_type
-- ----------------------------
DROP TABLE IF EXISTS `qms_skill_type`;
CREATE TABLE `qms_skill_type` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `skill_type` varchar(55) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '技能类型',
  `skill_description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '技能描述',
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
) ENGINE=InnoDB AUTO_INCREMENT=1774676800278536196 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='技能类型表';

-- ----------------------------
-- Table structure for qms_supplier_material_testing
-- ----------------------------
DROP TABLE IF EXISTS `qms_supplier_material_testing`;
CREATE TABLE `qms_supplier_material_testing` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'id',
  `supplier_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '供应商ID',
  `supplier_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '供应商名称',
  `material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料编码',
  `material_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料名称',
  `material_specification` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '物料规格',
  `checkout_number` int DEFAULT NULL COMMENT '送检数量',
  `start_time` datetime DEFAULT NULL COMMENT '开始时间',
  `predict_complete_date` datetime DEFAULT NULL COMMENT '预计完成时间',
  `checkout_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '送检时间',
  `checkout_accomplish_date` datetime DEFAULT NULL COMMENT '送检完成时间',
  `specification` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '规格',
  `checkout_status` tinyint DEFAULT '0' COMMENT '检验状态 0 未开始  1 检验中\r\n   2 检验完成   3 不合格退品',
  `not_qualified_number` int DEFAULT NULL COMMENT '不合格数量',
  `qualified_number` int DEFAULT NULL COMMENT '合格数量',
  `priority` int DEFAULT '100' COMMENT '优先级 1 为优先级最高',
  `comment` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint DEFAULT NULL COMMENT '创建人',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '创建人名称',
  `updater` bigint DEFAULT NULL COMMENT '修改人',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '更新人名称',
  `del_flag` bit(1) DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  `version` int DEFAULT '1' COMMENT '版本号',
  `enabled` bit(1) DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `tenant_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT '1001' COMMENT '租户编码',
  `old_material_code` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_supplier_id_checkout_status_idx` (`supplier_id`,`checkout_status`) USING BTREE,
  KEY `idx_supplier_id_idx` (`supplier_id`) USING BTREE,
  KEY `idx_material_code` (`material_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1675789722856640516 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='供应商送料检测';

-- ----------------------------
-- Table structure for qms_supplier_score_detailed
-- ----------------------------
DROP TABLE IF EXISTS `qms_supplier_score_detailed`;
CREATE TABLE `qms_supplier_score_detailed` (
  `id` bigint NOT NULL COMMENT 'ID',
  `supplier_name` varchar(128) DEFAULT NULL COMMENT '供应商名称',
  `year` varchar(32) DEFAULT NULL COMMENT '年份',
  `quarter` varchar(32) DEFAULT NULL COMMENT '季度',
  `supply_qty` int DEFAULT NULL COMMENT '供应次数',
  `below_standard_batch` int DEFAULT NULL COMMENT '不合格批次',
  `batch_defect_rate` decimal(4,2) DEFAULT NULL COMMENT '批次不良率',
  `sample_qty` int DEFAULT NULL COMMENT '抽样数量',
  `below_standard_qty` int DEFAULT NULL COMMENT '不合格数量',
  `below_standard_rate` decimal(4,2) DEFAULT NULL COMMENT '不合格率',
  `special_qty` int DEFAULT NULL COMMENT '特采次数',
  `score` int DEFAULT NULL COMMENT '评分',
  `grade` varchar(32) DEFAULT NULL COMMENT '等级',
  `repeat_qty` int DEFAULT NULL COMMENT '重复次数',
  `serious_qty` int DEFAULT NULL COMMENT '重大异常次数',
  `remarks` varchar(128) DEFAULT NULL COMMENT '备注',
  `creator` bigint NOT NULL DEFAULT '0' COMMENT '创建人',
  `updater` bigint NOT NULL DEFAULT '0' COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='供应商评分明细';

-- ----------------------------
-- Table structure for qms_user_complains_records
-- ----------------------------
DROP TABLE IF EXISTS `qms_user_complains_records`;
CREATE TABLE `qms_user_complains_records` (
  `id` bigint NOT NULL COMMENT 'id',
  `complaint_type` int DEFAULT NULL COMMENT '投诉类型:0 严重、1 一般、2 轻微',
  `material_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料编码',
  `model_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '机型名称',
  `sn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '产品序列号',
  `material_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '物料名称',
  `bad_qty` int DEFAULT NULL COMMENT '不良数量',
  `recorder` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '记录人',
  `recorder_job_number` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '记录人工号',
  `dept` varchar(32) DEFAULT NULL COMMENT '记录部门',
  `source` int DEFAULT NULL COMMENT '信息来源: 0 邮件、 1 官网、2 社交媒体、 3 其他',
  `status` int DEFAULT '0' COMMENT '处理状态: 0 待处理、1 已处理 2 已关闭',
  `question_type` int DEFAULT NULL COMMENT '问题类型:0 外观、1 功能、2 包装、3 可靠性、4 安全',
  `be_process` tinyint DEFAULT '1' COMMENT '是否需要处理 0-无需处理 1-需要处理',
  `file_url` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '不良附件',
  `json_files` json DEFAULT NULL COMMENT '文件列表',
  `outcome_feedback` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '与客户沟通结果反馈',
  `cause_analysis` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '原因分析',
  `description` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '问题描述',
  `description_zh` varchar(1500) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '问题描述中文',
  `data_type` tinyint DEFAULT NULL COMMENT '数据类型 1:原始数据 2:客诉数据',
  `handler` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '处理人',
  `handle_result` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '处理结果',
  `country` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '国家',
  `resolved` tinyint DEFAULT '0' COMMENT '是否解决 0-未解决 1-已解决',
  `expect_reply_date` varchar(20) DEFAULT NULL COMMENT '期待回复日期',
  `follow_file_url` varchar(1024) DEFAULT NULL COMMENT '跟进附件',
  `handle_file_url` varchar(1024) DEFAULT NULL COMMENT '处理附件',
  `rejects_codes` json DEFAULT NULL COMMENT '不良代码',
  `follow_json_files` json DEFAULT NULL COMMENT '跟进附件',
  `handle_json_files` json DEFAULT NULL COMMENT '处理附件',
  `remark` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '备注',
  `creator` bigint NOT NULL DEFAULT '0' COMMENT '创建人',
  `updater` bigint NOT NULL DEFAULT '0' COMMENT '修改人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_name` varchar(30) DEFAULT NULL COMMENT '创建人',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '修改时间',
  `update_name` varchar(30) DEFAULT NULL COMMENT '修改人',
  `enabled` bit(1) NOT NULL DEFAULT b'1' COMMENT '是否启用(0-未启用/1-已启用)',
  `version` int NOT NULL DEFAULT '1' COMMENT '版本号',
  `del_flag` bit(1) NOT NULL DEFAULT b'0' COMMENT '删除标识  0：未删除    1：删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='客户投诉记录';

SET FOREIGN_KEY_CHECKS = 1;
