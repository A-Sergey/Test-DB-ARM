import pytest
from TEST_BD_ARM.main import Objects
import xml.etree.ElementTree as ET

class WindowUps(Objects):
    def ups_objs():
        with open(WindowUps.objPath[:Objects.objPath.rfind('site')]+'station.snmp', encoding='utf-8') as UPS:
            ups_objs = [Objects.val(_, '<obj name', end = ' t')[1:-1] for _ in UPS if '<obj name=' in _ and 'ИБП' in _]
            return ups_objs
    
    def window_UPS():
        window_UPS ,= [x['Coordinates'] for x in Objects('SubType=Экран','Coordinates').VarsObjs if x['Name'] == 'Мониторинг ИБП']
        return window_UPS

main_ups = WindowUps('SubType=Main UPS','MainEbilockObject','Coordinates')
small_ups = WindowUps('SubType=Small UPS','MainEbilockObject','Coordinates')
table_ups = WindowUps('SubType=UPS table','MainEbilockObject','Coordinates')
all_ups = [x['MainEbilockObject']for x in main_ups.VarsObjs + small_ups.VarsObjs if int(x['Coordinates'][0])>int(WindowUps.window_UPS()[0]) and int(x['Coordinates'][1])>int(WindowUps.window_UPS()[1])]
ups_xml = ET.parse(WindowUps.objPath[:Objects.objPath.rfind('site')]+'station.snmp').getroot()


def test_link_ups():
    out = f"Отсутствует привязка прибора"
    union = set(all_ups) - set(WindowUps.ups_objs())
    assert union == set(), out

def test_link_ups_table():
    out = f"Отсутствует привязка таблицы"
    table_ups_list = [x['MainEbilockObject'] for x in table_ups.VarsObjs]
    union = set(table_ups_list) - set(WindowUps.ups_objs())
    assert union == set(), out

def test_absence_ups_in_window():
    out = f"Отсутствуе ИБП в окне мониторинга"
    union = set(WindowUps.ups_objs()) - set(all_ups)
    assert union == set(), out

def test_correct_param_snmp_ipu():
    out = f"Не верные параметры тэга ipu в station.snmp"
    assert (ups_xml.findall('ipu')[0].get('num') == '100' and
            ups_xml.findall('ipu')[0].get('connections') == '3' and
            ups_xml.findall('ipu')[0].get('cycle_delay') == '2000')

@pytest.mark.parametrize('var', ups_xml.findall('connection'))
def test_correct_param_snmp_connection(var):
    out = f"Не верные параметры тэга connection {var.findall('obj')[0].get('name')} в station.snmp"
    if 'ИБП' in var.findall('obj')[0].get('type'):
        assert (var.get('update_period') == '5000' and
                var.get('max_vars_in_pdu') == '5' and
                var.get('num_attempts') == '2' and
                var.get('protocol') == 'v2c'), out
    if 'MOPT652019M' in var.findall('obj')[0].get('type'):
        assert (var.get('update_period') == '10000' and
                var.get('max_vars_in_pdu') == '5' and
                var.get('num_attempts') == '2'), out
    if 'Nport' in var.findall('obj')[0].get('type'):
        assert (var.get('update_period') == '5000' and
                var.get('max_vars_in_pdu') == '5' and
                var.get('num_attempts') == '2'), out