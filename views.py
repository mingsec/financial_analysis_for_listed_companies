import pandas
import requests
import pymysql
from bs4 import BeautifulSoup
from lxml import etree


def get_financial_statement(statement_type_code, com_code):
    """从163股票网站下载特定单位的财务报表,同时对下载的财务报表进行数据清洗，并转成一维数据
    参数
    ----------
    statement_type_code: int
        可供下载的报表类：1 - 资产负债表； 2 - 利润表； 3 - 现金流量表； 4 - 公司资料
    com_code: int
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
        database_table_type = 'FD'
        front_name = 'BS-'
    elif statement_type_code == '2':
        statement_type = 'lrb'
        statement_name = '利润表'
        database_table_type = 'FD'
        front_name = 'PL-'
    elif statement_type_code == '3':
        statement_type = 'xjllb'
        statement_name = '现金流量表'
        database_table_type = 'FD'
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
    SQL_FD = "INSERT INTO financial_data(公司代码, 报告日期, 科目名称, 值) VALUES ('%s','%s','%s','%s')"
    # 配置 company_information 表更新 SQL 语句 
    SQL_CI = "INSERT INTO company_information(公司代码, 组织形式, 地域, 中文简称, 办公地址,\
                                              公司全称, 公司电话, 英文名称, 公司电子邮箱, 注册资本,\
                                              董事长, 员工人数, 董事会秘书, 法人代表, 董秘电话,\
                                              总经理, 董秘传真, 公司网址, 董秘邮箱, 信息披露网址,\
                                              信息披露报纸名称, 主营业务, 经营范围, 公司沿革) VALUES ('%s', '%s', '%s', '%s', '%s',\
                                                                                                  '%s', '%s', '%s', '%s', '%s',\
                                                                                                  '%s', '%s', '%s', '%s', '%s',\
                                                                                                  '%s', '%s', '%s', '%s', '%s',\
                                                                                                  '%s', '%s', '%s', '%s')"
    # 配置 IPO_information 表更新 SQL 语句 
    SQL_II = "INSERT INTO IPO_information(公司代码, 成立日期, 上市日期, 发行方式, 面值,\
                                          发行数量, 发行价格, 募资资金总额, 发行费用, 发行中签率,\
                                          发行市盈率, 发行后每股收益, 发行后每股净资产, 上市首日开盘价, 上市首日收盘价,\
                                          上市首日换手率, 主承销商, 上市保荐人, 会计师事务所) VALUES ('%s', '%s', '%s', '%s', '%s',\
                                                                                                  '%s', '%s', '%s', '%s', '%s',\
                                                                                                  '%s', '%s', '%s', '%s', '%s',\
                                                                                                  '%s', '%s', '%s', '%s')"
    # 配置 board_of_directors 表更新 SQL 语句 
    SQL_BD = "INSERT INTO board_of_directors(公司代码, 更新日期, 姓名, 职务, 起止时间, 持股数_万股, 报酬_元) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')"
    # 配置 revenue_data 表更新 SQL 语句 
    SQL_RD = "INSERT INTO revenue_data(公司代码, 报告日期, 分类维度, 分类名称, 收入_万元, 成本_万元, 利润_万元, 毛利率, 利润占比) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
    # 配置 employees_data 表更新 SQL 语句 
    SQL_ED = "INSERT INTO employees_data(公司代码, 报告日期, 分类维度, 分类名称, 员工人数, 员工占比) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"

    """ 创建数据库连接及游标 """
    FADB = pymysql.connect(
        host='88.88.4.123', 
        port=3306, 
        user='root', 
        passwd='330715', 
        db='financial_analysis_of_listed_companies')
    cursor = FADB.cursor()
    
    #将数据写入数据库
    for table in date_tables:
        table_type = table[0]
        data = table[1]

        if table_type == 'FD':
            SQL = SQL_FD
            data_type = "财务数据"
        elif table_type == 'CI':
            SQL = SQL_CI
            data_type = "公司信息数据"
        elif table_type == 'II':
            SQL = SQL_II
            data_type = "IPO信息数据"
        elif table_type == 'BD':
            SQL = SQL_BD
            data_type = "董事会成员信息数据"
        elif table_type == 'RD':
            SQL = SQL_RD
            data_type = "收入数据"
        elif table_type == 'ED':
            SQL = SQL_ED
            data_type = "职工数据"
        
        print("开始向数据库写入" + data_type + "...")
        if table_type == 'CI' or table_type == 'II':
            cursor.executemany(SQL, data)
        else:
            for item in data:
                cursor.executemany(SQL, item)

    #向数据库提交操作并关闭数据库连接
    FADB.commit()
    FADB.close()
    print("数据保存成功！")


def get_enterprise_information(statement_type_code, com_code):
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

    enterprise_information =[]

    """ 处理公司信息数据 """
    print("开始处理公司信息数据...")
    company_information = [com_code]
    # 以str类型（decode()）输出（tostring(））修正后的HTML代码
    company_information_table = etree.tostring(tables_one[0], encoding='utf-8').decode()
    # 获取公司信息表格中的数据
    company_information_df = pandas.read_html(company_information_table, encoding='utf-8', header=None)[0]
    for i in range(0, 10):
        company_information.append(company_information_df.iloc[i, 1])
        company_information.append(company_information_df.iloc[i, 3])
    for i in range(10, company_information_df.shape[0]):
        company_information.append(company_information_df.iloc[i, 1])
    # 去除数据中的异常字符
    for i in range(1, len(company_information)):
        # 将空值替换为 “--”
        if company_information[i] == '\n' or  company_information[i] == None or  company_information[i] == '' or company_information[i] == 'nan':
            company_information[i] = '--'
        # 删除单元格中的空格 ' ' 和 '\r\n' ,将 “"” 和 “'” 等替换为空格 “ ”
        if isinstance(company_information[i], str):
            company_information[i] = company_information[i].replace(' ', '')
            company_information[i] = company_information[i].replace('\r\n', '')
            company_information[i] = company_information[i].replace('"', ' ')
            company_information[i] = company_information[i].replace("'", ' ')
    enterprise_information.append(['CI', [company_information]])
    print("公司信息数据处理完毕！")

    """ 处理IPO信息数据 """
    print("开始处理IPO信息数据...")
    IPO_information = [com_code]
    # 以str类型（decode()）输出（tostring(））修正后的HTML代码
    IPO_information_table = etree.tostring(tables_one[1], encoding='utf-8').decode()
    # 获取 IPO 信息表格中的数据
    IPO_information_df = pandas.read_html(IPO_information_table, encoding='utf-8', header=None)[0]
    for i in range(0, IPO_information_df.shape[0]):
        IPO_information.append(IPO_information_df.iloc[i,1])
    # 去除数据中的异常字符
    for i in range(1, len(IPO_information)):
        # 将空值替换为 “--”
        if IPO_information[i] == '\n' or IPO_information[i] == None or IPO_information[i] == '' or IPO_information[i] == 'nan':
            IPO_information[i] = '--'
        # 删除单元格中的空格 ' ' 和 '\r\n'
        if isinstance(IPO_information[i], str):
            IPO_information[i] = IPO_information[i].replace(' ', '')
            IPO_information[i] = IPO_information[i].replace('\r\n', '')
    enterprise_information.append(['II', [IPO_information]])
    print("IPO信息数据处理完毕！")
    
    """ 处理董事会成员信息数据 """
    print("开始处理董事会成员信息数据...")
    board_of_directors = []
    # 以str类型（decode()）输出（tostring(））修正后的HTML代码
    board_of_directors_table = etree.tostring(tables_two[0], encoding='utf-8').decode()
    # 获取董事会成员信息表格中的数据
    board_of_directors_df = pandas.read_html(board_of_directors_table, encoding='utf-8', header=None)[0]
    for i in range(0, board_of_directors_df.shape[0]):
        board_of_directors.append([com_code, last_update_date] + list(board_of_directors_df.iloc[i]))
    # 去除数据中的异常字符   
    for i in range(0, len(board_of_directors)):
        for j in range(0, len(board_of_directors[i])):
            # 将空值替换为 “--”
            if board_of_directors[i][j] == '\n' or board_of_directors[i][j] == None or board_of_directors[i][j] == '' or board_of_directors[i][j] == 'nan':
                board_of_directors[i][j] = '--'
            # 删除单元格中的空格 ' ' 和 '\r\n'
            if isinstance(board_of_directors[i][j], str):
                board_of_directors[i][j] = board_of_directors[i][j].replace(' ', '')
                board_of_directors[i][j] = board_of_directors[i][j].replace('\r\n', '')
    enterprise_information.append(['BD', board_of_directors])
    print("董事会成员信息数据处理完毕！")

    """ 收入数据 """
    print("开始处理收入数据...")
    revenue_data = []
    for i in range(1, 4):
        # 以str类型（decode()）输出（tostring(））修正后的HTML代码
        revenue_data_table = etree.tostring(tables_two[i], encoding='utf-8').decode()
        # 获取收入数据表格中的数据
        revenue_data_df = pandas.read_html(revenue_data_table, encoding='utf-8', header=None)[0]
        table_type = revenue_data_df.columns[0]
        for i in range(0, revenue_data_df.shape[0]):
            revenue_data.append([com_code, report_date, table_type] + list(revenue_data_df.iloc[i]))
    # 去除数据中的异常字符   
    for i in range(0, len(revenue_data)):
        for j in range(0, len(revenue_data[i])):
            # 将空值替换为 “--”
            if revenue_data[i][j] == '\n' or revenue_data[i][j] == None or revenue_data[i][j] == '' or revenue_data[i][j] == 'nan':
                revenue_data[i][j] = '--'
            # 删除单元格中的空格 ' ' 和 '\r\n'.
            if isinstance(revenue_data[i][j], str):
                revenue_data[i][j] = revenue_data[i][j].replace(' ', '')
                revenue_data[i][j] = revenue_data[i][j].replace('\r\n', '')
    enterprise_information.append(['RD', revenue_data])
    print("收入数据处理完毕！")

    """ 处理人员数据 """
    print("开始处理人员数据...")
    employees_data = []
    for i in range(4, len(tables_two)):
        # 以str类型（decode()）输出（tostring(））修正后的HTML代码
        employees_data_table = etree.tostring(tables_two[i], encoding='utf-8').decode()
        # 获取收入数据表格中的数据
        employees_data_df = pandas.read_html(employees_data_table, encoding='utf-8', header=None)[0]
        table_type = employees_data_df.columns[0]
        for i in range(0, employees_data_df.shape[0]):
            employees_data.append([com_code, report_date, table_type] +  list(employees_data_df.iloc[i]))
    # 去除数据中的异常字符   
    for i in range(0, len(employees_data)):
        for j in range(0, len(employees_data[i])):
            # 将空值替换为 “--”
            if employees_data[i][j] == '\n' or employees_data[i][j] == None or employees_data[i][j] == '' or employees_data[i][j] == 'nan':
                employees_data[i][j] = '--'
            # 删除单元格中的空格 ' ' 和 '\r\n'.
            if isinstance(employees_data[i][j], str):
                employees_data[i][j] = employees_data[i][j].replace(' ', '')
                employees_data[i][j] = employees_data[i][j].replace('\r\n', '')
    enterprise_information.append(['ED', employees_data])
    print("人员数据处理完毕！")

    return enterprise_information