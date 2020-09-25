import os
import time, datetime
import re 

import pandas
import requests
import pymysql
from bs4 import BeautifulSoup
from lxml import etree
from decimal import Decimal, getcontext

# 设置货币的有效数字
getcontext().prec = 22

def get_financial_statement(statement_type_code, com_code):
    """从163股票网站下载特定单位的财务报表,同时对下载的财务报表进行数据清洗，并转成一维数据
    参数
    ----------
    statement_type_code: str
        可供下载的报表类：1 - 资产负债表； 2 - 利润表； 3 - 现金流量表； 4 - 公司资料
    com_code: str
        上市公司的在证券市场上的6位代码
        
    返回值
    -------
    database_table_type: str
        数据待存入的数据库表的简写
    data: list
        将财务报表整理成一维数据，每条记录4个字段，从左至右依次为：公司代码、报告日期、科目、值
    """

    """ 根据报表编号确定报表类型、名称、数据库表类型以及科目前缀 """
    if statement_type_code == '1':
        statement_type = 'zcfzb'
        statement_name = '资产负债表'
        database_table_type = 'BS'
        front_name = 'BS-'
    elif statement_type_code == '2':
        statement_type = 'lrb'
        statement_name = '利润表'
        database_table_type = 'PL'
        front_name = 'PL-'
    elif statement_type_code == '3':
        statement_type = 'xjllb'
        statement_name = '现金流量表'
        database_table_type = 'CF'
        front_name = 'CF-'
    else:
        print("不支持的报表类型！")

    """ 下载数据 """
    print("开始下载" + com_code + "的" + statement_name + "...")
    # 配置下载数据的URL
    url = 'http://quotes.money.163.com/service/' + statement_type + '_' + com_code + '.html' 
    # 下载数据
    try:
        page_data = pandas.read_csv(url, encoding='gbk', header=None)
        print("数据下载完毕！")
    except :
        print("该公司信息不存在，请检查输入的公司代码是否正确。")
        return
    
    """ 整理数据格式 """
    print("开始处理数据...")
    formate_data = []
    for row in range(1, page_data.shape[0]):
        # 处理非空行数据
        if len(page_data.iloc[row]):
            # 生成项目名称
            subject_name = front_name + page_data.iloc[row, 0][:-4].strip()
            # 调整项目名称
            if subject_name == 'PL-基本':
                subject_name = 'PL-基本每股收益'
            if subject_name == 'PL-稀释':
                subject_name = 'PL-稀释每股收益'
            if subject_name == 'BS-向中央银行借款净增加':
                subject_name = 'BS-向中央银行借款净增加额'
            # 按特定格式输出数据
            for column in range(1, page_data.shape[1]-1):
                # 将“--”替换为0
                if page_data.iloc[row, column] == '--':
                    page_data.iloc[row, column] = 0
                # 丢弃值为0的记录
                if page_data.iloc[row, column] == 0:
                    continue
                # 删除单元格中的空格' '
                report_date = page_data.iloc[0, column].replace(' ', '')
                value = page_data.iloc[row, column].replace(' ', '')
                formate_data.append([com_code, report_date, subject_name, value]) 
    print("数据处理完毕！")

    return [[database_table_type, formate_data], ]

"""
def get_company_information(statement_type_code, com_code):
    '''从163股票网站下载特定单位的企业信息，并对其进行清洗
    参数
    ----------
    statement_type_code: int
        可供下载的报表类：1 - 资产负债表； 2 - 利润表； 3 - 现金流量表； 4 - 公司资料
    com_code: int
        上市公司的在证券市场上的6位代码
        
    返回值
    -------
    str
        返回下载完的公司资料的文件名
    '''

    if statement_type_code == '4':
        statement_type = 'gszl'
    else:
        print("不支持的报表类型！")

    #获取包含公司资料的网页
    print("开始下载" + com_code + "的公司资料...")
    url = 'http://quotes.money.163.com/f10/' + statement_type + '_' + com_code + '.html#01f02'
    try:
        page = requests.get(url)
    except:
        print("该公司信息不存在，请检查输入的公司代码是否正确。")
    print("数据下载完毕！")

    #解析网页，获取所有表格并清洗数据
    print("开始处理数据...")
    soup = BeautifulSoup(page.text, 'html.parser')
    tables = soup.find_all('table')
    table_list =[]
    #获取表格数据
    for table in tables:
        table_rows = []
        #获取表格的所有行数据
        results = table.find_all('tr')
        # 清洗表格数据
        for tr in results:
            table_row = []
            # 获取表格单元格数据，并进行清洗
            for td in tr:
                table_cell = td.string
                #丢弃数据为'\n'、None和''的单元格
                if table_cell == '\n' or table_cell == None or table_cell == '':
                    continue
                #删除单元格中的空格' '和'\r\n'
                table_cell = table_cell.replace(' ', '')
                table_cell = table_cell.replace('\r\n', '')
                table_row.append(table_cell)
            table_rows.append(table_row)
        table_list.append(table_rows)

    #整理企业信息数据
    enterprise_information = []

    #整理公司信息数据格式
    company_information = [com_code]
    for item in table_list[3]:
        if len(item) == 4:
            company_information = company_information + [item[1], item[3]]
        else:
            company_information.append(item[1]) 
    
    #整理IPO信息数据格式
    IPO_information = [com_code]
    for item in table_list[4]:
        IPO_information.append(item[1])
    

    #整理董事会成员信息数据格式
    #获取数据最近更新日期
    update_date_results = soup.find_all('h2', attrs={'class':'title_01'})
    for item in  update_date_results:
        update_date_results = item.find('li')
        if update_date_results ==None:
            continue
        else:
            last_update_date = update_date_results.string[-10:]
    #拼接数据
    board_of_directors = []
    for item in table_list[5][1:]:
        item = [com_code, last_update_date] + item
        board_of_directors.append(item)
    

    #整理收入数据格式
    #获取报告日期
    report_date_results = soup.find('div', attrs={'class':'report_date'})
    report_date_result = report_date_results.find('span')
    report_date = report_date_result.string[-10:]
    #拼接数据
    revenue_data = []
    for item in table_list[6:9]:
        for row in item[1:]:
            row = [com_code, report_date, item[0][0]] + row
            revenue_data.append(row)
    

    #整理员工数据格式
    employees_data =[]
    for item in table_list[9:]:
        for row in item[1:len(item)-1]:
            row = [com_code, report_date, item[0][0]] + row
            employees_data.append(row)
""" 

