#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'hewenhui'
from base import ABCRelease
from base import Ssh
import configparser
import os
import json



class Git_UM(ABCRelease.ABCRelease):
    def __init__(self):
        cf = configparser.ConfigParser()
        cf.read("../resource/system.ini")
        self.class_dir = cf.get(r"%s" % "um", "class_dir")
        super(Git_UM, self).__init__("um")

    def get_diff_file(self, min, max):
        self.change = []
        os.chdir(self.base_dir)
        #os.system("git reset --hard HEAD")
        os.system("git reset --hard HEAD")
        # changes = os.system("git diff %s %s --name-only|xargs zip update.zip " % (min, max))
        out = os.popen(
            "git diff --binary %s %s --name-only ./um/um" % (min, max))
        for i in out.readlines():
            filename = i.strip('\n')
            self.logger.info("文件" + filename + "下载到工程")
            os.system("git checkout %s %s" % (max, filename))
            self.change.append(filename)

        return self.change

    def get_release(self):
        release = self.__get_git_release()
        return release


    def __get_git_release(self):
        release = []

        for f in self.change:
            print(f)
            if f.startswith("um/um/JavaSource/src"):
                if f.endswith(".java"):
                    f = f.replace(".java", ".class", 1)
                f = f.replace("um/um/JavaSource/src", "")
                sourceFile = r"%s%s%s" % (self.base_dir, "um/um/build/" + self.class_dir, f)
                targetDir = self.release_dir + self.date_file + "/WEB-INF/classes" + f[0:f.rfind("/")]
                targetFile = targetDir + f[f.rfind("/"):]

                if not os.path.exists(targetDir):
                    os.makedirs(targetDir)
                with open(targetFile, "wb") as file:
                    self.logger.info("将源文件" + sourceFile + "提取到：" + targetFile)
                    file.write(open(sourceFile, 'rb').read())
                release.append(targetFile)
            elif f.startswith("um/um/JavaSource/resource"):
                    f = f.replace("um/um/JavaSource/resource", "")
                    sourceFile = r"%s%s%s" % (self.base_dir, "um/um/build/" + self.class_dir, f)
                    targetDir = self.release_dir + self.date_file + "/WEB-INF/classes" + f[0:f.rfind("/")]
                    targetFile = targetDir + f[f.rfind("/"):]
                    if not os.path.exists(targetDir):
                        os.makedirs(targetDir)
                    with open(targetFile, "wb") as file:
                        self.logger.info("将源文件" + sourceFile + "提取到：" + targetFile)
                        file.write(open(sourceFile, 'rb').read())
                    release.append(targetFile)
            elif f.startswith("um/um/WebContent"):
                sourceFile = r"%s%s" % (self.base_dir, f)
                # 截掉um/WebRoot目录
                f = f.replace("um/um/WebContent", "")
                print("WebContent:"+f)
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
        os.system("java -version")
        os.system("ant -f %s" % "um_build.xml")

    def buildFileGroup(self, releaseFiles, replace_path):
        files = []
        for f in releaseFiles:
            files.append({"sourceFile": f,
                          "targetFile": f.replace(self.release_dir + self.date_file,
                                                  replace_path + self.date_file)})
        return files


if __name__ == "__main__":
    um = Git_UM()
    um.logger.info("####################开始########################" + um.date_file)
    min = "fe9ee82bf2559b8d93a975a9c148dd92e70a3895"
    max = "da122f379096261de79f205c5cf25c6535f5d040"
    um.logger.info("始版本号：" + min)
    um.logger.info("终止版本号：" + max)
    um.get_diff_file(min, max)
    # 编译工程
    um.logger.info("编译工程")
    um.build()
    # 获得编2222译后的发布文件
    #um.logger.info("获得编译后的发布文件")
    releaseFiles = um.get_release()
    replace_path = "/app/new_release/um/"
    files = um.buildFileGroup(releaseFiles, replace_path)
    # 服务器配置
    with open('E:/工作/project/Python_Project/resource/um_servers.json') as json_file:
        configs = json.load(json_file)
    for config in configs:
        um.logger.info("开始上传发布包到服务器：" + config["ip"])
        ssh = Ssh.SshUtil(config["ip"], config["port"], config["username"], config["password"])
        ssh.sftp_uploadFile(files, config["mkdirs"])
        um.logger.info("将服务器上的发布包发布到项目，并备份")
        ssh.release(config["release"], um.date_file)
        ssh.ssh.close()
        um.logger.info("上传服务器：" + config["ip"] + "结束")

    um.logger.info("####################结束########################" + um.date_file)


