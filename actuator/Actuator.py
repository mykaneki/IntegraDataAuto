# 执行器
import inspect
import logging
import os

from selenium.common import TimeoutException

from actuator.context import TestContext
from excel.readExcel import Excel
from appium.webdriver.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


def mylogging(sheet_name):
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger(sheet_name)
    logger.setLevel(logging.INFO)
    # 如果你想要同时将日志信息输出到控制台和文件，你可以为你的 logger 配置两个 handler：一个 StreamHandler 用于输出到控制台，一个 FileHandler 用于输出到文件。
    # 创建一个 FileHandler，用来将日志写入到文件中，并设置编码为 UTF-8
    file_handler = logging.FileHandler(f'logs/{sheet_name}.log', encoding='utf-8', mode='w')
    file_handler.setLevel(logging.INFO)

    # 创建一个 StreamHandler，用来将日志输出到控制台

    # StreamHandler并不需要编码设置，因为它是直接将日志信息输出到控制台，而控制台的编码方式通常由你的操作系统或者终端设置决定。
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # 创建一个 Formatter，用来设置日志的格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # 需要为每个 handler 分别设置 Formatter，因为每个 handler 都需要自己的 Formatter 来设置日志的格式。
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # 将 FileHandler 和 StreamHandler 添加到 logger 中
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    yield logger
    # 关闭 FileHandler 和 StreamHandler
    file_handler.close()
    stream_handler.close()


def setattr_(name, value):
    """
    将value的值赋给TestContext的name属性
    """
    setattr(TestContext, name, value)


def getattr_(name):
    """
    获取TestContext的name属性的值
    """
    return getattr(TestContext, name)


def driver_func(driver_name, action, value=None):
    """
    按有参无参调用driver自带的方法（如：driver.find_element()、driver.click()）
    无等待机制
    """
    return_value = None
    if value:
        if isinstance(value, dict):
            # 如果value是字典，则将其解包并传递给方法
            return_value = getattr_(driver_name).__getattribute__(action)(**value)
        else:
            # 否则，直接将value传递给方法
            return_value = getattr_(driver_name).__getattribute__(action)(value)
    else:
        # 如果没有提供value，则调用没有参数的方法
        return_value = getattr_(driver_name).__getattribute__(action)()
    return return_value


def check_value_and_raise(row_num, value, error_type):
    """
    检查值是否为空，如果为空则抛出ValueError
    """
    if not value:
        raise ValueError(f"第{row_num}行{error_type}为空")


def my_find_action(driver, wait, action_type, selector, selector_value):
    """
    根据给定的选择器找到网页元素
    """
    element = None
    if action_type in ["find_element", "find_elements"]:
        locator = {'by': selector, 'value': selector_value}
        element = driver_func(driver, action_type, locator)
    else:
        locator = (selector, selector_value)
        try:
            element = wait.until(getattr(ec, action_type)(locator))
        except TimeoutException:
            raise TimeoutException(f"等待超时，找不到元素：{locator}")
    return element


def find(driver, wait, action_type, selector, selector_value, element_name, row_num, logger):
    """
    根据给定的选择器找到网页元素并将其存储在TestContext中
    """
    logger.info(
        f"正在执行第{row_num}行，{element_name}={driver}.{action_type}('{selector}', '{selector_value}')")
    # 元素命名
    check_value_and_raise(row_num, element_name and selector and selector_value, '元素命名或选择器或选择器的值')
    setattr_(element_name, my_find_action(driver, wait, action_type, selector, selector_value))


def click(driver_name, action, row_num, logger):
    """
    调用driver的方法，例如click
    :param driver_name: str, 驱动器的名称，例如"Selenium"或"Appium"
    :param action: str, 驱动器的方法的名称，此处为"click"
    :param row_num: int, Excel表格中当前测试用例的行号，用于错误报告
    :return: None
    """
    logger.info(f"正在执行第{row_num}行，{driver_name}.{action}()")
    check_value_and_raise(row_num, driver_name, '操作对象')
    driver_func(driver_name, action)


