import pytest,os
from TEST_BD_ARM.main import Objects

komm = Objects('Коммутатор_ЛВС','SwitchType','Ports','Expansion')

@pytest.mark.parametrize('pattern', komm.VarsObjs, ids=komm.get_obj_id())
def test_correct_port(pattern):
    out = 'Не верное количество портов-'+pattern['Name']
    if pattern['SwitchType'] == '1':
        assert pattern['Ports'] == '8', out
    if pattern['SwitchType'] == '2' or pattern['SwitchType'] == '3':
        assert pattern['Ports'] == '10', out
    if pattern['SwitchType'] == '4':
        assert pattern['Ports'] == '28', out
    if pattern['SwitchType'] == '5':
        assert pattern['Ports'] == '18', out
    if pattern['SwitchType'] == '6':
        if pattern.get('Expansion') == '1':
            assert pattern['Ports'] == '19', out
        else:
            assert pattern['Ports'] == '13', out