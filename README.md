# Financial Analysis for Listed Companies
_一个从网络上下载上市公司财务报表进行财务分析的python系统_


20200918 version0.0.1
1. 修改前期Python爬虫代码用于下载创业板、科创板公司信息数据
2. 修改相关代码用于上市公司财务分析
3. 创建git仓库
4. 生成requirements文档

20200921 version0.0.2
1. 修复无法使用executemany()存入数据的bug
2. 修复statement_type_code数据类型的错误
3. 其他文字显示错误
4. 增加check_list()函数
5. 增加download_data()函数
6. 优化调整main

20200924 version0.0.3
1. 增加get_financial_data_from_SINA()函数
2. 增加get_corporation_information_from_SINA()函数
3. 增加get_issue_information_from_SINA()函数
4. 增加sava_data_to_database()函数
5. 创建MySQL.sql文档，用于创建数据库及表(正式数据库)
6. 增加download_listed_companies_data()函数
7. 优化调整main
8. 更新requirements.txt文档