def find_and_click(driver_name, wait, action_type, selector, selector_value, element_name, row_num, logger):
    """
    找到一个元素并点击它
    :param driver_name: str, 驱动器的名称
    :param wait: WebDriverWait, 当前使用的等待器，用于等待页面元素加载
    :param action_type: str, 操作类型，例如"find_element"
    :param selector: str, 选择器类型，例如"id"或"class name"
    :param selector_value: str, 选择器的值，例如元素的id或class name
    :param element_name: str, 在TestContext中存储元素的名称
    :param row_num: int, Excel表格中当前测试用例的行号，用于错误报告
    :return: None
    :raises ValueError: 如果action_type是"find_elements"，因为这个函数不支持查找多个元素并点击
    """
    logger.info(
        f"正在执行第{row_num}行，{element_name}={driver_name}.{action_type}('{selector}', '{selector_value}')\n{element_name}.click()")
    check_value_and_raise(row_num, element_name and selector and selector_value, '元素命名或选择器或选择器的值')
    if 'elements' in action_type:
        raise ValueError(f"第{row_num}行的方式为find_elements，不支持 find_and_click")
    if action_type == "find_element":
        locator = {'by': selector, 'value': selector_value}
        setattr_(element_name, driver_func(driver_name, action_type, locator))
        driver_func(element_name, 'click')
    else:
        locator = (selector, selector_value)
        setattr_(element_name,
                 wait.until(getattr(ec, action_type)(locator)))
        driver_func(element_name, 'click')


def find_in_elm(driver_name, wait_time, action_type, selector, selector_value, element_name, row_num, logger):
    """
    元素内查找，并将查找结果储存到 TestContext 中。

    :param driver_name: 操作的对象名。
    :param wait_time: 显示等待的时间。
    :param action_type: 操作类型，如"find_element"或"find_elements"。
    :param selector: 选择器，例如 'id' 或 'name'。
    :param selector_value: 选择器的值。
    :param element_name: 元素名称，用于存储查找结果。
    :param row_num: 行号，用于错误提示。
    """
    logger.info(
        f"正在执行第{row_num}行，{element_name}={driver_name}.{action_type}('{selector}', '{selector_value}')")
    # 元素命名
    check_value_and_raise(row_num, driver_name and element_name and selector and selector_value, '操作的对象名或元素命名或选择器或选择器的值')
    if hasattr(TestContext, driver_name):
        if action_type in ["find_element", "find_elements"]:
            # 操作对象为已定义元素
            locator = {'by': selector, 'value': selector_value}
            setattr_(element_name, driver_func(driver_name, action_type, locator))
        else:
            locator = (selector, selector_value)
            wait = WebDriverWait(getattr_(driver_name), wait_time)
            setattr(TestContext, element_name,
                    wait.until(getattr(ec, action_type)(locator)))
    else:
        raise ValueError(f"第{row_num}行的操作对象{driver_name}在TestContext中未找到")


def send_keys(driver_name, action, action_value, row_num, logger):
    """
    向操作对象发送指定的键值。

    :param driver_name: 操作的对象名。
    :param action: 操作名称。
    :param action_value: 要发送的键值。
    :param row_num: 行号，用于错误提示。
    """
    logger.info(f"正在执行第{row_num}行，{driver_name}.{action}({action_value})")
    check_value_and_raise(row_num, driver_name and action_value, '操作对象或操作的值')
    driver_func(driver_name, action, action_value)


def get_attribute_(driver_name, element_name, action, action_value, row_num, logger):
    """
    获取指定元素的属性值，并将其存储在 TestContext 中。

    :param driver_name: 操作的对象名。
    :param element_name: 元素名称。
    :param action: 操作名称。
    :param action_value: 操作的值（属性名）。
    :param row_num: 行号，用于错误提示。
    :param logger: 日志对象。
    """
    logger.info(f"正在执行第{row_num}行，{element_name}={driver_name}.{action}({action_value})")
    check_value_and_raise(row_num, driver_name and element_name and action_value, '操作对象或元素命名或操作的值')
    elm_obj = getattr_(driver_name)
    try:
        if elm_obj and isinstance(elm_obj, WebElement):
            setattr_(element_name, getattr(elm_obj, action_value))
        if elm_obj and isinstance(elm_obj, list):
            setattr_(element_name, (getattr(i, action_value) for i in elm_obj))
    except Exception as e:
        logger.error(f"{e}\n没有找到元素{elm_obj}或元素没有属性{action_value}，行号：{row_num}")
        raise e


