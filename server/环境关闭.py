import subprocess

# �ر� rethinkdb
subprocess.run(['taskkill', '/IM', 'rethinkdb.exe', '/F'], shell=True)

# �ر� appium
subprocess.run(['taskkill', '/IM', 'node.exe', '/F'], shell=True)

# �ر� atxserver2 �� atxserver2-android-provider
# �������������̶����� Python �����ģ�������Ҫ�������е� Python ����
# ע�⣬�⽫���������е����� Python ���̣�������������� Python ���������У���Ҫ����ʹ��
subprocess.run(['taskkill', '/IM', 'python.exe', '/F'], shell=True)