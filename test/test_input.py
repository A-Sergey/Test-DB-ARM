import pytest,os
from TEST_BD_ARM.main import Objects

class Input(Objects):
    dic_objs = dict()
    def __init__(self,typeObj, *varsObj):
        super().__init__(typeObj, *varsObj)
        self.get_input_in_objsXml()

    def add_dict_vars_obj(self,dict_,obj, name):
        if name in ['LeftTop','RightBottom','LeftUp','RightDown','Center']:
            dict_.update({name:Input.val(obj,name,',')[1:]})
        else:
            dict_.update({name:Input.val(obj,name)})
    
    def get_input_in_objsXml(self):
        with open(Input.objPath, encoding='utf-8') as obj:
            for line in obj:
                if 'Признак_' in line:
                    name = line[line.find('name=')+6:line.find('"',line.find('name=')+7)]
                    objtype = line[line.find('objtype=')+9:line.find('"',line.find('objtype=')+10)]
                    Input.dic_objs[name]=Input.alarm(objtype, Input.objPath)
            return(Input.dic_objs)
        
    @classmethod
    def get_rel_screen(cls):
        __screens = ()
        with open(cls.get_stnPath(), encoding='utf-8') as stn:
            stn = stn.read().split('create universal')
            for obj in stn:
                dictVarsObj = dict()
                if 'SubType=Экран\n' in obj and 'Name=Релейные' in obj:
                    dictVarsObj.update({'Name':Objects.val(obj, 'Name')})
                    dictVarsObj.update({'LeftTop':Objects.val(obj, 'LeftTop',',')[1:]})
                    dictVarsObj.update({'RightBottom':Objects.val(obj, 'RightBottom',',')[1:]})
                    __screens += (dictVarsObj,)
            if __screens == (): raise('Нет экрана релейных входов')
            return(__screens)

contact = Input('SubType=Контакт\n','MainEbilockObject','Coordinates','Center',
                'alarm_button','ttable','Аларм',)
user_mark = Input('SubType=Пользовательская_разметка\n','MainEbilockObject',
                   'Coordinates','LeftUp','RightDown')
time_table = Input('SubType=Таблица_времен\n','MainEbilockObject','Coordinates',
                    'Сосед',)

def test_absence_old_realisation():
    out = f"Старая реализация команд на релейных входах"
    commAlarm = Input.grep(["'<commtype", "name=\"Признак_аларма\">'"],"-hrA18")
    assert ('Убрать_аларм' not in commAlarm and 'Аларм_' not in commAlarm), out


@pytest.mark.parametrize('var', contact.VarsObjs, ids=contact.get_ids())
def test_correct_name_with_linked(var):
    out = f"Не верная привязка контакта {var['Name']}"
    assert (var['Name'] == var['MainEbilockObject'] or var['Name']+'_' in var['MainEbilockObject']), out

@pytest.mark.skipif(absent_diag_contact == False, reason='Absent diag contact')
@pytest.mark.parametrize('var', contact.VarsObjs, ids=contact.get_ids())
def test_correct_linked_table_alarm_button(var):
    out = f"{var['Name']} Необходимо проверить link alarm_button"
    __rel_status_ident = ()
    for screen in Input.get_rel_screen():
        for u_m in user_mark.VarsObjs:
            if int(u_m['LeftUp']) > int(screen['LeftTop']) and int(u_m['RightDown']) < int(screen['RightBottom']):
                __rel_status_ident += ((u_m['Ident'],int(screen['LeftTop']),int(screen['RightBottom'])),)
    for r_s in __rel_status_ident:
        if int(var['Center']) > r_s[1] and int(var['Center']) < r_s[2]:
            assert var['alarm_button'] == r_s[0], out

@pytest.mark.skipif(absent_diag_contact == True, reason='Absent diag contact')
@pytest.mark.parametrize('var', contact.VarsObjs, ids=contact.get_ids())
def test_correct_linked_table_ttable(var):
    out = f"{var['Name']} Необходимо проверить link ttable"
    __table = [[],[]]
    for t_t in time_table.VarsObjs:
        __table[0] += [t_t['Ident']]
        if t_t['Сосед'] != '-1':
            __table[1] += [t_t['Сосед']]
    __table_time_ident = list(set(__table[0]) - set(__table[1]))[0]
    assert var['ttable'] == __table_time_ident, out

@pytest.mark.parametrize('var', contact.VarsObjs, ids=contact.get_ids())
def test_correct_alarm_stn_objs(var):
   out = f"{var['Name']} не соответствуют алармы"
   try:
       assert var['Аларм'] == contact.dic_objs[var['Name']], out
   except KeyError:
       assert False, f"{var['Name']} отсутствует в object.xml"

@pytest.mark.parametrize('var', contact.dic_objs)
def test_absence_input_in_stn(var):
    dictStn = {_['Name']:_['Ident'] for _ in contact.VarsObjs}
    try:
        dictStn[var]
    except KeyError as err:
        assert False, f"{var} отсутствует в .stn"