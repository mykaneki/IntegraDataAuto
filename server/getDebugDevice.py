import platform
import subprocess
import os

from appium.webdriver.appium_service import AppiumService
from atxApi import AtxByCF

atxurl = 'http://127.0.0.1:4000'
port = '4723'
token = 'd9277c08d8d04401910c93364eeecb1f'
appiumbasepath = ''


def get_os():
    os_platform = platform.system()

    if os_platform == 'Windows':
        return 'Windows'
    elif os_platform == 'Darwin':
        return 'macOS'
    elif os_platform == 'Linux':
        return 'Linux'
    else:
        return 'Unknown OS'


def start_appium_inspector():
    os_type = get_os()
    if os_type == 'Windows':
        appium_path = os.environ.get('APPIUM_INSPECTOR_PATH')  # 获取环境变量
        if appium_path:
            subprocess.Popen([appium_path])
        else:
            print("APPIUM_INSPECTOR_PATH environment variable not found.")
    elif os_type == 'macOS':
        subprocess.call(["open", "-a", "APPIUM_INSPECTOR_PATH"])
    else:
        print(f"Unsupported OS: {os_type}")


def start_appium_server():
    service = AppiumService()
    service.start(
        args=['--address', '127.0.0.1',
              '--port', port,
              '--base-path', appiumbasepath],
        timeout_ms=20000,
    )
    return service


if __name__ == '__main__':
    '''
    在本地获取一个用于调试的设备
    '''
    atx = AtxByCF(atxurl)
    device = atx.get_one_device_by_random_choice(token)
    atx.user_device(token, device)
    caps = atx.get_remote_info(token, device)
    print(f"调试的设备信息为：\n{caps}")
    print("启动appium")
    service = start_appium_server()
    print("启动appium inspector")
    start_appium_inspector()
    while True:
        command = input("输入q退出：")
        if command == "q":
            atx.release_device(token, device)
            service.stop()
            print("设备已释放，debug动作完结")
            break
