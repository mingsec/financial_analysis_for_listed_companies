from views import *

import os
import time

if __name__ == '__main__':
    
    yes_or_no = True
    while yes_or_no:
        com_code = input("请输入待下载报表的单位的公司代码：")
        statement_type_code = input("报表类型：\n 1 - 资产负债表\n 2 - 利润表\n 3 - 现金流量表\n 4 - 公司资料\n 请输入需下载的报表编号：")
        
        if int(statement_type_code)  == 4 :
            # write_data_to_database(get_enterprise_information(statement_type_code, com_code))
            tables = get_enterprise_information(statement_type_code, com_code)
        else:
            # write_data_to_database(get_financial_statement(statement_type_code, com_code))
            tables = get_financial_statement(statement_type_code, com_code)
        
        for table in tables:
            print(table[0] + "的内容如下：")
            print(table[1])
            print("======")
            
        is_continue = input("是否继续（y/n)：")
        if is_continue == 'n' or is_continue == 'N':
            yes_or_no = False

        os.system('cls')



    '''

    old_list = []
    new_list = []
    
    with open("list.txt", "r") as filetxt:
        for line in filetxt.readlines():
            old_list.append(line.strip('\n'))

    statement_type_code = '4'

    for com_code in old_list:  #range(688001,688601):
        try:
            write_data_to_database(get_enterprise_information(statement_type_code, com_code))
            #time.sleep(5)
            os.system('cls')
        except Exception as e:
            new_list.append(com_code)

    with open("new_list.txt", "w") as filetxt:
        for item in new_list:
            filetxt.write(str(item)+"\n")
    '''
    