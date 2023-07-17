import pytest

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.appium_service import AppiumService
from appium.webdriver.common.appiumby import AppiumBy
from pytest_html import extras as _extras
from actuator.context import TestContext
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
def android_driver(request, android_options, appium_service, atx, conf):  # 注意我们添加了 request 参数
    _android_driver = None
    try:
        _android_driver = user_device(android_options, atx, conf)
        # 将 android_driver 保存到 item
        request.node.android_driver = _android_driver
        setattr(TestContext, "driver", _android_driver)
        yield _android_driver
    except Exception as e:
        print(e)
    finally:
        release_device(_android_driver, atx, conf)


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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):  # 注意这里我们没有 android_driver 参数
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])
    if report.when == "call":
        print("⽤例执⾏结果:", report.outcome)
    if report.outcome != "passed":
        """失败截图数据"""
        # 从 item 获取 android_driver
        # android_driver = getattr(TestContext, "android_driver", None)
        if android_driver is not None:
            print("添加截图")
            extra.append(_extras.image(getattr(TestContext,'driver').get_screenshot_as_base64()))
            report.extra = extra


def pytest_addoption(parser):
    parser.addoption("--excel_path", action="store", default="../excel/data/data.xlsx",
                     help="可选参数，默认为../excel/data/data.xlsx")


def test_android_click(android_driver):
    print(android_driver.find_element(AppiumBy.ACCESSIBILITY_ID, '书城').text)
    elm = android_driver.find_element(AppiumBy.ACCESSIBILITY_ID, '书城')
    elm.get_attribute('text')
