import pytest
from selenium.common import TimeoutException

from actuator.Actuator import actuator
from excel.readExcel import get_all_test_sheet_name

excel_path = '../excel/data/data.xlsx'


@pytest.mark.parametrize("sheet_name", get_all_test_sheet_name(excel_path))
def test_dsw(sheet_name, android_driver):
    try:
        actuator(sheet_name, excel_path)
    except TimeoutException as e:
        print(e)
        print("请查看用例是否正确，元素没有定位到")