def write_data_to_database(date_tables):
    """ 创建数据库连接，打开数据库，并调用函数将数据存入 MySQL 数据库
    参数
    ----------
    date_tables: list
        欲存入数据库的数据
        
    返回值
    -------
    无
    """

    """ 配置 SQL 插入语句 """
    # 配置 financial_data 表更新 SQL 语句      
    # SQL_FD = f"INSERT INTO { table_name }({ fileds })financial_data(公司代码, 报告日期, 科目名称, 值) VALUES ({ field_values })('%s','%s','%s','%s')"
    # 配置 company_information 表更新 SQL 语句 
    #SQL_CI = "INSERT INTO company_information(公司代码, 组织形式, 地域, 中文简称, 办公地址,\
    #                                          公司全称, 公司电话, 英文名称, 公司电子邮箱, 注册资本,\
    #                                          董事长, 员工人数, 董事会秘书, 法人代表, 董秘电话,\
    #                                          总经理, 董秘传真, 公司网址, 董秘邮箱, 信息披露网址,\
    #                                          信息披露报纸名称, 主营业务, 经营范围, 公司沿革) VALUES ('%s', '%s', '%s', '%s', '%s',\
    #                                                                                              '%s', '%s', '%s', '%s', '%s',\
    #                                                                                              '%s', '%s', '%s', '%s', '%s',\
    #                                                                                              '%s', '%s', '%s', '%s', '%s',\
    #                                                                                              '%s', '%s', '%s', '%s')"
    # 配置 IPO_information 表更新 SQL 语句 
    #SQL_II = "INSERT INTO IPO_information(公司代码, 成立日期, 上市日期, 发行方式, 面值,\
    #                                      发行数量, 发行价格, 募资资金总额, 发行费用, 发行中签率,\
    #                                      发行市盈率, 发行后每股收益, 发行后每股净资产, 上市首日开盘价, 上市首日收盘价,\
    #                                      上市首日换手率, 主承销商, 上市保荐人, 会计师事务所) VALUES ('%s', '%s', '%s', '%s', '%s',\
    #                                                                                              '%s', '%s', '%s', '%s', '%s',\
    #                                                                                              '%s', '%s', '%s', '%s', '%s',\
    #                                                                                              '%s', '%s', '%s', '%s')"
    # 配置 board_of_directors 表更新 SQL 语句 
    #SQL_BD = "INSERT INTO board_of_directors(公司代码, 更新日期, 姓名, 职务, 起止时间, 持股数_万股, 报酬_元) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
    # 配置 revenue_data 表更新 SQL 语句 
    #SQL_RD = "INSERT INTO revenue_data(公司代码, 报告日期, 分类维度, 分类名称, 收入_万元, 成本_万元, 利润_万元, 毛利率, 利润占比) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
    # 配置 employees_data 表更新 SQL 语句 
    #SQL_ED = "INSERT INTO employees_data(公司代码, 报告日期, 分类维度, 分类名称, 员工人数, 员工占比) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"

    """ 创建数据库连接及游标 """
    FADB = pymysql.connect(
        host='88.88.4.123', 
        port=3306, 
        user='root', 
        passwd='330715', 
        db='financial_analysis_for_listed_companies')
    cursor = FADB.cursor()
    
    """ 将数据写入数据库 """
    print("开始向数据库写入数据...")
    for table in date_tables:
        # 根据表格类型确定待写入数据的表名、字段名及字段值数量
        if table[0] == 'BS':
            table_name = 'financial_data'
            fileds = '公司代码, 报告日期, 科目名称, 值'
            field_values = r'%s, %s, %s, %s'
            data_type = "资产负债表数据"
        elif table[0] == 'PL':
            table_name = 'financial_data'
            fileds = '公司代码, 报告日期, 科目名称, 值'
            field_values = r'%s, %s, %s, %s'
            data_type = "利润表数据"
        elif table[0] == 'CF':
            table_name = 'financial_data'
            fileds = '公司代码, 报告日期, 科目名称, 值'
            field_values = r'%s, %s, %s, %s'
            data_type = "现金流量表数据"
        elif table[0] == 'CI':
            table_name = 'company_information'
            fileds = '公司代码, 组织形式, 地域, 中文简称, 办公地址, 公司全称, 公司电话, 英文名称, 公司电子邮箱,  注册资本, \
                董事长, 员工人数, 董事会秘书, 法人代表, 董秘电话, 总经理, 董秘传真, 公司网址, 董秘邮箱, 信息披露网址, \
                信息披露报纸名称, 主营业务, 经营范围, 公司沿革'
            field_values = r'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'
            data_type = "公司信息数据"
        elif table[0] == 'II':
            table_name = 'IPO_information'
            fileds = '公司代码, 成立日期, 上市日期, 发行方式, 面值, 发行数量, 发行价格, 募资资金总额, 发行费用, 发行中签率, \
                发行市盈率, 发行后每股收益, 发行后每股净资产, 上市首日开盘价, 上市首日收盘价, 上市首日换手率, 主承销商, 上市保荐人, 会计师事务所'
            field_values = r'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'
            data_type = "IPO信息数据"
        elif table[0] == 'BD':
            table_name = 'board_of_directors'
            fileds = '公司代码, 更新日期, 姓名, 职务, 起止时间, 持股数_万股, 报酬_元'
            field_values = r'%s, %s, %s, %s, %s, %s, %s'
            data_type = "董事会成员信息数据"
        elif table[0] == 'RD':
            table_name = 'revenue_data'
            fileds = '公司代码, 报告日期, 分类维度, 分类名称, 收入_万元, 成本_万元, 利润_万元, 毛利率, 利润占比'
            field_values = r'%s, %s, %s, %s, %s, %s, %s, %s, %s'
            data_type = "收入数据"
        elif table[0] == 'ED':
            table_name = 'employees_data'
            fileds = '公司代码, 报告日期, 分类维度, 分类名称, 员工人数, 员工占比'
            field_values = r'%s, %s, %s, %s, %s, %s'
            data_type = "职工数据"
        
        # 向数据库写入数据
        print("..." + data_type + "写入完毕")
        cursor.executemany(f"INSERT INTO { table_name }({ fileds }) VALUES ({ field_values })", table[1])

    """ 向数据库提交操作并关闭数据库连接 """
    FADB.commit()
    FADB.close()
    print("数据保存成功！")


