#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'hewenhui'
import paramiko


class SshUtil:
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.ip, self.port, self.username, self.password)

    def sftp_uploadFile(self, Files, py_script):
        try:
            t = paramiko.Transport(self.ip, self.port)
            t.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(t)

            for f in Files:
                targetFile = f["targetFile"]
                sourceFile = f["sourceFile"]

                targetPath = targetFile[0:targetFile.rfind("/")]
                print(targetPath)
                # 调用服务器端的脚本，创建目录
                std_in, std_out, std_err = self.ssh.exec_command(r"python %s %s" % (py_script, targetPath))
                # 防止文件未创建，已经执行sftp.put
                out = std_out.readlines()
                for o in out:
                    print(out)

                sftp.put(sourceFile, targetFile)
            t.close()
        except Exception as e:
            print(e)
            print("出错")
            t.close()

    def release(self, py_script, fileName):
        std_in, std_out, std_err = self.ssh.exec_command(r"python %s %s" % (py_script, fileName))
        out = std_out.readlines()
        for o in out:
            print(out)


if __name__ == "__main__":
    configs = [
  {
    "ip": "10.21.10.10",
    "port": 22,
    "username": "weblogic",
    "password": "1qaz@wsx",
    "release_dir": "/bea/application/release/eam",
    "mkdirs":"/bea/application/release/mkdirs.py",
    "release":"/bea/application/release/release_backup.py111"
  }
]
    files = [{'targetFile': '/app/release/20171106160412/asset/goods/search/toolbar.jsp',
              'sourceFile': ''}
             ]
    # for config in configs:
    #     ssh = SshUtil(config["ip"], config["port"], config["username"], config["password"])
    #     ssh.sftp_uploadFile(files, "/app/mkdirs.py")
    ssh = SshUtil("10.21.10.10", 22, "weblogic", "1qaz@wsx")
    #ssh = SshUtil("10.20.3.146", 22, "weblogic", "weblogic")
    ssh.release("/bea/application/release/release_backup.py","20171106172354")
    #ssh.release("/app/release/release_backup.py", "20171106164230")
    ssh.ssh.close()
    #ssh.sftp_uploadFile(files,"/bea/application/release/mkdirs.py")
