import pytest,os
from TEST_BD_ARM.main import Objects

class OC(Objects):
    def __init__(self,typeObj, *varsObj):
        super().__init__(typeObj, *varsObj)
        self.identsTables = ()

    def sort_table(self):
        _list = []
        for table in self.VarsObjs:
            _list.append(int(table['Coordinates'][0]))
        _list.sort()
        for n in _list:
            for table in self.VarsObjs:
                if str(n) == table['Coordinates'][0]:
                    self.identsTables += (table['Ident'],)

    def get_obj_id(self,tmp):
        return([f'{tmp} ME={dic["MainEbilockObject"][dic["MainEbilockObject"].find("("):]} ID={dic["Ident"]}' for dic in self.VarsObjs if dic['Ident'] != None])

orders_status = OC('SubType=Список_переменных','MainEbilockObject','Coordinates','Ident','Next','Prev')

controllers = OC('SubType=Контроллер','MainEbilockObject','Ident','OC_Type','varlist',
                    )

mks = OC('SubType=Концентратор\n','MainEbilockObject','Ident','Boss','МКС-МУ_1','МКС-МУ_2',
         'Coordinates','disconnect_table',)
table_losses_ycu = OC('SubType=Таблица_потерь_связи_с_концентраторами','MainEbilockObject',
                        'Ident','graph',)
oc_plates = OC('SubType=Плата ','MainEbilockObject','SubType','Ident',)
unknown_ycu = OC('Неизвестный_концентратор\n','MainEbilockObject','table','Ident',)
table_unknown_ycu = OC('SubType=Таблица_неизвестных_концентраторов\n','MainEbilockObject',
                        'Ident',)
table_failed_ycu = OC('SubType=Таблица_сбойных_концентраторов\n','MainEbilockObject','Ident',
                        'disconnect_table',)

@pytest.mark.parametrize('var', orders_status.VarsObjs, ids=orders_status.get_obj_id('Table'))
def test_correct_linked_table(var):
    orders_status.sort_table()
    out = f"Не правильные линки на {orders_status.identsTables.index(var['Ident'])+1} таблице"
    if orders_status.identsTables.index(var['Ident']) == 0:
        assert (var['Next'] == '-1' and var['Prev'] == '-1'), out
    if orders_status.identsTables.index(var['Ident']) == 1:
        assert (var['Next'] == orders_status.identsTables[0] and var['Prev'] == '-1'), out
    if orders_status.identsTables.index(var['Ident']) == 2:
        assert (var['Next'] == orders_status.identsTables[1] and var['Prev'] == '-1'), out

@pytest.mark.parametrize('var', controllers.VarsObjs, ids=controllers.get_obj_id('OC'))
def test_correct_type_OC(var):
    out = f"Не верный тип ОК {var['MainEbilockObject']}"
    assert ((var['Name'].startswith('Ст') and var['OC_Type'] == '2') or
        (var['Name'].startswith('Св') and var['OC_Type'] == '1') or
        (var['Name'].startswith('Ре') and var['OC_Type'] == '3')), out
        
@pytest.mark.parametrize('var', controllers.VarsObjs, ids=controllers.get_obj_id('OC'))
def test_correct_link_to_varlist(var):
    out = f"Не правильная привязка OK varlist {var['MainEbilockObject']}"
    assert var['varlist'] == orders_status.identsTables[2], out

@pytest.mark.parametrize('var', mks.VarsObjs, ids=mks.get_obj_id('MKS'))
def test_correct_linked_mks(var):
    out = f"Не верная привязка {var['Name']} концентратора"
    out2 = f"'Декоративный концентратор {var['MainEbilockObject']} имеет привязку"
    if var['Name'] != '':
        if var['Boss'] == '-1':
            assert (var['Name']+'_' in var['MainEbilockObject']),out
            assert (var['Name']+'_1' in var['МКС-МУ_1']),out
            assert (var['Name']+'_2' in var['МКС-МУ_2']),out
        else:
            assert var['Name'] == '', f"Декоротивный концентратор {var['MainEbilockObject']} имеет название"
    else:
        assert (var['МКС-МУ_1'] == '-1' and var['МКС-МУ_2'] == '-1'), out2

def test_absent_table_losses_ycu():
    out = f"Не верное количество таблиц потерей связи"
    assert len(table_losses_ycu.VarsObjs) == 1, out
    
@pytest.mark.parametrize('var', mks.VarsObjs, ids=mks.get_obj_id('MKS'))
def test_correct_link_mks_to_varlist_disconnect_table(var):
    out = f"Не правильная привязка МКС disconnect_table {var['Name']}"
    if var['Name'] != '' and var['Boss'] =='-1':
        assert (var['disconnect_table'] == table_losses_ycu.get_first_obj()['Ident']),out
    else:
        assert (var['disconnect_table'] != table_losses_ycu.get_first_obj()['Ident']),out

@pytest.mark.parametrize('var', oc_plates.VarsObjs, ids=oc_plates.get_obj_id('Plate OC'))
def test_correct_type_plate(var):
    out = f"Не верный тип платы {var['Name']}"
    assert (('МУЭП' in var['SubType'] and var['MainEbilockObject'].startswith('Стр')) or
            ('МУОС' in var['SubType'] and var['MainEbilockObject'].startswith('Св')) or
            ('МУОР' in var['SubType'] and var['MainEbilockObject'].startswith('Рел'))), out

@pytest.mark.parametrize('var', unknown_ycu.VarsObjs, ids=unknown_ycu.get_obj_id('Unknown_ycu'))
def test_correct_linked_table_unknown_ycu(var):
    out = f"Не правильная привязка {var['Name']}"
    assert var['table'] == table_unknown_ycu.get_first_obj()['Ident'], out

def test_correct_linked_table_losses_ycu_main():
    out = f"Неверная привязка Таблица_потерь_связи_с_концентраторами(main)"
    assert table_losses_ycu.get_first_obj()['MainEbilockObject'] in mks.get_value_all_objs('MainEbilockObject'),out

def test_correct_linked_table_losses_ycu_graph():
    out = f"Неверная привязка Таблица_потерь_связи_с_концентраторами(graph)"
    assert table_losses_ycu.get_first_obj()['graph'] in ['YCU_statistics','Concentrator_statistics'],out

def test_correct_linked_table_failed_ycu():
    out = f"Неверный линк Таблицы сбойных концентраторов"
    assert table_failed_ycu.get_first_obj()['disconnect_table'] == table_losses_ycu.get_first_obj()['Ident'],out