def get_enterprise_information(statement_type_code, com_code):
    """从163股票网站下载特定单位的企业信息，并对其进行清洗
    参数
    ----------
    statement_type_code: str
        可供下载的报表类：1 - 资产负债表； 2 - 利润表； 3 - 现金流量表； 4 - 公司资料
    com_code: str
        上市公司的在证券市场上的6位代码
        
    返回值
    -------
    data_list:list
        返回下载完的公司资料的数据列表,列表格式为：[["表类型"，[[记录1],[记录2]...]],[...]]
        [
            ["表类型"，[
                [记录1],
                [记录2],...]
            ],
            [...]
        ]
    """

    """ 保存返回数据的空列表 """
    enterprise_information =[]

    """ 判断调用的下载函数是否正确 """
    if statement_type_code == '4':
        statement_type = 'gszl'
    else:
        print("不支持的报表类型！")

    """ 获取包含公司资料的网页 """
    print("开始下载" + com_code + "的公司资料...")
    # 配置下载数据的URL 
    url = 'http://quotes.money.163.com/f10/' + statement_type + '_' + com_code + '.html#01f02'
    # 下载数据
    try:
        page = requests.get(url)
        print("数据下载完毕！")
    except:
        print("该公司信息不存在，请检查输入的公司代码是否正确。")
        return 
    
    print("开始处理数据...")

    """ 初步处理数据 """
    # 获取初始化页面，用于后续解析
    page_elements = etree.HTML(page.text)
    # 查找并取得包含公司信息、IPO信息的表格代码
    tables_one = page_elements.xpath('//table[@class="table_bg001 border_box limit_sale table_details"]')
    tables_two = page_elements.xpath('//table[@class="table_bg001 border_box limit_sale"]')
    
    """ 获取并处理日期数据 """
    soup = BeautifulSoup(page.text, 'html.parser')
    # 获取最近更新日期
    update_date_results = soup.find_all('h2', attrs={'class':'title_01'})
    for item in  update_date_results:
        update_date_results = item.find('li')
        if update_date_results ==None:
            continue
        else:
            last_update_date = update_date_results.string[-10:]
    # 获取报告日期
    report_date_results = soup.find('div', attrs={'class':'report_date'})
    report_date_result = report_date_results.find('span')
    report_date = report_date_result.string[-10:]

    """ 处理公司信息数据 """
    company_information = [com_code]
    # 以str类型（decode()）输出（tostring(））修正后的HTML代码
    company_information_table = etree.tostring(tables_one[0], encoding='utf-8').decode()
    # 获取公司信息表格中的数据
    company_information_df = pandas.read_html(company_information_table, encoding='utf-8', header=None)[0]
    # 将空值替换为 “--”
    company_information_df.fillna('--', inplace=True)
    # # 收集 dataframe 中需要的数据
    for i in range(0, 10):
        company_information.append(company_information_df.iloc[i, 1])
        company_information.append(company_information_df.iloc[i, 3])
    for i in range(10, company_information_df.shape[0]):
        company_information.append(company_information_df.iloc[i, 1])
    # 去除数据中的异常字符空格 ' ' 和换行符 '\r\n' 等
    for i in range(1, len(company_information)):
        # 将值强制转换为str
        company_information[i] = str(company_information[i])
        company_information[i] = company_information[i].replace(' ', '')
        company_information[i] = company_information[i].replace('\r\n', '')
        company_information[i] = company_information[i].replace('"', ' ')
        company_information[i] = company_information[i].replace("'", ' ')
    enterprise_information.append(['CI', [company_information,]])
    print("...公司信息数据处理完毕")

    """ 处理IPO信息数据 """
    IPO_information = [com_code]
    # 以str类型（decode()）输出（tostring(））修正后的HTML代码
    IPO_information_table = etree.tostring(tables_one[1], encoding='utf-8').decode()
    # 获取 IPO 信息表格中的数据
    IPO_information_df = pandas.read_html(IPO_information_table, encoding='utf-8', header=None)[0]
    # 将空值替换为 “--”
    IPO_information_df.fillna('--', inplace=True)
    # 收集 dataframe 中需要的数据
    for i in range(0, IPO_information_df.shape[0]):
        IPO_information.append(IPO_information_df.iloc[i,1])
    # 去除数据中的异常字符空格 ' ' 和换行符 '\r\n' 等
    for i in range(1, len(IPO_information)):
        # 将值强制转换为str
        IPO_information[i] = str(IPO_information[i])
        IPO_information[i] = IPO_information[i].replace(' ', '')
        IPO_information[i] = IPO_information[i].replace('\r\n', '')
    enterprise_information.append(['II', [IPO_information,]])
    print("...IPO信息数据处理完毕")
    
    """ 处理董事会成员信息数据 """
    board_of_directors = []
    # 以str类型（decode()）输出（tostring(））修正后的HTML代码
    board_of_directors_table = etree.tostring(tables_two[0], encoding='utf-8').decode()
    # 获取董事会成员信息表格中的数据
    board_of_directors_df = pandas.read_html(board_of_directors_table, encoding='utf-8', header=None)[0]
    # 将空值替换为 “--”
    board_of_directors_df.fillna('--', inplace=True)
    # 收集 dataframe 中需要的数据
    for i in range(0, board_of_directors_df.shape[0]):
        board_of_directors.append([com_code, last_update_date] + list(board_of_directors_df.iloc[i]))
    # 去除数据中的异常字符空格 ' ' 和换行符 '\r\n' 等 
    for i in range(0, len(board_of_directors)):
        for j in range(0, len(board_of_directors[i])):
            # 将值强制转换为str
            board_of_directors[i][j] = str(board_of_directors[i][j])
            board_of_directors[i][j] = board_of_directors[i][j].replace(' ', '')
            board_of_directors[i][j] = board_of_directors[i][j].replace('\r\n', '')
    enterprise_information.append(['BD', board_of_directors])
    print("...董事会成员信息数据处理完毕")

    """ 收入数据 """
    revenue_data = []
    for i in range(1, 4):
        # 以str类型（decode()）输出（tostring(））修正后的HTML代码
        revenue_data_table = etree.tostring(tables_two[i], encoding='utf-8').decode()
        # 获取收入数据表格中的数据
        revenue_data_df = pandas.read_html(revenue_data_table, encoding='utf-8', header=None)[0]
        # 将空值替换为 “--”
        revenue_data_df.fillna('--', inplace=True)
        # 收集 dataframe 中需要的数据
        table_type = revenue_data_df.columns[0]
        for i in range(0, revenue_data_df.shape[0]):
            revenue_data.append([com_code, report_date, table_type] + list(revenue_data_df.iloc[i]))
    # 去除数据中的异常字符空格 ' ' 和换行符 '\r\n' 等  
    for i in range(0, len(revenue_data)):
        for j in range(0, len(revenue_data[i])):
            # 将值强制转换为str
            revenue_data[i][j] = str(revenue_data[i][j])
            revenue_data[i][j] = revenue_data[i][j].replace(' ', '')
            revenue_data[i][j] = revenue_data[i][j].replace('\r\n', '')
    enterprise_information.append(['RD', revenue_data])
    print("...收入数据处理完毕")

    """ 处理人员数据 """
    employees_data = []
    for i in range(4, len(tables_two)):
        # 以str类型（decode()）输出（tostring(））修正后的HTML代码
        employees_data_table = etree.tostring(tables_two[i], encoding='utf-8').decode()
        # 获取收入数据表格中的数据
        employees_data_df = pandas.read_html(employees_data_table, encoding='utf-8', header=None)[0]
        # 将空值替换为 “--”
        employees_data_df.fillna('--', inplace=True)
        # 收集 dataframe 中需要的数据
        table_type = employees_data_df.columns[0]
        for i in range(0, employees_data_df.shape[0]):
            employees_data.append([com_code, report_date, table_type] +  list(employees_data_df.iloc[i]))
    # 去除数据中的异常字符空格 ' ' 和换行符 '\r\n' 等   
    for i in range(0, len(employees_data)):
        for j in range(0, len(employees_data[i])):
            employees_data[i][j] = str(employees_data[i][j])
            employees_data[i][j] = employees_data[i][j].replace(' ', '')
            employees_data[i][j] = employees_data[i][j].replace('\r\n', '')
    enterprise_information.append(['ED', employees_data])
    print("...人员数据处理完毕")

    print("公司资料数据处理完毕...")

    return enterprise_information


