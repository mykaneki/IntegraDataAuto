import subprocess

# 定义路径变量
RETHINKDB_PATH = r'D:\project\PycharmProjects\rethinkdb\Windows\rethinkdb.exe'
ATXSERVER2_ANDROID_PROVIDER_PATH = r'D:\project\PycharmProjects\atxserver2-android-provider'
ATXSERVER2_MASTER_PATH = r'D:\project\PycharmProjects\atxserver2-master'

# 定义一个辅助函数，启动进程并等待其输出特定的字符串
def start_process_and_wait_for_output(command, success_message, cwd=None, shell=False):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell, cwd=cwd, universal_newlines=True)

    # 循环读取输出，直到找到成功的消息
    while True:
        output = process.stdout.readline().strip()
        print(output)  # 打印输出，以便调试
        if success_message in output:
            break

    return process

# 启动 rethinkdb
print('启动 rethinkdb')
rethinkdb_process = start_process_and_wait_for_output([RETHINKDB_PATH], 'Server ready', cwd=ATXSERVER2_ANDROID_PROVIDER_PATH)
print('启动 rethinkdb 成功')

# 启动 appium
print('启动 appium')
appium_process = start_process_and_wait_for_output(['appium'], 'Available drivers:', shell=True)
print('启动 appium 成功')

# 启动 atxserver2
print('启动 atxserver2')
atxserver2_process = start_process_and_wait_for_output(['python', r'.\main.py'], 'listen on', cwd=ATXSERVER2_MASTER_PATH)
print('启动 atxserver2 成功')

# 启动 atxserver2-android-provider
print('启动 atxserver2-android-provider')
atxserver2_android_provider_process = start_process_and_wait_for_output(['python', r'.\main.py', '--server', 'localhost:4000'], 'DeviceEvent(present=True', cwd=ATXSERVER2_ANDROID_PROVIDER_PATH)
print('启动 atxserver2-android-provider 成功')