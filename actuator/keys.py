import random

from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


# 定义一个断言类，提供各种常用断言方法
class TestAssertObject:
    # 为了处理波浪线
    @staticmethod
    # 断言 value 在 obj 中
    def assert_in(assert_value, assert_obj):
        assert assert_value in assert_obj, f"{assert_value}不存在于{assert_obj}"

    @staticmethod
    # 断言 value 在 obj 的一部分中
    def assert_in_one_local(assert_value, assert_obj):
        string_ = ""
        for i in assert_obj:
            string_ += i
        assert assert_value in string_, f"{assert_value}不存在于{assert_obj}"

    @staticmethod
    # 断言两个值相等
    def assert_equal(value1, value2):
        assert value1 == value2, f"{value1}不等于{value2}"

    @staticmethod
    # 断言两个值不相等
    def assert_not_equal(value1, value2):
        assert value1 != value2, f"{value1}等于{value2}"

    @staticmethod
    # 断言某个值为真
    def assert_true(value):
        assert value, f"预期 {value} 为真，但实际不是。"

    @staticmethod
    # 断言某个值为假
    def assert_false(value):
        assert not value, f"预期 {value} 为假，但实际不是。"

    @staticmethod
    # 断言两个值是同一个对象
    def assert_is(value1, value2):
        assert value1 is value2, f"预期 {value1} 和 {value2} 是同一对象，但实际不是。"

    @staticmethod
    # 断言两个值不是同一个对象
    def assert_is_not(value1, value2):
        assert value1 is not value2, f"预期 {value1} 和 {value2} 不是同一对象，但实际是。"

    @staticmethod
    # 断言某个值为 None
    def assert_is_none(value):
        assert value is None, f"预期 {value} 为 None，但实际不是。"

    @staticmethod
    # 断言某个值不为 None
    def assert_is_not_none(value):
        assert value is not None, f"预期 {value} 不为 None，但实际是。"

    @staticmethod
    # 断言某个值不在某个容器中
    def assert_not_in(value, container):
        assert value not in container, f"预期 {value} 不在 {container} 中，但实际在。"

    @staticmethod
    # 断言某个值是某个类的实例
    def assert_is_instance(value, cls):
        assert isinstance(value, cls), f"预期 {value} 是 {cls} 的实例，但实际不是。"

    @staticmethod
    # 断言某个值不是某个类的实例
    def assert_not_is_instance(value, cls):
        assert not isinstance(value, cls), f"预期 {value} 不是 {cls} 的实例，但实际是。"

    @staticmethod
    # 判断两个列表是否相反
    def assert_list_reverse(value1, value2):
        assert value1 == value2[::-1], f"预期 {value1} 和 {value2} 是相反的列表，但实际不是。"


# 定义一个关键字类，提供各种方法
class TestKeyWords:
    @staticmethod
    # 从给定的序列中随机选择一个元素
    def random_choice(value):
        return random.choice(value)

    @staticmethod
    # 执行一个触摸屏动作，包括移动到指定位置，按下，暂停，释放
    def action_chains_pointer_down(driver, value):
        try:
            value_list = value.split(',')
            x = value_list[0]
            y = value_list[1]
            pause = float(value_list[2])
        except ValueError:
            raise ValueError("action_chains_pointer_down 参数错误(三个参数，需要均可以转为为小数)")
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(x, y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(pause)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    @staticmethod
    # 存储目录列表，并返回
    def store_directories(driver):
        directories_list = []
        while True:
            page_source = driver.page_source
            locator = ("id", "com.zhao.myreader:id/tv_chapter_title")
            element = WebDriverWait(driver, 10).until(ec.presence_of_all_elements_located(locator))
            for i in element:
                title = i.text.split("\n")
                if title not in directories_list:
                    directories_list.append(title)
            x1 = 457
            y1 = 1700
            x2 = 457
            y2 = 872
            driver.swipe(x1, y1, x2, y2)
            new_page_source = driver.page_source
            if page_source == new_page_source:
                break
        return directories_list


def test():
    from appium import webdriver

    # For W3C actions
    caps = {}
    caps["platformName"] = "Android"
    caps["appium:platformVersion"] = "9"
    caps["appium:automationName"] = "uiautomator2"
    caps["appium:deviceName"] = "FJH5T18C31075437"
    caps["appium:appPackage"] = "com.zhao.myreader"
    caps["appium:appActivity"] = "com.zhao.myreader.ui.home.MainActivity"
    caps["appium:ensureWebviewsHavePages"] = True
    caps["appium:nativeWebScreenshot"] = True
    caps["appium:newCommandTimeout"] = 3600
    caps["appium:connectHardwareKeyboard"] = True

    driver = webdriver.Remote("http://127.0.0.1:4723", caps)
    TestKeyWords.action_chains_pointer_down(driver, "100,100,0.1")
    driver.find_element("id", "com.zhao.myreader:id/tv_chapter_title").get_attribute("text")