def download_data(download_list):
    """ 调用函数从股票网站下载数据

    根据提供的 download_list 参数，选择不同的爬虫函数从股票网站下载数据，并将清理格式后的数据存入数据库，
    同时将下载失败或保存失败的数据存入 problem_list.txt 文档中

    参数
    -------
    download_list: list
        可公司资料的数据列表，列表格式为：[["公司代码", "报表类型"],[记录2],[...]]
        
    返回值
    -------
    无

    """

    problem_list = []
    
    if download_list:
        for item in download_list:
            try:
                if item[1] == '4':
                    write_data_to_database(get_enterprise_information(item[1], item[0]))
                else:
                    write_data_to_database(get_financial_statement(item[1], item[0]))
            except:
                problem_list.append(item[0] + " " + item[1]) 
            # 等待 5 秒
            time.sleep(5) 
            # 清除屏幕信息
            os.system('cls')
    else:
        continue_or_not = True
        while continue_or_not:
            com_code = input("请输入待下载报表的单位的公司代码：")
            statement_type_code = input("报表类型：\n 1 - 资产负债表\n 2 - 利润表\n 3 - 现金流量表\n 4 - 公司资料\n 请输入需下载的报表编号：")
        
            if statement_type_code == '4' : 
                write_data_to_database(get_enterprise_information(statement_type_code, com_code))
            else:
                write_data_to_database(get_financial_statement(statement_type_code, com_code))

            is_continue = input("是否继续（y/n)：")
            if is_continue == 'n' or is_continue == 'N':
                continue_or_not = False

            os.system('cls')
    
    with open("problem_list.txt", "w") as filetxt:
        for item in problem_list:
            filetxt.write(item + "\n")


