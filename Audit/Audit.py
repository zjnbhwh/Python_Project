#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'hewenhui'
from base import Bastion
class Audit(Bastion.Bastion):
    def __init__(self):
        super(Audit, self).__init__("audit")

if __name__ == "__main__":
    audit = Audit()
    filename = input("请输入要发布的文件夹名：")
    resp = ""
    resp = audit.get_release_file(filename)
    if resp.endswith("$ "):
        resp = audit.release(filename)
        if resp.endswith("$ "):
            audit.ssh.close()
