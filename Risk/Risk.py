#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'hewenhui'
from base import Bastion


class Risk(Bastion.Bastion):
    def __init__(self):
        super(Risk, self).__init__("risk")


if __name__ == "__main__":
    risk = Risk()
    filename = input("请输入要发布的文件夹名：")
    resp = ""
    resp = risk.get_release_file(filename)

    if resp.endswith("$ "):
        resp = risk.release(filename)
        if resp.endswith("$ "):
            risk.ssh.close()
