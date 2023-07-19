from selenium.common import TimeoutException
from actuator.Actuator import actuator
from excel.readExcel import get_all_test_sheet_name


def test_main(pytestconfig, android_driver):
    excel_path = pytestconfig.getoption("excel_path")
    sheet_names = get_all_test_sheet_name(excel_path)
    for sheet_name in sheet_names:
        actuator(sheet_name, excel_path)
