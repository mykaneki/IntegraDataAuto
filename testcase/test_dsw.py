import logging
import os
from selenium.common import TimeoutException
from actuator.Actuator import actuator
from excel.readExcel import get_all_test_sheet_name


def test_dsw(pytestconfig, android_driver):
    excel_path = pytestconfig.getoption("excel_path")
    sheet_names = get_all_test_sheet_name(excel_path)
    for sheet_name in sheet_names:
        try:
            actuator(sheet_name, excel_path)
        except TimeoutException as e:
            print(e)
            print("请查看用例是否正确，元素没有定位到")





def setup_logger(test_name):
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger(test_name)
    logger.setLevel(logging.INFO)

    # 创建一个 FileHandler，用来将日志写入到文件中，并设置编码为 UTF-8
    file_handler = logging.FileHandler(f'logs/{test_name}.log', encoding='utf-8', mode='w')
    file_handler.setLevel(logging.INFO)

    # 创建一个 StreamHandler，用来将日志输出到控制台
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # 创建一个 Formatter，用来设置日志的格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    # 将 FileHandler 和 StreamHandler 添加到 logger 中
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

def test_example1():
    logger = setup_logger('test_example1')
    logger.info('This is an info message from test_example1')

def test_example2():
    logger = setup_logger('test_example2')
    logger.info('This is an info message from test_example2')