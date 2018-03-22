#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import pysvn
import time
import os
from abc import ABC, abstractmethod
from urllib import parse
import logging
import logging.config

import glob


class ABCRelease(ABC):
    # 初始化
    def __init__(self, project):
        cf = configparser.ConfigParser()
        cf.read("../resource/system.ini")
        logging.config.fileConfig("../resource/logging.conf")
        logger_name = project
        self.logger = logging.getLogger(logger_name)
        self.project = project
        self.release_svn_dir = cf.get(r"%s" % self.project, "release_svn_dir")
        self.url = cf.get(r"%s" % self.project, "url")
        self.base_dir = cf.get(r"%s" % self.project, "base_dir")
        self.release_dir = cf.get(r"%s" % self.project, "release_dir")
        self.release_back_dir = cf.get(r"%s" % self.project, "release_back_dir")
        self.date_file = time.strftime(r"%Y%m%d%H%M%S", time.localtime())

    # 检出svn
    def checkout(self, versionNum):
        client = pysvn.Client()
        pysvn.Revision(pysvn.pysvn.opt_revision_kind.number, versionNum)
        client.checkout(self.svn_url, self.base_dir)

    # 更新svn版本库
    def update(self):
        client = pysvn.Client()
        client.update(self.base_dir)

    # 获得版本之间的差异文件
    @abstractmethod
    def get_diff_file(self, min, max):
        pass

    # 备份工程
    def backup(self, sourceDir, backupDir):
        targetF = sourceDir.replace(self.base_dir, backupDir + self.date_file + "/")
        sourceF = sourceDir[0:sourceDir.rfind("\\")]
        targetDir = sourceF.replace(self.base_dir, backupDir + self.date_file + "/")
        if not os.path.exists(targetDir):
            os.makedirs(targetDir)
        with open(targetF, 'wb') as f:
            f.write(open(sourceDir, 'rb').read())

    # 将待发布的文件拷贝到工程
    def copyFiles(self, sourceDir, targetDir):
        for f in os.listdir(sourceDir):
            sourceF = os.path.join(sourceDir, f)
            targetF = os.path.join(targetDir, f)
            if os.path.isfile(sourceF):
                if not os.path.exists(targetDir):
                    os.makedirs(targetDir)
                if not os.path.exists(targetF):
                    with open(targetF, "wb") as f:
                        f.write(open(sourceF, "rb").read())
                else:
                    self.backup(targetF, self.release_back_dir)
                    with open(targetF, "wb") as f:
                        f.write(open(sourceF, "rb").read())
            if os.path.isdir(sourceF):
                self.copyFiles(sourceF, targetF)

    # 获得发布文件
    @abstractmethod
    def get_release(self):
        pass

    # 获得待发布的文件名

    def get_release_files(self, path, release_files):
        if os.path.isdir(path):
            for f in os.listdir(path):
                sourceFile = path + "/" + f
                if os.path.isdir(sourceFile):
                    self.get_release_files(sourceFile, release_files)
                elif os.path.isfile(sourceFile):
                    release_files.append(sourceFile)

    @staticmethod
    #glob 文件路径查找
    def get_classFile(path, ext):
        for i in glob.glob(path+ext+"$*.class"):
            yield i.replace("\\","/")
        yield os.path.join(path, ext+".class")

if __name__ == '__main2__':
    # 初始化环境变量
    for i in ABCRelease.get_classFile("D:/source_project/MI/mi/webapp/WEB-INF/classes/cn/com/sinatay/portal/service/impl/",
                             "SendRequestServiceImpl"):
        print(i)

if __name__ == '__main__':
    # 初始化环境变量
    ABCRelease('identity')

