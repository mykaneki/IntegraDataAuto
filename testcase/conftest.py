import pytest

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.appium_service import AppiumService
from appium.webdriver.common.appiumby import AppiumBy

from actuator.context import Test_Context
from config import Config
from server.atxApi import AtxByCF


@pytest.fixture(autouse=True, scope='session')
def conf():
    config_path = '../excel/data/data.xlsx'
    return Config(config_path)


@pytest.fixture(autouse=True, scope='session')
def appium_service(conf):
    service = AppiumService()
    service.start(
        args=['--address', conf.appiumhost,
              '--port', conf.appiumport,
              '--base-path', conf.appiumbasepath],
        timeout_ms=20000,
    )
    yield service
    service.stop()


@pytest.fixture(scope='session')
def android_options(conf):
    options = UiAutomator2Options()
    options.load_capabilities(conf.appiumcaps)
    return options


@pytest.fixture(scope='session')
def ios_options(conf):
    options = XCUITestOptions()
    options.load_capabilities(conf.appiumcaps)
    return options


@pytest.fixture(autouse=True, scope='session')
def android_driver(android_options, appium_service, atx, conf):
    _android_driver = None
    try:
        _android_driver = user_device(android_options, atx, conf)
        setattr(Test_Context, "driver", _android_driver)
        yield _android_driver
    except Exception as e:
        print(e)
    finally:
        release_device(_android_driver, atx, conf)
        print(f"释放设备；{conf.atxdevice} 成功")

def ios_driver(ios_options, appium_service, atx, conf):
    pass


@pytest.fixture(scope='session')
def atx(conf):
    return AtxByCF(conf.atxurl)


def user_device(options, atx, conf):
    try:
        atx.user_device(conf.atxtoken, conf.atxdevice)
        print(f"占用设备；{conf.atxdevice} 成功")
    except Exception as e:
        print(f"占用设备；{conf.atxdevice} 失败")
        print(e)
    try:
        return webdriver.Remote(conf.appiumurl, options=options)
    except Exception as e:
        print(f"连接设备；{conf.atxdevice} 失败")
        print(e)
        return None


def release_device(android_driver, atx, conf):
    try:
        android_driver.quit()
    except Exception as e:
        print(f"释放设备；{conf.atxdevice} 失败")
        print(e)
    try:
        atx.release_device(conf.atxtoken, conf.atxdevice)
        print(f"释放设备；{conf.atxdevice} 成功")
    except Exception as e:
        print(f"+释放设备；{conf.atxdevice} 失败")
        print(e)


def test_android_click(android_driver):
    print(android_driver.find_element(AppiumBy.ACCESSIBILITY_ID, '书城').text)
    elm = android_driver.find_element(AppiumBy.ACCESSIBILITY_ID, '书城')
    elm.get_attribute('text')
