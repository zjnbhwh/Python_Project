#!/usr/bin/env python
# -*- coding: utf-8 -*-
#功能：从svn抓发布包，本地编译后，增量发布到服务器
#

__author__ = 'hewenhui'
from base import ABCRelease
from base import Ssh
import configparser
import pysvn
from urllib import parse
import os
import json


class SVN_MI(ABCRelease.ABCRelease):
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("../resource/system.ini")
        #本地编译后的class路径
        self.class_dir = cf.get(r"%s" % "mi", "class_dir")
        super(SVN_MI, self).__init__("mi")
    #该方法目前只处理了新增或修改的发布
    def get_diff_file(self, min, max):
        targetPath = self.release_svn_dir + self.date_file
        client = pysvn.Client()
        revision_max = pysvn.Revision(pysvn.pysvn.opt_revision_kind.number, max)
        revision_min = pysvn.Revision(pysvn.pysvn.opt_revision_kind.number, min)
        self.change = client.diff_summarize(self.url, revision_min, self.url, revision_max)
        for changed in self.change:
            try:
                if pysvn.diff_summarize_kind.added == changed['summarize_kind'] or pysvn.diff_summarize_kind.modified == \
                        changed['summarize_kind']:
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
        self.logger.info("将编译后的文件，按差异提取到：" + self.release_dir)
        release = []
        for changed in self.change:
            if pysvn.diff_summarize_kind.added == changed['summarize_kind'] or pysvn.diff_summarize_kind.modified == \
                    changed['summarize_kind']:
                f = changed["path"]
                if f.startswith("mi/src/test"):
                    continue
                if f.startswith("mi/src/main"):

                    if f.endswith(".java"):
                        f = f.replace("mi/src/main/java", "")
                        temp = f[f.rfind("/") + 1:]
                        className = temp[0:temp.rfind(".")]
                        pathName = f[0:f.rfind("/") + 1]
                        pathName = r"%s%s%s" % (self.base_dir, self.class_dir, pathName)
                        for f in self.get_classFile(pathName, className):
                            filePath = f.replace("D:/source_project/MI/mi/webapp/WEB-INF/classes/", "")

                            targetDir = self.release_dir + self.date_file + "/WEB-INF/classes/" + filePath[
                                                                                                  0:filePath.rfind("/")]
                            targetFile = targetDir + filePath[filePath.rfind("/"):]

                            if not os.path.exists(targetDir):
                                os.makedirs(targetDir)
                            with open(targetFile, "wb") as file:
                                try:
                                    file.write(open(f, 'rb').read())
                                except Exception as e:
                                    print("错误："+f)
                                    print(e)
                            release.append(targetFile)
                    else:
                        if f.startswith("mi/src/main/java"):
                            f = f.replace("mi/src/main/java", "")
                        else:
                            f = f[f.rfind("/"):]

                        sourceFile = r"%s%s%s" % (self.base_dir, self.class_dir, f)

                        if os.path.isfile(sourceFile):
                            targetDir = self.release_dir + self.date_file + "/WEB-INF/classes" + f[0:f.rfind("/")]

                            targetFile = targetDir + f[f.rfind("/"):]
                            if not os.path.exists(targetDir):
                                os.makedirs(targetDir)
                            with open(targetFile, "wb") as file:
                                file.write(open(sourceFile, 'rb').read())
                            release.append(targetFile)
                else:
                    sourceFile = r"%s%s" % (self.base_dir, f)
                    if os.path.isfile(sourceFile):
                        # 截掉Web Root目录
                        f = f.replace("mi/webapp", "")
                        targetDir = self.release_dir + self.date_file + f[0:f.rfind("/")]
                        targetFile = targetDir + f[f.rfind("/"):]
                        if not os.path.exists(targetDir):
                            os.makedirs(targetDir)
                        with open(targetFile, "wb") as file:
                            file.write(open(sourceFile, "rb").read())
                        release.append(targetFile)
        return release

    def build(self):
        os.chdir("E:/工作/project/Python_Project/resource")
        os.system("ant -f %s" % "mi_build.xml")

    def buildFileGroup(self, releaseFiles):
        files = []
        for f in releaseFiles:
            files.append({"sourceFile": f,
                          "targetFile": f.replace(self.release_dir + self.date_file,
                                                  "/app/new_release/mi/" + self.date_file)})

        return files


if __name__ == "__main1__":
    mi = SVN_MI()
    mi.logger.info("####################开始########################" + mi.date_file)
    # mi.update()
    # min = input("请输入起始版本号：")
    # max = input("请输入终止版本号：")
    min = "2254"
    max = "2260"
    mi.logger.info("始版本号：" + min)
    mi.logger.info("终止版本号：" + max)
    # 获得svn文件,并返回存放路径
    svnPath = mi.get_diff_file(min, max)

    mi.logger.info("####################结束#########################" + mi.date_file)

if __name__ == "__main__":
    mi = SVN_MI()
    mi.logger.info("####################开始########################" + mi.date_file)
    mi.update()
    min = input("请输入起始版本号：")
    max = input("请输入终止版本号：")

    mi.logger.info("始版本号：" + min)
    mi.logger.info("终止版本号：" + max)
    # 获得svn文件,并返回存放路径
    svnPath = mi.get_diff_file(min, max)
    #将svn文件拷贝到工程并备份
    mi.copyFiles(svnPath, mi.base_dir)
    #编译工程
    mi.build()
    #按差异将编译后的文件拷贝到发布目录
    releaseFiles = mi.get_release()
    #组织发布到服务器的二维数组
    files = mi.buildFileGroup(releaseFiles)
    #读取服务器配置
    with open('E:/工作/project/Python_Project/resource/mi_servers.json') as json_file:
        configs = json.load(json_file)
    for config in configs:
        mi.logger.info("开始上传发布包到服务器：" + config["ip"])
        ssh = Ssh.SshUtil(config["ip"], config["port"], config["username"], config["password"])
        ssh.sftp_uploadFile(files, config["mkdirs"])
        mi.logger.info("将服务器上的发布包发布到项目，并备份")
        ssh.release(config["release"], mi.date_file)
        ssh.ssh.close()
        mi.logger.info("上传服务器：" + config["ip"] + "结束")

    mi.logger.info("####################结束#########################" + mi.date_file)
