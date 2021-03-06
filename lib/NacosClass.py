# -*- coding: utf-8 -*-
import nacos
from lib.Log import RecodeLog
from lib.lftp import FTPBackupForDB
from lib.settings import BACKUP_DIR, NACOS_CONFIG
import os
import glob
import platform
import yaml
import shutil


def cmd(cmd_str):
    """
    :param cmd_str:
    :return:
    """
    if int(platform.python_version().strip(".")[0]) < 3:
        import commands

        exec_proc = commands
    else:
        import subprocess

        exec_proc = subprocess
    try:
        status, output = exec_proc.getstatusoutput(cmd_str)
        if status != 0:
            raise Exception(output)
        RecodeLog.info("执行:{0},成功!".format(cmd_str))
        return True
    except Exception as error:
        RecodeLog.error(msg="执行:{0},失败，原因:{1}".format(cmd_str, error))
        return False


class NacosClass:
    def __init__(self):
        self.nacos = None
        self.ftp = FTPBackupForDB(db='nacos')
        self.ftp.connect()
        self.backup_dir = BACKUP_DIR

    def upload_config(self, yaml_achieve, config_type):
        """
        :param yaml_achieve:
        :param config_type:
        :return:
        """
        if not os.path.exists(yaml_achieve):
            RecodeLog.error(msg="文件不存在:{}".format(yaml_achieve))
            return False
        data = yaml_achieve.split(os.sep)
        try:
            with open(yaml_achieve, 'r') as fff:
                load_dict = yaml.load_all(fff, Loader=yaml.Loader)
                self.nacos.publish_config(
                    content=yaml.dump_all(
                        load_dict,
                        allow_unicode=True
                    ),
                    config_type=config_type,
                    timeout=30,
                    data_id=data[-1],
                    group=data[-2]
                )
                return True
        except Exception as error:
            RecodeLog.error(msg="上传配置失败:{}".format(error))
            return False

    def connect_nacos(self, content, namespace=''):
        """
        :param content:
        :param namespace:
        :return:
        """
        if not isinstance(content, dict):
            RecodeLog.error(msg="选择模板错误：{}！".format(content))
            return False
        try:
            if content['port'] == 443:
                address = 'https://{}:{}'.format(content['host'], content['port'])
            else:
                address = 'http://{}:{}'.format(content['host'], content['port'])
            self.nacos = nacos.NacosClient(
                address,
                namespace=namespace,
                username=content['user'],
                password=content['passwd']
            )
            return True
        except Exception as error:
            RecodeLog.error(msg="登录验证失败,{}".format(error))
            return False

    def run(self, zipfile):
        """
        :param zipfile:
        :return:
        """
        name, extension = os.path.splitext(zipfile)
        if extension != '.zip':
            RecodeLog.error(msg="文件类型错误:{}".format(zipfile))
            return False
        sql_data = name.split("#")
        if not self.connect_nacos(
                content=NACOS_CONFIG[sql_data[2]]
        ):
            return False
        self.ftp.download(remote_path=sql_data[2], local_path=self.backup_dir, achieve=zipfile)
        if os.path.exists(os.path.join(self.backup_dir, name)):
            shutil.rmtree(path=os.path.join(self.backup_dir, name))
        unzip_shell_string = 'unzip {} -d {} '.format(
            os.path.join(self.backup_dir, zipfile),
            os.path.join(self.backup_dir, name)
        )
        if not cmd(cmd_str=unzip_shell_string):
            RecodeLog.error(msg="解压文件失败：{}".format(unzip_shell_string))
            return False
        yaml_list = glob.glob(os.path.join(self.backup_dir, name, "*", "*.yaml"))
        if not yaml_list:
            RecodeLog.warn(msg="导入配置文件为空,请检查！")
            return True
        for yml in yaml_list:
            if not self.upload_config(yaml_achieve=yml, config_type='yaml'):
                RecodeLog.error(msg="导入相关配置失败")
                return False
        return True
