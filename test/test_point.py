import pytest,os
from TEST_BD_ARM.main import Objects

class Point(Objects):
    def add_dict_vars_obj(self,dict_,obj, name):
        if name == 'Контроллер':
            dict_.update({name:Point.val(obj,name,'(').replace('Стр.','')})
        else:
            dict_.update({name:Point.val(obj,name)})

    def get_obj_id(self):
        return([f'Point {dic["Name"]}' for dic in self.VarsObjs if dic['Name'] != None])

points = Point('SubType=Стрелка\n','MainEbilockObject','Контроллер','Номер_платы_МУЭП',
                'Макет',)
pointSwitches = Point('SubType=Стрелочный_коммутатор','MainEbilockObject','OC',
                'Спаренная_стрелка',)

@pytest.mark.parametrize('var', points.VarsObjs, ids=points.get_ids())
def test_correct_linked_controller(var):
    out = 'К стрелке ' + var['Name'] + ' не верно привязан контроллер'
    if ('-1' not in var.get('MainEbilockObject')):
        if '/' not in var['Контроллер']:
            assert (var['MainEbilockObject'] in var['Контроллер']
                or var['Контроллер'] == var['MainEbilockObject']), out
        else:       
            assert (var['Name']+'/' in var['Контроллер']
                    or '/'+var['Name'] in var['Контроллер']), out

@pytest.mark.parametrize('var', points.VarsObjs, ids=points.get_ids())
def test_correct_number_plate(var):
    out = 'На стрелке №'+var['Name']+' не правильно выставлен номер платы'
    if var['Name'] in var['Контроллер'].split('/'):
        if var['Контроллер'].split('/').index(var['Name']) == 0:
            assert var['Номер_платы_МУЭП'] == '1',out
        elif var['Контроллер'].split('/').index(var['Name']) == 1:
            assert var['Номер_платы_МУЭП'] == '2',out

@pytest.mark.parametrize('var', points.VarsObjs, ids=points.get_ids())
def test_availability_of_all_point_switches(var):
    out = 'Отсутсвует стрелочный коммутатор '+ var['Name']
    count = 0
    for switch in pointSwitches.VarsObjs:
        if '/' in switch['Name']: 
            if var['Name'] in switch['Name'].split('/'): count = 1
        else:
            if switch['MainEbilockObject'] == var['MainEbilockObject']: count = 1
    assert count == 1, out

@pytest.mark.parametrize('var', points.VarsObjs, ids=points.get_ids())
def test_linked_to_maket(var):
    out = 'Стрелка №' + var['Name'] + ' не привязана к макету'
    assert var['Макет'] != '-1', out
    
@pytest.mark.parametrize('var', pointSwitches.VarsObjs, ids=pointSwitches.get_ids())
def test_correct_linked_point_switches(var):
    out = 'На стр. коммутаторе '+var['Name']+' не верно привязан контроллер'
    if '/' in var['Name']:
        assert 'Стр.'+var['Name']+'(' in var['OC'], out

@pytest.mark.parametrize('var', pointSwitches.VarsObjs, ids=pointSwitches.get_ids())
def test_correct_linked_point_couple_switches(var):
    out = 'На стр. коммутаторе '+var['Name']+' не верный параметр "Спаренная_стрелка"'
    if '/' in var['Name']:
        assert var['Спаренная_стрелка'] == '1',out
    else:
        assert var['Спаренная_стрелка'] == '0',out