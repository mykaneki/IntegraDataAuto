from excel.readExcel import Excel
from server.atxApi import AtxByCF
from urllib.parse import urlparse


class Config:
    def __init__(self, confpath):
        self.confPath = confpath
        self.atxurl, self.atxtoken, self.atxdevice = self.get_atx_config()
        self.appiumurl, self.appiumcaps = self.get_appium_config()
        self.appiumhost, self.appiumport, self.appiumbasepath = self.split_url()

    def get_atx_config(self):
        '''
        获取atx配置
        :return: atx配置字典
        '''
        excel = Excel(self.confPath)
        atxdata = excel.read_conf_excel()
        atxurl = atxdata['atxurl']
        # 优先读取url，如果url为空，则读取host和port拼接url
        # 如果host和port都为空，则使用默认url：http://127.0.0.1:4000
        if atxurl is None:
            atxhost = atxdata['atxhost']
            atxport = atxdata['atxport']
            if atxhost is None or atxport is None:
                atxurl = 'http://127.0.0.1:4000'
            else:
                atxurl = 'http://' + atxhost + ':' + atxport
        atxtoken = atxdata['atxtoken']
        if atxtoken is None:
            print('请在配置文件中填写atxtoken')
            exit()
        atxdevice = atxdata['atxdevice']
        # 如果atxdevice为空，则随机获取一个设备
        if atxdevice is None:
            atx = AtxByCF(atxurl)
            atxdevice = atx.get_one_device_by_random_choice(atxtoken)
        return atxurl, atxtoken, atxdevice

    def get_appium_config(self):
        '''
        从配置文件中获取用户自定义的appium配置
        :return: appium配置字典
        '''
        excel = Excel(self.confPath)
        appiumdata = excel.read_conf_excel()
        appiumurl = appiumdata['appiumurl']
        if appiumurl is None:
            appiumhost = appiumdata['appiumhost']
            appiumport = appiumdata['appiumport']
            appiumbasepath = appiumdata['appiumbasepath']
            if appiumhost is None or appiumport is None:
                appiumurl = 'http://127.0.0.1:4723'
            if appiumbasepath is None:
                appiumbasepath = ''
            appiumurl = f'http://{appiumhost}:{appiumport}{appiumbasepath}'
        appiumcaps = appiumdata['appiumcaps']
        appiumcaps.update(self.get_appium_base_caps())
        return appiumurl, appiumcaps

    def get_appium_base_caps(self):
        '''
        从atx获取appium基本配置
        :return: appium基本配置字典
        '''
        appiumcaps = dict()
        atx = AtxByCF(self.atxurl)
        remote_info = atx.get_remote_info(self.atxtoken, self.atxdevice)
        appiumcaps.update(remote_info)
        return appiumcaps

    def split_url(self):
        '''
        拆分appiumurl
        :return: appiumhost, appiumport, appiumbasepath
        '''
        appiumhost = urlparse(self.appiumurl).hostname
        appiumport = str(urlparse(self.appiumurl).port)
        appiumbasepath = urlparse(self.appiumurl).path
        return appiumhost, appiumport, appiumbasepath





if __name__ == '__main__':
    config = Config('./excel/data/data.xlsx')
    print(config.get_atx_config())  # ('http://127.0.0.1:4000', '10f9e684b0ab455980db87f61a4d7d93')
    print(config.atxurl)
    print(config.get_appium_config())
    print(config.appiumurl)
    print(config.appiumcaps)