def get_financial_data_from_SINA(com_code, statement_type_code):
    """
    """

    ''' 根据报表编号确定报表类型、名称、数据库表类型以及科目前缀 '''
    if statement_type_code == '1':
        statement_type = 'BalanceSheet'
        statement_name = '资产负债表'
        database_table_type = 'BS'
        front_name = 'BS-'
    elif statement_type_code == '2':
        statement_type = 'ProfitStatement'
        statement_name = '利润表'
        database_table_type = 'PS'
        front_name = 'PS-'
    elif statement_type_code == '3':
        statement_type = 'CashFlow'
        statement_name = '现金流量表'
        database_table_type = 'CF'
        front_name = 'CF-'
    else:
        print("报表类型选择错误，请重新选择！")
        return

    ''' 下载数据 '''
    print("开始下载" + com_code + "的" + statement_name + "...")
    # 配置下载数据的URL
    url = 'http://money.finance.sina.com.cn/corp/go.php/vDOWN_' + statement_type + '/displaytype/4/stockid/' + com_code + '/ctrl/all.phtml'
    # 下载数据，并保存为 pandas 的数据框架
    # 尽管下载的过来的数据为 .xls 格式的文档，但实际为 csv 格式的文档，所以用 read_csv() 函数，同时按 ‘\t’ 进行数据切分
    page_data = pandas.read_csv(url, encoding='gbk', header=None, sep='\t')
    print("数据下载完毕")
    
    print("开始处理数据...")

    ''' 将二维数据表转为一维数据表，并转换数据类型 '''
    origin_data = []
    # --.shape[0] 返回 dataframe 的行数
    # --.shape[1] 返回 dataframe 的列数
    for column in range(1, page_data.shape[1]-2):
        for row in range(2, page_data.shape[0]):
            # 去除值为 ’0‘ 或 nan 的行 
            if pandas.isnull(page_data.iloc[row, column]) or page_data.iloc[row, column] == '0':
                continue
            # 转换获取的数据的数据类型
            subject_number = front_name + str(row)
            report_date = datetime.datetime.strptime(str(page_data.iloc[0, column]), r'%Y%m%d').date()
            value = Decimal(page_data.iloc[row, column]).quantize(Decimal('0.00'))
            # 向一维数据表（list）添加数据
            origin_data.append([com_code, report_date, subject_number, value]) 

    # 将数据由 list 转为 dataframe 
    #standard_data_df = pandas.DataFrame(origin_data, columns=["公司代码", "报表日期", "项目编号","值"])

    print("数据处理完毕！")
    
    return [database_table_type, origin_data]


