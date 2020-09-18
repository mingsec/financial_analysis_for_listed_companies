-- Create database
CREATE DATABASE financial_analysis_for_listed_companies;


-- Create financial_data table
CREATE TABLE financial_data(
  id             int         NOT NULL AUTO_INCREMENT,
  公司代码       char(6)      NOT NULL,
  报告日期       char(10)     NOT NULL,
  科目名称       char(100)    NOT NULL,
  值             char(15)    NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;


-- Create company_information table
CREATE TABLE company_information(
  公司代码          char(6)        NOT NULL,
  组织形式          char(20)               ,
  地域             char(20)       NOT NULL,
  中文简称          char(10)        NOT NULL,
  办公地址          char(100)       NOT NULL,
  公司全称          char(100)       NOT NULL,
  公司电话          char(50)       NOT NULL,
  英文名称          char(100)       NOT NULL,
  公司电子邮箱       char(50)       NOT NULL,
  注册资本          char(20)       NOT NULL,
  董事长            char(50)       NOT NULL,
  员工人数          char(20)       NOT NULL,
  董事会秘书        char(20)       NOT NULL,
  法人代表          char(20)       NOT NULL,
  董秘电话          char(50)       NOT NULL,
  总经理            char(20)       NOT NULL,
  董秘传真          char(50)       NOT NULL,
  公司网址          char(100)       NOT NULL,
  董秘邮箱          char(50)       NOT NULL,
  信息披露网址      char(50)       NOT NULL,
  信息披露报纸名称   char(50)       NOT NULL,
  主营业务          varchar(300)   NOT NULL,
  经营范围          varchar(300)   NOT NULL,
  公司沿革          varchar(300)   NOT NULL,
  PRIMARY KEY (公司代码)
) ENGINE=InnoDB;

-- Create IPO_information table
CREATE TABLE IPO_information(
  公司代码          char(6)         NOT NULL,
  成立日期          char(12)        NOT NULL,
  上市日期          char(12)        NOT NULL,
  发行方式          char(255)        NOT NULL,
  面值             char(20)         NOT NULL,
  发行数量          char(15)        NOT NULL,
  发行价格          char(15)        NOT NULL,
  募资资金总额       char(15)        NOT NULL,
  发行费用          char(20)        NOT NULL,
  发行中签率        char(10)         NOT NULL,
  发行市盈率        char(10)         NOT NULL,
  发行后每股收益    char(10)         NOT NULL,
  发行后每股净资产  char(10)         NOT NULL,
  上市首日开盘价    char(10)         NOT NULL,
  上市首日收盘价    char(10)         NOT NULL,
  上市首日换手率    char(10)         NOT NULL,
  主承销商          char(100)        NOT NULL,
  上市保荐人        char(100)        NOT NULL,
  会计师事务所      char(100)        NOT NULL,
  PRIMARY KEY (公司代码)
) ENGINE=InnoDB;


-- Create board_of_directors table
CREATE TABLE board_of_directors(
  id              int        NOT NULL AUTO_INCREMENT,
  公司代码         char(6)    NOT NULL,
  更新日期         char(15)   NOT NULL,
  姓名            char(50)    NOT NULL,
  职务            char(20)   NOT NULL,
  起止时间         char(25)   NOT NULL,
  持股数_万股      char(12)   NOT NULL,
  报酬_元          char(12)   NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;


-- Create revenue_data table
CREATE TABLE revenue_data(
  id           int            NOT NULL AUTO_INCREMENT,
  公司代码       char(6)       NOT NULL,
  报告日期       char(12)      NOT NULL,
  分类维度       char(20)      NOT NULL,
  分类名称       char(50)      NOT NULL,
  收入_万元      char(15)      NOT NULL,
  成本_万元      char(15)      NOT NULL,
  利润_万元      char(15)      NOT NULL,
  毛利率         char(15)        NOT NULL,
  利润占比       char(15)        NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;

-- Create employees_data table
CREATE TABLE employees_data(
  id             int         NOT NULL AUTO_INCREMENT,
  公司代码       char(6)     NOT NULL,
  报告日期       char(15)    NOT NULL,
  分类维度       char(20)     NOT NULL,
  分类名称       char(50)    NOT NULL,
  员工人数       char(15)    NOT NULL,
  员工占比       char(15)    NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB;