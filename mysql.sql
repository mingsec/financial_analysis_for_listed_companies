-- Create database
CREATE DATABASE FALC_pro;


-- Create financial_data table
CREATE TABLE financial_data(
  ID  int  NOT NULL AUTO_INCREMENT,
  公司代码  char(6)  NOT NULL,
  报告日期  date  NOT NULL,
  项目编号  char(6)  NOT NULL,
  值  decimal(22,2)  NOT NULL,
  PRIMARY KEY (ID)
)ENGINE=InnoDB;


-- Create corporation_information table
CREATE TABLE corporation_information(
  公司代码  char(6)  NOT NULL,
  公司名称  char(100)  NOT NULL,
  公司英文名称  char(100)  NOT NULL,
  上市市场  char(10)  NOT NULL,
  上市日期  date  NOT NULL,
  发行价格  decimal(5,2)  NOT NULL, 
  主承销商  char(100)  NOT NULL,
  成立日期  date  NOT NULL,
  注册资本(万元)  decimal(18,2)  NOT NULL,
  机构类型  char(20)   NOT NULL,
  组织形式  char(20)   NOT NULL,
  董事会秘书  char(20)  NOT NULL,
  公司电话  char(25)  NOT NULL,
  董秘电话  char(25)  NOT NULL,
  公司传真  char(25)  NOT NULL,
  董秘传真  char(25)  NOT NULL,
  公司电子邮箱  char(50)  NOT NULL,
  董秘电子邮箱  char(50)  NOT NULL,
  公司网址  char(100)  NOT NULL,
  邮政编码  char(6)  NOT NULL,
  信息披露网址  char(50)  NOT NULL,
  证券简称更名历史  char(255)  NOT NULL,
  注册地址  char(100)  NOT NULL,
  办公地址  char(100)  NOT NULL,
  公司简介  char(255)  NOT NULL,
  经营范围  char(255)  NOT NULL, 
  PRIMARY KEY (公司代码)
)ENGINE=InnoDB;


-- Create issue_information table
CREATE TABLE issue_information(
  公司代码  char(6)  NOT NULL,
  上市地  char(10)  NOT NULL,
  主承销商  char(100)  NOT NULL,
  承销方式  char(50)  NOT NULL,
  上市推荐人  char(100)  NOT NULL,
  每股发行价(元)  decimal(5,2)  NOT NULL, 
  发行方式    char（255)  NOT NULL,
  发行市盈率(按发行后总股本)  decimal(10,2)  NOT NULL, 
  首发前总股本(万股)  decimal(18,2)  NOT NULL,
  首发后总股本(万股)  decimal(18,2)  NOT NULL,
  实际发行量(万股)  decimal(18,2)  NOT NULL,
  预计募集资金(万元)  decimal(18,2)  NOT NULL,
  实际募集资金合计(万元)  decimal(18,2)  NOT NULL,
  发行费用总额(万元)  decimal(18,2)  NOT NULL,
  募集资金净额(万元)  decimal(18,2)  NOT NULL,
  承销费用(万元)  decimal(18,2)  NOT NULL,
  招股公告日  date  NOT NULL,
  上市日期  date  NOT NULL,
  PRIMARY KEY (公司代码)
)ENGINE=InnoDB;