def get_assert_value(driver_name, assert_value):
    """
    获取断言的值。如果值以 '$' 开头，那么从 TestContext 中获取；否则，直接返回值。

    :param driver_name: 操作的对象名或值。
    :param assert_value: 断言的值或 TestContext 中的变量名。
    :return: (val1, val2)
    """
    # 以$开头的为Context中的变量
    if driver_name.startswith('$'):
        val1 = getattr_(driver_name[1:])
    else:
        val1 = driver_name
    if assert_value.startswith('$'):
        val2 = getattr_(assert_value[1:])
    else:
        val2 = assert_value
    return val1, val2


def assert_(driver_name, assert_type, assert_value, row_num, logger):
    """
    执行断言。断言方法和值从 TestContext 中获取。

    :param driver_name: 操作的对象名或值。
    :param assert_type: 断言类型。
    :param assert_value: 断言的值。
    :param row_num: 行号，用于错误提示。
    :param logger: 日志对象。
    """
    if assert_value is None:
        logger.info(f"正在执行第{row_num}行，{assert_type}({driver_name})")
    else:
        logger.info(f"正在执行第{row_num}行，{assert_type}({driver_name}, {assert_value})")
    check_value_and_raise(row_num, driver_name and assert_value, '操作对象或断言的值')
    val1, val2 = get_assert_value(driver_name, assert_value)
    if not hasattr(TestContext, assert_type):
        logger.error(f"第{row_num}行的断言类型无效，请在 keys.Test_AssertObject 中添加")
        raise ValueError(f"第{row_num}行的断言类型无效，请在 keys.Test_AssertObject 中添加")
    assert_method = getattr_(assert_type)
    # 根据参数个数划分断言方法
    params = inspect.signature(assert_method).parameters
    if len(params) == 1:
        # 优先使用driver_name
        assert_method(val1)
    elif len(params) == 2:
        assert_method(val1, val2)
    else:
        raise ValueError(f"第{row_num}行的断言方法的参数不正确")


def wait_activity_(driver_name, action, action_value, row_num, logger):
    """
    等待特定的操作完成。

    :param driver_name: 操作的对象名。
    :param action: 操作名称。
    :param action_value: 操作的值。
    :param row_num: 行号，用于错误提示。
    :param logger: 日志对象。
    """
    logger.info(f"正在执行第{row_num}行，{driver_name}.{action}({action_value})")
    check_value_and_raise(row_num, driver_name and action_value, '操作对象或操作的值')
    driver_func(driver_name, action, action_value)


def page_source_(driver_name, action, element_name, row_num, logger):
    """
    获取页面源码，并将其存储在 TestContext 中。

    :param driver_name: 操作的对象名。
    :param action: 操作名称。
    :param element_name: 元素名称，用于存储查找结果。
    :param row_num: 行号，用于错误提示。
    :param logger: 日志对象。
    """
    logger.info(f"正在执行第{row_num}行，{element_name}={driver_name}.{action}()")
    check_value_and_raise(row_num, driver_name, '操作对象')
    setattr_(element_name, driver_func(driver_name, action))


def startswith_(driver_name, action, action_value, element_name, row_num, logger):
    """
    执行 keys.Test_KeyWords 中特定的操作（以$开头的为Context中的变量），并将结果存储在 TestContext 中。

    :param driver_name: 操作的对象名。
    :param action: 操作名称。
    :param action_value: 操作的值。
    :param element_name: 元素名称，用于存储查找结果。
    :param row_num: 行号，用于错误提示。
    :param logger: 日志对象。
    """
    logger.info(f"正在执行第{row_num}行，{element_name}={driver_name}.{action}({action_value})")
    action = action.replace("$", "")
    if driver_name is None:
        # 默认操作对象为driver
        driver_name = "driver"
    if not hasattr(TestContext, action):
        logger.error(f"第{row_num}行的action未定义")
        raise ValueError(f"第{row_num}行的action未定义")
    action_method = getattr_(action)  # 取到函数
    # 将函数分为是否需要action_value的两种情况
    params = inspect.signature(action_method).parameters
    if len(params) == 1:
        if element_name is not None:
            # 函数有返回值且需要保存
            setattr_(element_name,
                     action_method(getattr_(driver_name)))
        else:
            action_method(getattr_(driver_name))
    elif len(params) == 2:
        if element_name is not None:
            setattr_(element_name,
                     action_method(getattr_(driver_name), action_value))
        else:
            action_method(getattr_(driver_name), action_value)