def get_corporation_information_from_SINA(com_code, statement_type_code='4'):
    """
    """
    
    ''' 根据报表编号确定报表类型、名称、数据库表类型以及科目前缀 '''
    if statement_type_code == '4':
        database_table_type = 'CI'
    else:
        print("报表类型选择错误，请重新选择！")
        return
    
    ''' 获取包含公司资料的网页，并下载数据 '''
    print("开始下载" + com_code + "的公司资料...")
    # 配置下载数据的 URL 
    url = 'https://vip.stock.finance.sina.com.cn/corp/go.php/vCI_CorpInfo/stockid/' + com_code + '.phtml'
    # 下载数据，所需的数据在 pandas 读取的页面的表格中的第 4 个中
    page_data = pandas.read_html(url)[3]
    print("数据下载完毕")
        
    ''' 将 dataframe 中的数据整理成字典，并转换数据类型 '''
    origin_data = {}
    origin_data['公司代码'] = com_code
    origin_data['公司名称'] = page_data.iloc[0, 1]
    origin_data['公司英文名称'] = page_data.iloc[1, 1]
    origin_data['上市市场'] = page_data.iloc[2, 1]
    origin_data['上市日期'] = datetime.datetime.strptime(str(page_data.iloc[2, 3]), r'%Y-%m-%d').date()
    origin_data['发行价格'] = Decimal(page_data.iloc[3, 1]).quantize(Decimal('0.00'))
    origin_data['主承销商'] = page_data.iloc[3, 3]
    origin_data['成立日期'] = datetime.datetime.strptime(str(page_data.iloc[4, 1]), r'%Y-%m-%d').date()
    origin_data['注册资本(万元)'] = Decimal(re.findall('\d+',page_data.iloc[4, 3])[0]).quantize(Decimal('0.00'))
    origin_data['机构类型'] = page_data.iloc[5, 1]
    origin_data['组织形式'] = page_data.iloc[5, 3]
    origin_data['董事会秘书'] = page_data.iloc[6, 1]
    origin_data['公司电话'] = page_data.iloc[6, 3]
    origin_data['董秘电话'] = page_data.iloc[8, 1]
    origin_data['公司传真'] = page_data.iloc[8, 3]
    origin_data['董秘传真'] = page_data.iloc[10, 1]
    origin_data['公司电子邮箱'] = page_data.iloc[10, 3]
    origin_data['董秘电子邮箱'] = page_data.iloc[12, 1]
    origin_data['公司网址'] = page_data.iloc[12, 3]
    origin_data['邮政编码'] = page_data.iloc[14, 1]
    origin_data['信息披露网址'] = page_data.iloc[14, 3]
    origin_data['证券简称更名历史'] = page_data.iloc[16, 1]
    origin_data['注册地址'] = page_data.iloc[17, 1]
    origin_data['办公地址'] = page_data.iloc[18, 1]
    origin_data['公司简介'] = page_data.iloc[19, 1]
    origin_data['经营范围'] = page_data.iloc[20, 1]
    
    ''' 清洗字典中的异常值 '''
    for key in origin_data:
        # 将空值替换为 ‘--’
        if pandas.isna(origin_data[key]):
            origin_data[key] = '--'
        # 将 '\r\n'、' '、'"'、"'"去除
        if isinstance(origin_data[key], str):
            origin_data[key] = origin_data[key].replace('\r\n', '')
            origin_data[key] = origin_data[key].replace(' ', '')
            origin_data[key] = origin_data[key].replace('"', '')
            origin_data[key] = origin_data[key].replace("'", '')

    print("数据处理完毕")

    return [database_table_type, [list(origin_data.values())]]


