# 执行器
import inspect
from actuator.context import Test_Context
from excel.readExcel import Excel
from appium.webdriver.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from enum import Enum, auto


class Action(Enum):
    FIND = auto()
    CLICK = auto()
    FIND_AND_CLICK = auto()
    SEND_KEYS = auto()
    GET_ATTRIBUTE = auto()
    ASSERT = auto()
    PAGE_SOURCE = auto()


def setattr_(name, value):
    setattr(Test_Context, name, value)


def getattr_(name):
    return getattr(Test_Context, name)


def driver_func(driver_name, action, value=None):
    return_value = None
    if value:
        return_value = getattr_(driver_name).__getattribute__(action)(value)
    else:
        # click
        return_value = getattr_(driver_name).__getattribute__(action)()
    return return_value


def check_value_and_raise(row_num, value, error_type):
    if not value:
        raise ValueError(f"第{row_num}行{error_type}为空")


def my_find_action(driver, wait, action_type, selector, selector_value):
    element = None
    if action_type in ["find_element", "find_elements"]:
        element = driver.__getattribute__(action_type)(by=selector,
                                                       value=selector_value)
    else:
        locator = (selector, selector_value)
        element = wait.until(getattr(ec, action_type)(locator))
    return element


def locate_and_set_element(driver, wait, action_type, selector, selector_value, element_name):
    value = my_find_action(driver, wait, action_type, selector, selector_value)
    setattr_(element_name, value)


def find(driver, wait, action_type, selector, selector_value, element_name, row_num):
    # 元素命名
    check_value_and_raise(row_num, element_name and selector and selector_value, '元素命名或选择器或选择器的值')
    locate_and_set_element(driver, wait, action_type, selector, selector_value, element_name)


def click(driver_name, action, row_num):
    check_value_and_raise(row_num, driver_name, '操作对象')
    driver_func(driver_name, action)
    getattr_(driver_name).__getattribute__(action)()


def find_and_click(driver_name, wait, action_type, selector, selector_value, element_name, row_num):
    check_value_and_raise(row_num, element_name and selector and selector_value, '元素命名或选择器或选择器的值')
    if 'elements' in action_type:
        raise ValueError(f"第{row_num}行的方式为find_elements，不支持")
    my_find_action(driver_name, wait, action_type, selector, selector_value)
    if action_type == "find_element":
        setattr(Test_Context, element_name,
                driver_name.__getattribute__(action_type)(by=selector, value=selector_value))
        getattr(Test_Context, element_name).__getattribute__('click')()
    else:
        locator = (selector, selector_value)
        setattr(Test_Context, element_name,
                wait.until(getattr(ec, action_type)(locator)))
        getattr(Test_Context, element_name).__getattribute__('click')()


