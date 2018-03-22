#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'hewenhui'
import paramiko
import configparser

class Bastion(object):
    def __init__(self, pro):
        cf = configparser.ConfigParser()
        cf.read("../resource/bastion.ini")
        self.ip = cf.get(r"%s" % pro, "ip")
        self.username = cf.get(r"%s" % pro, "username")
        self.password = cf.get(r"%s" % pro, "password")
        self.project = cf.get(r"%s" % pro, "project")
        self.owner = cf.get(r"%s" % pro, "owner")
        self.local_user = cf.get(r"%s" % pro, "local_user")
        self.local_password = cf.get(r"%s" % pro, "local_password")
        self.local_ip = cf.get(r"%s" % pro, "local_ip")
        self.local_path = cf.get(r"%s" % pro, "local_path")
        self.server_path = cf.get(r"%s" % pro, "server_path")
        self.server_script_path = cf.get(r"%s" % pro, "server_script_path")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.ip, 22, self.username, self.password)
        self.channel = self.ssh.invoke_shell()
        self.channel.settimeout(10)
        # 通过堡垒机跳转到审计系统
        buff = ""
        resp = ""
        # 选择服务器

        self.channel.send(self.project + "\n")

        while not buff.endswith("> "):
            resp = self.channel.recv(9999).decode("gb2312")
            buff += resp
        buff = ""
        # 选择用户
        self.channel.send(self.owner + '\n')
        while not buff.endswith("$ "):
            resp = self.channel.recv(9999).decode("gb2312")
            buff += resp

    def get_release_file(self, filename):
        buff = ""
        resp = ""
        cmd = "scp -r %s@%s:/%s/%s %s\n" % (self.local_user, self.local_ip, self.local_path, filename, self.server_path)
        self.channel.send(cmd)
        while not buff.endswith("password: "):
            resp = self.channel.recv(9999).decode("gb2312")
            buff += resp
        self.channel.send(self.local_password + "\n")

        while not buff.endswith("$ "):
            resp = self.channel.recv(9999).decode("gb2312")
            buff += resp
        return buff

    def release(self, filename):
        buff = ""
        resp = ""
        cmd = "python %s %s\n" % (self.server_script_path, filename)
        print(cmd)
        self.channel.send(cmd)
        while not buff.endswith("$ "):
            resp = self.channel.recv(9999).decode("gb2312")
            buff += resp
            print(resp)
        return buff

    def download_file(self, file):
        buff = ""
        resp = ""
        cmd = "scp -rp %s %s@%s:%s\n" % (file, self.local_user, self.local_ip, self.local_path)
        print(cmd)
        self.channel.send(cmd)
        while not buff.endswith("password: "):
            resp = self.channel.recv(9999).decode("gb2312")
            buff += resp
        self.channel.send(self.local_password + "\n")

        while not buff.endswith("$ "):
            resp = self.channel.recv(9999).decode("gb2312")
            buff += resp
        return buff


if __name__ == "__main__":
    bastion = Bastion("risk")

    filename = "/bea/user_projects/domains/base_domain/bin/app1/nohup.out"
    print(bastion.download_file(filename))
