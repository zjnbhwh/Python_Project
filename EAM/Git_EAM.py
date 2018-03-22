#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'hewenhui'
from base import ABCRelease
from base import Ssh
import configparser
import os
import json


class Git_EAM(ABCRelease.ABCRelease):
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("../resource/system.ini")
        self.class_dir = cf.get(r"%s" % "eam", "class_dir")
        super(Git_EAM, self).__init__("eam")

    def get_diff_file(self, min, max):
        self.change = []
        os.chdir(self.base_dir)
        os.system("git reset --hard HEAD")
        # changes = os.system("git diff %s %s --name-only|xargs zip update.zip " % (min, max))
        out = os.popen(
            "git diff --binary %s %s --name-only ./eam " % (min, max))
        for i in out.readlines():
            filename = i.strip('\n')
            self.logger.info("文件" + filename + "下载到工程")
            os.system("git checkout %s %s" % (max, filename))
            self.change.append(filename)

        return self.change

    def get_release(self):
        release = self.__get_git_release()
        return release

    def __get_svn_release(self):
        self.logger.info("将编译后的文件，按差异提取到：" + self.release_dir)
        release = []
        for changed in self.change:
            f = changed["path"]

            if f.endswith(".java"):
                f = f.replace(".java", ".class", 1)
                f = f[f.find("/"):]
                if not f.endswith(".class"):
                    self.logger.error("出错！")
                    break
                sourceFile = r"%s%s%s" % (self.base_dir, self.class_dir, f)
                print(sourceFile)
                targetDir = self.release_dir + self.date_file + "/WEB-INF/classes" + f[0:f.rfind("/")]
                targetFile = targetDir + f[f.rfind("/"):]
                if not os.path.exists(targetDir):
                    os.makedirs(targetDir)
                with open(targetFile, "wb") as file:
                    file.write(open(sourceFile, 'rb').read())
                release.append(targetFile)
            else:
                sourceFile = r"%s%s" % (self.base_dir, f)
                # 截掉Web Root目录
                f = f[f.find("/"):]
                targetDir = self.release_dir + self.date_file + f[0:f.rfind("/")]
                targetFile = targetDir + f[f.rfind("/"):]
                if not os.path.exists(targetDir):
                    os.makedirs(targetDir)
                with open(targetFile, "wb") as file:
                    file.write(open(sourceFile, "rb").read())
                release.append(targetFile)

        return release

    def __get_git_release(self):
        release = []
        for f in self.change:
            if f.startswith("eam/JavaSource/src"):
                if f.endswith(".java"):
                    f = f.replace(".java", ".class", 1)
                f = f.replace("eam/JavaSource/src", "")
                sourceFile = r"%s%s%s" % (self.base_dir, "eam/" + self.class_dir, f)
                targetDir = self.release_dir + self.date_file + "/WEB-INF/classes" + f[0:f.rfind("/")]
                targetFile = targetDir + f[f.rfind("/"):]
                if not os.path.exists(targetDir):
                    os.makedirs(targetDir)
                with open(targetFile, "wb") as file:
                    self.logger.info("将源文件" + sourceFile + "提取到：" + targetFile)
                    file.write(open(sourceFile, 'rb').read())
                release.append(targetFile)
            elif f.startswith("eam/JavaSource/resources"):
                    f = f.replace("eam/JavaSource/resources", "")
                    print("f"+f)
                    sourceFile = r"%s%s%s" % (self.base_dir, "eam/" + self.class_dir, f)
                    targetDir = self.release_dir + self.date_file + "/WEB-INF/classes" + f[0:f.rfind("/")]
                    targetFile = targetDir + f[f.rfind("/"):]
                    print("sourceFile:"+sourceFile)
                    print("targetDir:" + targetDir)
                    print("targetFile:" + targetFile)
                    if not os.path.exists(targetDir):
                        os.makedirs(targetDir)
                    with open(targetFile, "wb") as file:
                        self.logger.info("将源文件" + sourceFile + "提取到：" + targetFile)
                        file.write(open(sourceFile, 'rb').read())
                    release.append(targetFile)
            else:
                sourceFile = r"%s%s" % (self.base_dir, f)
                # 截掉eam/WebRoot目录
                f = f.replace("eam/WebRoot", "")
                targetDir = self.release_dir + self.date_file + f[0:f.rfind("/")]
                targetFile = targetDir + f[f.rfind("/"):]
                if not os.path.exists(targetDir):
                    os.makedirs(targetDir)
                with open(targetFile, "wb") as file:
                    self.logger.info("将源文件" + sourceFile + "提取到：" + targetFile)
                    file.write(open(sourceFile, "rb").read())
                release.append(targetFile)
        return release

    def build(self):
        os.chdir("E:/工作/project/Python_Project/resource")
        os.system("ant -f %s" % "eam_build.xml")

    def buildFileGroup(self, releaseFiles, replace_path):
        files = []
        for f in releaseFiles:
            files.append({"sourceFile": f,
                          "targetFile": f.replace(self.release_dir + self.date_file,
                                                  replace_path + self.date_file)})
        return files



if __name__ == "__main1__":
    eam = Git_EAM()
    eam.logger.info("####################开始########################" + eam.date_file)
    min = "a6e01bccd7d353a4b0dd8170825ed01f1b91a039"
    max = "561ec5d112ca511298797c2ebcc5136b6794d2eb"
    eam.logger.info("始版本号：" + min)
    eam.logger.info("终止版本号：" + max)
    eam.get_diff_file(min, max)
    # 编译工程
    eam.logger.info("编译工程")
    eam.build()
    # 获得编译后的发布文件
    # eam.logger.info("获得编译后的发布文件")
    releaseFiles = eam.get_release()
    replace_path = "/bea/application/release/eam/"
    files = eam.buildFileGroup(releaseFiles, replace_path)





if __name__ == "__main__":
    eam = Git_EAM()
    eam.logger.info("####################开始########################" + eam.date_file)
    # 不包含min版本号，包含max
    min = "43fad82f8e71149b714751c3a542a11cfa7fd7f6"
    max = "42472f69a7d5ba0be8e77a27a9bdd1c2b15ee84c"
    eam.logger.info("始版本号：" + min)
    eam.logger.info("终止版本号：" + max)
    eam.get_diff_file(min, max)
    # 编译工程
    eam.logger.info("编译工程")
    eam.build()
    # 获得编译后的发布文件
    eam.logger.info("获得编译后的发布文件")
    releaseFiles = eam.get_release()
    replace_path = "/bea/application/release/eam/"
    files = eam.buildFileGroup(releaseFiles, replace_path)

    # 服务器配置
    with open('E:/工作/project/Python_Project/resource/eam_servers.json') as json_file:
        configs = json.load(json_file)
    for config in configs:
        eam.logger.info("开始上传发布包到服务器：" + config["ip"])
        ssh = Ssh.SshUtil(config["ip"], config["port"], config["username"], config["password"])
        ssh.sftp_uploadFile(files, config["mkdirs"])
        eam.logger.info("将服务器上的发布包发布到项目，并备份")
        ssh.release(config["release"], eam.date_file)
        ssh.ssh.close()
        eam.logger.info("上传服务器：" + config["ip"] + "结束")

    eam.logger.info("####################结束########################" + eam.date_file)