def get_issue_information_from_SINA(com_code, statement_type_code='5'):
    """
    """
    
    ''' 根据报表编号确定报表类型、名称、数据库表类型以及科目前缀 '''
    if statement_type_code == '5':
        database_table_type = 'II'
    else:
        print("报表类型选择错误，请重新选择！")
        return
    
    ''' 获取包含发行情况的网页，并下载数据 '''
    print("开始下载" + com_code + "的发行情况...")
    # 配置下载数据的 URL 
    url = 'https://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_NewStock/stockid/' + com_code + '.phtml'
    # 下载数据，所需的数据在 pandas 读取的页面的表格中的第 13 个中
    page_data = pandas.read_html(url)[12]
    print("数据下载完毕")


    ''' 将 dataframe 中的数据整理成字典，并转换数据类型 '''
    print("开始处理数据...")
    origin_data = {}
    origin_data['公司代码'] = com_code
    origin_data['上市地'] = page_data.iloc[0, 1]
    origin_data['主承销商'] = page_data.iloc[1, 1]
    origin_data['承销方式'] = page_data.iloc[2, 1]
    origin_data['上市推荐人'] = page_data.iloc[3, 1]
    origin_data['每股发行价(元)'] = Decimal(page_data.iloc[4, 1]).quantize(Decimal('0.00'))
    origin_data['发行方式'] = page_data.iloc[5, 1]
    origin_data['发行市盈率(按发行后总股本)'] = Decimal(page_data.iloc[6, 1]).quantize(Decimal('0.00'))
    origin_data['首发前总股本(万股)'] = Decimal(page_data.iloc[7, 1]).quantize(Decimal('0.00')) 
    origin_data['首发后总股本(万股)'] = Decimal(page_data.iloc[8, 1]).quantize(Decimal('0.00')) 
    origin_data['实际发行量(万股)'] = Decimal(page_data.iloc[9, 1]).quantize(Decimal('0.00'))
    origin_data['预计募集资金(万元)'] = Decimal(page_data.iloc[10, 1]).quantize(Decimal('0.00'))
    origin_data['实际募集资金合计(万元)'] = Decimal(page_data.iloc[11, 1]).quantize(Decimal('0.00'))
    origin_data['发行费用总额(万元)'] = Decimal(page_data.iloc[12, 1]).quantize(Decimal('0.00'))
    origin_data['募集资金净额(万元)'] = Decimal(page_data.iloc[13, 1]).quantize(Decimal('0.00'))
    origin_data['承销费用(万元)'] = Decimal(page_data.iloc[14, 1]).quantize(Decimal('0.00'))
    origin_data['招股公告日'] = datetime.datetime.strptime(str(page_data.iloc[15, 1]), r'%Y-%m-%d').date()
    origin_data['上市日期'] = datetime.datetime.strptime(str(page_data.iloc[16, 1]), r'%Y-%m-%d').date()
    
    ''' 清理字典中的异常值 (nan) '''
    for key in origin_data:  
        # 将空值替换为 ‘--’
        if pandas.isna(origin_data[key]):
            origin_data[key] = '--'
        # 将 '\r\n'、' '、'"'、"'"去除
        if isinstance(origin_data[key], str):
            origin_data[key] = origin_data[key].replace('\r\n', '')
            origin_data[key] = origin_data[key].replace(' ', '')
            origin_data[key] = origin_data[key].replace('"', '')
            origin_data[key] = origin_data[key].replace("'", '')

    print("数据处理完毕")

    return [database_table_type, [list(origin_data.values())]]


def sava_data_to_database(date_table):
    """ 保存数据至数据库

    创建数据库连接，打开数据库，并调用函数将数据存入 MySQL 数据库

    参数
    ----------
    date_table: list
        欲存入数据库的数据
        
    返回值
    -------
    无
    """

    ''' 创建数据库连接及游标 '''
    DB = pymysql.connect(
        host='127.0.0.1', 
        port=3306, 
        user='root', 
        passwd='330715', 
        db='FALC_pro')
    cursor = DB.cursor()
    
    ''' 将数据写入数据库 '''
    print("开始向数据库写入数据...")
    # 根据表格类型确定待写入数据的表名、字段名及字段值数量
    if date_table[0] == 'BS':
        table_name = 'financial_data'
        fileds = '公司代码, 报告日期, 项目编号, 值'
        field_values = r'%s, %s, %s, %s'
        data_type = "资产负债表"
    elif date_table[0] == 'PS':
        table_name = 'financial_data'
        fileds = '公司代码, 报告日期, 项目编号, 值'
        field_values = r'%s, %s, %s, %s'
        data_type = "利润表"
    elif date_table[0] == 'CF':
        table_name = 'financial_data'
        fileds = '公司代码, 报告日期, 项目编号, 值'
        field_values = r'%s, %s, %s, %s'
        data_type = "现金流量表"
    elif date_table[0] == 'CI':
        table_name = 'corporation_information'
        fileds = '公司代码, 公司名称, 公司英文名称, 上市市场, 上市日期, 发行价格, 主承销商, 成立日期, 注册资本(万元),  机构类型, \
            组织形式, 董事会秘书, 公司电话, 董秘电话, 公司传真, 董秘传真, 公司电子邮箱, 董秘电子邮箱, 公司网址, 邮政编码, \
            信息披露网址, 证券简称更名历史, 注册地址, 办公地址, 公司简介, 经营范围'
        field_values = r'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'
        data_type = "公司信息"
    elif date_table[0] == 'II':
            table_name = 'issue_information'
            fileds = '公司代码, 上市地, 主承销商, 承销方式, 上市推荐人, 每股发行价(元), 发行方式, 发行市盈率(按发行后总股本), 首发前总股本(万股), 首发后总股本(万股), \
                实际发行量(万股), 预计募集资金(万元), 实际募集资金合计(万元), 发行费用总额(万元), 募集资金净额(万元), 承销费用(万元), 招股公告日, 上市日期'
            field_values = r'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s'
            data_type = "发行信息"
        
    # 向数据库写入数据
    print("..." + data_type + "数据写入完毕")
    cursor.executemany(f"INSERT INTO { table_name }({ fileds }) VALUES ({ field_values })", date_table[1])

    """ 向数据库提交操作并关闭数据库连接 """
    DB.commit()
    DB.close()

    print("数据保存成功！")

    return