def print_(action_value, row_num, logger):
    """
    打印变量值。如果值以 '$' 开头，那么从 TestContext 中获取；否则，直接打印值。

    :param action_value: 要打印的值或 TestContext 中的变量名。
    :param row_num: 行号，用于错误提示。
    :param logger: 日志对象。
    """
    logger.info(f"正在执行第{row_num}行，print({action_value})")
    action_value_ = action_value
    if action_value.startswith("$"):
        try:
            action_value_ = getattr_(action_value[1:])
        except Exception as e:
            logger.error(f"{e}\n没有找到变量{action_value[1:]}")
    logger.info(f"{action_value} = {action_value_}")


# 创建一个映射，将操作名称映射到对应的函数和参数名。
action_map = {
    'find': (
        find, ['driver', 'wait', 'action_type', 'selector', 'selector_value', 'element_name', 'row_num', 'logger']),
    'click': (click, ['driver_name', 'action', 'row_num', 'logger']),
    'find_and_click': (
        find_and_click,
        ['driver_name', 'wait', 'action_type', 'selector', 'selector_value', 'element_name', 'row_num', 'logger']),
    'find_in_elm': (
        find_in_elm,
        ['driver_name', 'wait_time', 'action_type', 'selector', 'selector_value', 'element_name', 'row_num', 'logger']),
    'send_keys': (send_keys, ['driver_name', 'action', 'action_value', 'row_num', 'logger']),
    'get_attribute': (get_attribute_, ['driver_name', 'element_name', 'action', 'action_value', 'row_num', 'logger']),
    'assert': (assert_, ['driver_name', 'assert_type', 'assert_value', 'row_num', 'logger']),
    'page_source': (page_source_, ['driver_name', 'action', 'element_name', 'row_num', 'logger']),
    'wait_activity': (wait_activity_, ['driver_name', 'action', 'action_value', 'row_num', 'logger']),
    'print': (print_, ['action_value', 'row_num', 'logger']),
}


def actuator(sheet_name, excel_path):
    """
    逐行执行测试步骤。
    该函数在test_case软件包中被调用。

    :param sheet_name: Excel 工作表名称，包含测试步骤。从@pytest.mark.parametrize("sheet_name", get_all_test_sheet_name(excel_path))获取。
    :param excel_path: 测试用例的 Excel 文件路径。
    """
    logger = next(mylogging(sheet_name))
    # 获取测试设备及driver
    driver = getattr(TestContext, "driver")
    wait_time = 5
    wait = WebDriverWait(driver, wait_time)
    # 获取测试用例
    excel = Excel(excel_path)
    test_case_data = excel.read_case_excel(sheet_name)

    for index, i in enumerate(test_case_data):
        keys = list(i.keys())
        action = i.get(keys[0]) or None
        action_type = i.get(keys[1]) or None
        selector = i.get(keys[2]) or None
        selector_value = i.get(keys[3]) or None
        element_name = i.get(keys[4]) or None
        driver_name = i.get(keys[5]) or 'driver'
        action_value = i.get(keys[6]) or None
        assert_type = i.get(keys[7]) or None
        assert_value = i.get(keys[8]) or None
        row_num = index + 1  # 索引从0开始，所以加1
        # 执行操作
        # find,click,find_and_click,send_keys,get_attribute_,assert,page_source
        if action.startswith("$"):
            startswith_(driver_name, action, action_value, element_name, row_num, logger)
            continue
        # 为避免冗长的if-else，用字典模拟switch-case
        # 从映射中获取操作对应的函数和参数名。
        func, arg_names = action_map[action]
        args = {}
        # 根据参数名获取参数值。
        for name in arg_names:
            value = locals()[name]
            args.update({name: value})
        # 使用获取的参数值调用函数。
        func(**args)
