from views import *


if __name__ == '__main__':
    """ 获取待下载数据的公司代码清单 """
    download_list = []
    with open("download_list.txt", "r") as filetxt:
        for line in filetxt.readlines():
            # 去除字符串末尾的 ‘\n’，并按 ‘ ’ 将字符串切分成 list， 然后追加至 download_list 列表中
            download_list.append(line.strip('\n').split(' '))

    """ 下载数据 """
    download_data(download_list)

    """ 检查数据 """
    check_list()