def actuator(sheet_name, excel_path):
    # 获取测试设备及driver
    driver = getattr(Test_Context, "driver")
    wait_time = 5
    wait = WebDriverWait(driver, wait_time)
    # 获取测试用例
    excel = Excel(excel_path)
    test_case_data = excel.read_case_excel(sheet_name)
    # 获取测试步骤
    for index, i in enumerate(test_case_data):
        action = i.get('操作') or None
        action_type = i.get("方式") or None
        selector = i.get('选择器') or None
        selector_value = i.get('定位元素的值') or None
        element_name = i.get('给获取到的元素命名') or None
        driver_name = i.get('操作的对象') or 'driver'
        action_value = i.get('操作的值') or None
        assert_type = i.get('断言类型') or None
        assert_value = i.get('断言的值') or None
        row_num = index + 1  # 索引从0开始，所以加1
        # 执行操作
        # find,click,find_and_click,send_keys,get_attribute,assert,page_source
        # 如何实现元素内定位？
        if action == 'find':
            find(driver, wait, action_type, selector, selector_value, element_name, row_num)
        elif action == 'click':
            click(driver_name, action, row_num)
        elif action == 'find_and_click':
            find_and_click(driver_name, wait, action_type, selector, selector_value, element_name, row_num)
        elif action == 'find_in_elm':
            # 元素命名
            if element_name:
                # 有选择器及其值
                if selector and selector_value and hasattr(Test_Context, driver_name):
                    if action_type in ["find_element", "find_elements"]:
                        # 操作对象为已定义元素
                        setattr(Test_Context, element_name,
                                driver_name.__getattribute__(action_type)(by=selector,
                                                                          value=selector_value))
                    else:
                        locator = (selector, selector_value)
                        # element = WebDriverWait(driver, 10).until(ec.presence_of_element_located(locator))
                        wait = WebDriverWait(getattr(Test_Context, driver_name), wait_time)
                        setattr(Test_Context, element_name,
                                wait.until(getattr(ec, action_type)(locator)))
                else:
                    raise ValueError(f"第{row_num}行的选择器或选择器的值为空")
            else:
                raise ValueError(f"第{row_num}行元素命名为空")
        elif action == 'send_keys':
            if driver_name:
                getattr(Test_Context, driver_name, None).__getattribute__(action)(action_value)
            else:
                raise ValueError(f"第{row_num}行的操作对象为空")
        elif action == 'get_attribute':
            # elm.get_attribute('text')
            if driver_name:
                elm_obj = getattr(Test_Context, driver_name, None)
                if element_name and action_value:
                    if elm_obj and isinstance(elm_obj, WebElement):
                        setattr(Test_Context, element_name, elm_obj.__getattribute__(action)(action_value))
                    elif elm_obj and isinstance(elm_obj, list):
                        setattr(Test_Context, element_name, (i.__getattribute__(action)(action_value) for i in elm_obj))
                else:
                    raise ValueError(f"第{row_num}行的元素命名或操作的值为空")
            else:
                raise ValueError(f"第{row_num}行的操作对象为空")
        elif action == 'assert':
            if driver_name:
                # 以$开头的为Context中的变量
                if driver_name.startswith('$'):
                    val1 = getattr(Test_Context, driver_name[1:], None)
                else:
                    val1 = driver_name
                if assert_value and assert_value.startswith('$'):
                    val2 = getattr(Test_Context, assert_value[1:], None)
                else:
                    val2 = assert_value
                assert_method = getattr(Test_Context, assert_type, None)
                if assert_method is not None:
                    # 根据参数个数划分断言方法
                    params = inspect.signature(assert_method).parameters
                    if len(params) == 1:
                        # 优先使用driver_name
                        assert_method(val1)
                    elif len(params) == 2 and assert_value is not None:
                        assert_method(val1, val2)
                    else:
                        raise ValueError(f"第{row_num}行的操作对象或断言的值为空或断言方法的参数不正确")
                else:
                    raise ValueError(f"第{row_num}行的断言类型无效，请在 keys.Test_AssertObject 中添加")
            else:
                raise ValueError(f"第{row_num}行的操作对象为空")
        elif action == 'page_source':
            if driver_name:
                getattr(Test_Context, driver_name, None).__getattribute__(action)()
            else:
                raise ValueError(f"第{row_num}行的操作对象为空")
        elif action == 'wait_activity':
            if driver_name and action_value:
                getattr(Test_Context, driver_name, None).__getattribute__(action)(action_value)
            else:
                raise ValueError(f"第{row_num}行的操作对象或操作的值为空")
        elif action.startswith("$"):
            # 以$开头的为Context中的变量，是在 keys.Test_KeyWords 自定义的方法
            if driver_name is None:
                driver_name = "driver"
            if driver_name is not None and hasattr(Test_Context, action.replace("$", "")):
                action_method = getattr(Test_Context, action.replace("$", ""))  # 取到函数
                # 将函数分为是否需要action_value的两种情况
                params = inspect.signature(action_method).parameters
                if len(params) == 1:
                    if element_name is not None:
                        setattr(Test_Context, element_name,
                                action_method(getattr(Test_Context, driver_name)))  # 执行函数，并将结果保存为 name
                    else:
                        action_method(getattr(Test_Context, driver_name))
                elif len(params) == 2:
                    if element_name is not None:
                        setattr(Test_Context, element_name,
                                action_method(getattr(Test_Context, driver_name), action_value))
                    else:
                        action_method(getattr(Test_Context, driver_name), action_value)
            else:
                raise ValueError(f"第{row_num}行的操作对象为空或函数未定义")
