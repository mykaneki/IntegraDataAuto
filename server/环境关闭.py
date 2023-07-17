import subprocess

subprocess.run(['taskkill', '/IM', 'rethinkdb.exe', '/F'], shell=True)

subprocess.run(['taskkill', '/IM', 'node.exe', '/F'], shell=True)

subprocess.run(['taskkill', '/IM', 'python.exe', '/F'], shell=True)