def download_listed_companies_data():
    """ 调用函数从股票网站下载上市公司数据

    根据提供的 download_list 参数，选择不同的爬虫函数从股票网站下载上市公司数据，并将清理格式后的数据存入数据库，
    同时将下载失败或保存失败的数据存入 problem_list.txt 文档中

    参数
    -------
    无
    -------
    无

    """

    ''' 启动下载时，用户选择下载方式 '''
    download_type = input("下载方式：\n 1 - 全局下载\n 2 - 清单下载\n 3 - 手工下载\n 请输入下载数据的方式：")

    # 用于保存待下载数据的公司的公司代码的 list
    download_list = []
    # 用于保存数据下载失败的公司的公司代码和报表类型的 list
    problem_list = []

    ''' 获取不存在的公司代码清单 '''
    not_exist_list = []
    with open("not_exist_list.txt", "r") as filetxt:
        for line in filetxt.readlines():
            # 去除字符串末尾的 ‘\n’，并追加至 not_exist_list 列表中
            not_exist_list.append(line.strip('\n'))


    ''' 根据选择的下载方式下载数据 '''
    # 全局下载
    if download_type == '1':
        download_range = input("下载范围：\n 1 - 创业板\n 2 - 科创板\n 请输入下载数据的范围：")

        # 生成待下载的公司代码清单
        if download_range == '1':
            for com_code in range(300001, 300999):
                if str(com_code) in not_exist_list:
                    continue
                download_list.append(str(com_code))
        elif download_range == '2':
            for com_code in range(688001, 688999):
                if str(com_code) in not_exist_list:
                    continue
                download_list.append(str(com_code))
        else:
            print("暂不支持的数据范围！")
            return
        
        # 生成待下载的报表类型清单
        statement_type = ['1','2','3','4','5']
        
        # 下载并保存数据
        for com_code in download_list:
            for statement_type_code in statement_type:
                # 根据待下载的数据类型调用函数
                try:
                    if statement_type_code == '4':
                        #sava_data_to_database(get_corporation_information_from_SINA(com_code, statement_type_code))
                        print(get_corporation_information_from_SINA(com_code, statement_type_code))
                    elif statement_type_code == '5':
                        #sava_data_to_database(get_issue_information_from_SINA(com_code, statement_type_code))
                        print(get_issue_information_from_SINA(com_code, statement_type_code))
                    else:
                        #sava_data_to_database(get_financial_data_from_SINA(com_code, statement_type_code))
                        print(get_financial_data_from_SINA(com_code, statement_type_code))
                except:
                    problem_list.append(com_code + ' ' + statement_type_code) 
                # 等待 2 秒
                time.sleep(2) 
                # 清除屏幕信息
                os.system('cls')

    # 清单下载
    elif download_type == '2':
        # 获取待下载数据的公司代码清单
        with open("download_list.txt", "r") as filetxt:
            for line in filetxt.readlines():
                if line[0] == '#':
                    continue
                # 去除字符串末尾的 ‘\n’，并按 ‘ ’ 将字符串切分成 list， 然后追加至 download_list 列表中
                download_list.append(line.strip('\n').split(' '))
        
        # 下载并保存数据
        for item in download_list:
            # 检查待下载数据的公司是否存在，如该公司代码在 not_exist_list 中，则跳过
            if item[0] in not_exist_list:
                continue
            # 根据待下载的数据类型调用函数
            try:
                if item[1] == '4':
                    #sava_data_to_database(get_corporation_information_from_SINA(item[0], item[1]))
                    print(get_corporation_information_from_SINA(item[0], item[1]))
                elif item[1] == '5':
                    #sava_data_to_database(get_issue_information_from_SINA(item[0], item[1]))
                    print(get_issue_information_from_SINA(item[0], item[1]))
                else:
                    #sava_data_to_database(get_financial_data_from_SINA(item[0], item[1]))
                    print(get_financial_data_from_SINA(item[0], item[1]))
            except:
                problem_list.append(item[0] + ' ' + item[1]) 
            # 等待 2 秒
            time.sleep(10) 
            # 清除屏幕信息
            os.system('cls')
    
    # 手工下载
    elif download_type == '3':
        continue_or_not = True
        while continue_or_not:
            com_code = input("请输入待下载报表的单位的公司代码：")
            statement_type_code = input("报表类型：\n 1 - 资产负债表\n 2 - 利润表\n 3 - 现金流量表\n 4 - 公司资料\n 5 - 发行情况\n 请输入需下载的报表编号：")
        
            if statement_type_code == '4': 
                #sava_data_to_database(get_corporation_information_from_SINA(com_code, statement_type_code))
                print(get_corporation_information_from_SINA(com_code, statement_type_code))
            elif statement_type_code == '5': 
                #sava_data_to_database(get_issue_information_from_SINA(com_code, statement_type_code))
                print(get_issue_information_from_SINA(com_code, statement_type_code))
            else:
                #sava_data_to_database(get_financial_data_from_SINA(com_code, statement_type_code))
                print(get_financial_data_from_SINA(com_code, statement_type_code))

            is_continue = input("是否继续（y/n)：")
            if is_continue == 'n' or is_continue == 'N':
                continue_or_not = False

            os.system('cls')
    
    ''' 保存数据下载失败的公司的公司代码和报表类型 '''
    with open("problem_list.txt", 'w') as filetxt:
        for item in problem_list:
            filetxt.write(item + '\n')