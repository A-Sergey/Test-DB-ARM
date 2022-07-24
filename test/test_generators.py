import pytest
from TEST_BD_ARM.main import Objects

okde = Objects('SubType=ОКДЕ_ОК','MainEbilockObject', 'РЦ')

@pytest.mark.skipif(okde.VarsObjs == False, reason='Absent okde')
@pytest.mark.parametrize('var', okde.VarsObjs, ids=okde.get_ids())
def test_param_RC(var):
    out = f"Не верный параметр РЦ {var['Name']}"
    assert (('ОКДЕВ' not in var['Name'] and '1' == var['РЦ']) or
            ('ОКДЕВ' in var['Name'] and '0' == var['РЦ'])
            ), out
