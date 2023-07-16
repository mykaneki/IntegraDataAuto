import pytest

from actuator.Actuator import actuator
from excel.readExcel import get_all_test_sheet_name

excel_path = '../excel/data/data.xlsx'


@pytest.mark.parametrize("sheet_name", get_all_test_sheet_name(excel_path))
def test_dsw(sheet_name, android_driver):
    actuator(sheet_name,excel_path)

