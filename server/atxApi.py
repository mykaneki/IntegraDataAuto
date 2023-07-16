import random
import time

from requests import get, post, delete


class AtxByCF:
    def __init__(self, host, token=None):
        self.host = host
        self.using_devices = []
        self.token = token

    def get_user(self, token):
        """
        获取用户信息
        :param token: token可以在 {self.HOST}/user 界面获取到
        :return:
        """
        path = "/api/v1/user"
        url = self.host + path
        headers = {"Authorization": f"Bearer {token}"}  # 每个请求在固定在 Header中增加 Authorization: Bearer {token}
        response = get(url=url, headers=headers)

        return response.json()

    def get_devices(self, token, **params):
        """
        获取设备列表
        :param token:
        :param params: (经过我的验证，同学们尽量不要传这几个个参数，默认使用不带参数最好；原因是官方接口没有写好，导致部分传参反而接收不到数据)
            platform:目前有两个值 android 和 apple
            present:代表设备是否在线
            colding:代表设备是否正在清理或者自检中, 此时是不能占用设备的
            using:代表设备是否有人正在使用
            userId:代表使用者的ID，这里的ID其实就是Email
            properties:代表设备的一些状态信息，基本都是静态信息
            usable等价于{present: true, using: false, colding: false}
        :return:
        """
        path = "/api/v1/devices"
        url = self.host + path
        headers = {"Authorization": f"Bearer {token}"}
        response = get(url=url, headers=headers, params=params)

        return response.json()

    def get_one_devices_no_sources(self, token, udid):
        """
        获取单个设备信息（不包含 sources 字段)
        :param token:
        :param udid:
        :return:
        """
        path = f"/api/v1/devices/{udid}"
        url = self.host + path
        headers = {"Authorization": f"Bearer {token}"}
        response = get(url=url, headers=headers)

        return response.json()

    def user_device(self, token, udid):
        """
        占用设备
        :param token:
        :param udid:
        :return:
        """
        path = "/api/v1/user/devices"
        url = self.host + path
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data = {"udid": udid}
        end_time = time.monotonic() + 30

        while True:
            self.get_user(token)
            self.get_devices(token)
            self.get_one_devices_no_sources(token, udid)
            response = post(url=url, headers=headers, json=data)
            self.using_devices.append(udid)
            # print(f"尝试连接的设备为：{udid}")
            self.token = token
            if response.json()["success"]:
                break
            if time.monotonic() > end_time:
                break
            time.sleep(0.5)
        return response.json()

    def get_one_devices_has_sources(self, token, udid):
        """
        获取用户设备信息(包含 sources 字段)
        :param token:
        :param udid:
        :return:
        """
        path = f"/api/v1/user/devices/{udid}"
        url = self.host + path
        end_time = time.monotonic() + 3
        headers = {"Authorization": f"Bearer {token}"}
        response = get(url=url, headers=headers)
        try:
            while True:
                success = response.json().get("success", None)
                if success:
                    return response.json()
                if time.monotonic() > end_time:
                    return response.json()
        except Exception as e:
            print("获取设备信息失败，可能秘钥错误")
            print(e)
            exit(1)

    def release_device(self, token, udid):
        """
        释放设备
        :param token:
        :param udid:
        :return:
        """
        path = f"/api/v1/user/devices/{udid}"
        url = self.host + path
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = delete(url=url, headers=headers, )
        return response.json()

    # 获取随机的可用设备
    def get_one_device_by_random_choice(self, token):
        devices = list()
        all_devices = self.get_devices(token).get("devices", None)
        if all_devices:
            for i in all_devices:
                # print(f"得到的所有的i:{i}")
                using = i.get("using", None)
                present = i.get("present", None)
                if not using and present:  # 正在空闲状态的手机设备
                    _ud_id = i.get("udid", None)
                    devices.append(_ud_id)
            try:
                choice_device = random.choice(devices)
                return choice_device
            except IndexError:
                raise ValueError("没有空闲设备")
        else:
            raise ValueError("没有设备")

    def get_remote_info(self, token, device):
        result_data = self.get_one_devices_has_sources(token, device)
        print(result_data)
        platform = result_data["device"]["platform"]
        version = result_data["device"]["properties"]["version"]
        sources = result_data["device"]["sources"]
        sources_id = list(sources.keys())[0]  # 可以取到这个键名
        remote_connect_address = sources.get(sources_id).get("remoteConnectAddress")
        return {
            "platformName": platform,
            "platformVersion": version,
            "deviceName": remote_connect_address
        }

    # def __del__(self):
    #     for i in self.using_devices:
    #         self.release_device(self.token, i)


if __name__ == '__main__':
    _token = '10f9e684b0ab455980db87f61a4d7d93'
    host = 'http://127.0.0.1:4000'
    atx = AtxByCF(host)
    udid = atx.get_one_device_by_random_choice(_token)
    remote_info = atx.get_remote_info(_token, udid)
    # print(remote_info) # {'platformName': 'android', 'platformVersion': '9', 'deviceName': '192.168.3.5:20089'}
    # {'success': True, 'description': 'Device successfully added'}
    # {'success': True, 'description': 'Device successfully released'}
    print(atx.user_device(_token, udid))  # 占用设备
    print(atx.release_device(_token, udid))  # 释放设备
