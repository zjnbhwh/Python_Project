#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'hewenhui'
import paramiko
import os
import json
import configparser
from base import Ssh


class WorkFlow(object):
    def __init__(self, project):

        cf = configparser.ConfigParser()
        cf.read("../resource/system.ini")
        self.local_path = cf.get(r"%s" % project, "local_path")
        self.server_path = cf.get(r"%s" % project, "server_path")
        self.date_file = ''

    def get_release_files(self, path, release_files):
        if os.path.isdir(path):
            for f in os.listdir(path):
                sourceFile = path + "/" + f
                if os.path.isdir(sourceFile):
                    self.get_release_files(sourceFile, release_files)
                elif os.path.isfile(sourceFile):
                    release_files.append(sourceFile)

    def buildFileGroup(self, releaseFiles):
        files = []
        for f in releaseFiles:
            files.append({"sourceFile": f,
                          "targetFile": f.replace(self.local_path + "/" + self.date_file,
                                                  self.server_path + "/" + self.date_file)})
        return files


if __name__ == "__main__":
    filename = input("请输入要发布的文件夹名：")
    # filename = '20171218'
    with open('workflow_servers.json') as json_file:
        configs = json.load(json_file)
    release_files = []
    wf = WorkFlow("workflow")
    wf.date_file = filename

    wf.get_release_files(wf.local_path + "/" + filename, release_files)
    files = wf.buildFileGroup(release_files)
    with open('workflow_servers.json') as json_file:
        configs = json.load(json_file)
    for config in configs:
        ssh = Ssh.SshUtil(config["ip"], config["port"], config["username"], config["password"])
        ssh.sftp_uploadFile(files, config["mkdirs"])
        ssh.release(config["release"], filename)
        ssh.ssh.close()
