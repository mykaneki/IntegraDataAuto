import subprocess

# 关闭 rethinkdb
subprocess.run(['taskkill', '/IM', 'rethinkdb.exe', '/F'], shell=True)

# 关闭 appium
subprocess.run(['taskkill', '/IM', 'node.exe', '/F'], shell=True)

# 关闭 atxserver2 和 atxserver2-android-provider
# 由于这两个进程都是由 Python 启动的，我们需要结束所有的 Python 进程
# 注意，这将结束运行中的所有 Python 进程，如果你有其他的 Python 进程在运行，需要谨慎使用
subprocess.run(['taskkill', '/IM', 'python.exe', '/F'], shell=True)