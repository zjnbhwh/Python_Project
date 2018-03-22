#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'hewenhui'
from base import ABCRelease
from base import Ssh
import configparser
import pysvn
from urllib import parse
import os
import json


class SVN_HEC(ABCRelease.ABCRelease):
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("../resource/system.ini")
        super(SVN_HEC, self).__init__("hec")

    def get_diff_file(self, min, max):
        targetPath = self.release_svn_dir + self.date_file
        client = pysvn.Client()
        revision_max = pysvn.Revision(pysvn.pysvn.opt_revision_kind.number, max)
        revision_min = pysvn.Revision(pysvn.pysvn.opt_revision_kind.number, min)
        self.change = client.diff_summarize(self.url, revision_max, self.url, revision_min)
        for changed in self.change:
            try:
                self.logger.info("从SVN下载：" + changed['path'])
                file_text = client.cat(self.url + parse.quote(changed['path'].encode('utf8')), revision_max)
                fullpath = targetPath + "/" + changed["path"]
                dirpath = fullpath[0:fullpath.rfind("/")]
                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)
                with open(fullpath, "wb") as f:
                    f.write(file_text)
            except:
                print("error:" + parse.quote(changed['path'].encode('utf8')))
                continue
        return targetPath

    def get_release(self):
        print("release")

    def buildFileGroup(self, releaseFiles):
        files = []
        for f in releaseFiles:
            files.append({"sourceFile": f,
                          "targetFile": f.replace(self.release_dir + self.date_file,
                                                  "/bea/hec/release/hec/" + self.date_file)})

        return files


if __name__ == "__main__":
    hec = SVN_HEC()
    hec.logger.info("####################开始########################" + hec.date_file)
    hec.update()
    min = input("请输入起始版本号：")
    max = input("请输入终止版本号：")

    hec.logger.info("始版本号：" + min)
    hec.logger.info("终止版本号：" + max)
    # 获得svn文件
    hec.logger.info("获得发布文件")
    releasePath = hec.get_diff_file(min, max)
    hec.logger.info("将svn获得的文件拷贝到工程")
    hec.copyFiles(releasePath, hec.base_dir)
    hec.logger.info("获得发布文件名")
    releaseFiles = []
    hec.get_release_files(hec.release_dir + hec.date_file, releaseFiles)

    files = hec.buildFileGroup(releaseFiles)

    with open('E:/工作/project/Python_Project/resource/hec_servers.json') as json_file:
        configs = json.load(json_file)
    for config in configs:
        hec.logger.info("开始上传发布包到服务器：" + config["ip"])
        ssh = Ssh.SshUtil(config["ip"], config["port"], config["username"], config["password"])
        ssh.sftp_uploadFile(files, config["mkdirs"])
        hec.logger.info("将服务器上的发布包发布到项目，并备份")
        ssh.release(config["release"], hec.date_file)
        ssh.ssh.close()
        hec.logger.info("上传服务器：" + config["ip"] + "结束")

    hec.logger.info("####################结束#########################" + hec.date_file)
