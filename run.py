# -*- coding: utf-8 -*-
import getopt
import sys
from lib.NacosClass import NacosClass


def useage():
    print("%s -f\t#执行文件" % sys.argv[0])
    print("%s -h\t#帮助文档" % sys.argv[0])


def main():
    if len(sys.argv) == 1:
        useage()
        sys.exit()
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "f:h"
        )
    except getopt.GetoptError:
        print("%s -h" % sys.argv[0])
        sys.exit(1)
    command_dict = dict(options)
    command_data = dict()
    # 帮助
    if '-h' in command_dict:
        useage()
        sys.exit()
    # 获取监控项数据
    elif "-f" in command_dict:
        command_data['achieve'] = command_dict.get('-f')
        sql_data = command_data['achieve'].split("#")
        if sql_data[1] == 'nacos':
            ff = NacosClass()
            ff.run(zipfile=sql_data)
        else:
            print("error input file")
            sys.exit(1)
    else:
        useage()
        sys.exit(1)


if __name__ == '__main__':
    main()
