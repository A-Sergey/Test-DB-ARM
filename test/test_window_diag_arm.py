import pytest
from TEST_BD_ARM.main import Objects

class WindowDiagArm(Objects):

    def get_feu_objs():
        with open(Objects.objPath[:Objects.objPath.rfind('site')]+'site\\ipu1\\feu_objects.xml', encoding='utf-8') as FO:
            return [Objects.val(_, 'name', end = ' ob')[1:-1] for _ in FO if '<obj objnum' in _]

    def window_diag_arm():
        window ,= [(x['Coordinates'],x['RightBottom']) for x in Objects('SubType=Экран','Coordinates','RightBottom').VarsObjs if 'Диагностика АРМов и серверов, схема локальной сети' in x['Name']]
        return window
        
    def set_dict_objs(self):
        with open(Objects.get_stnPath(), encoding='utf-8') as stn:
            stn = stn.read().split('create universal')
            for obj in stn:
                dictVarsObj = dict()
                if self.typeObj in obj:
                    self.add_dict_vars_obj(dictVarsObj,obj, 'Name')
                    self.add_dict_vars_obj(dictVarsObj,obj, 'Ident')
                    for var in self.varsObj:
                        self.add_dict_vars_obj(dictVarsObj,obj, var)
                    if int(dictVarsObj['Coordinates'][0]) < int(WindowDiagArm.window_diag_arm()[0][0]) or int(dictVarsObj['Coordinates'][1]) < int(WindowDiagArm.window_diag_arm()[0][1]):
                        continue
                    if int(dictVarsObj['Coordinates'][0]) > int(WindowDiagArm.window_diag_arm()[1][0]) or int(dictVarsObj['Coordinates'][1]) > int(WindowDiagArm.window_diag_arm()[1][1]):
                        continue
                    self.VarsObjs +=(dictVarsObj,)
     
    def get_name_cpu(self):
        with open(Objects.objPath[:Objects.objPath.rfind('site')]+'site\\ipu1\\objects.xml', encoding='utf-8') as objs:
            for line in objs:
                if 'objtype="ЦП"' in line:
                    return Objects.val(line, 'name', end = ' ob')[1:-1]
    
    def sorted_by_X(self):
        _listCoord = [int(_['Coordinates'][0]) for _ in self.VarsObjs]
        _listCoord.sort()
        _sorted_VarsObjs = ()
        _VarsObjs = self.VarsObjs
        count = 0
        for _ in _listCoord:
            count += 1
            for obj in _VarsObjs:
                if obj['Coordinates'][0] == str(_):
                    obj['count'] = count
                    _sorted_VarsObjs += (obj,)
                    
                    break
        return _sorted_VarsObjs
    
    def get_sorted_by_X(self,linked,tmp):
        count = 0
        for _ in self.sorted_by_X():
            if _[linked] == tmp:
                _['count'] = count
                count += 1
                yield _
                
        
        

diag_sys_unit = Objects('SubType=Диагностика_системных_блоков','MainEbilockObject',)
select_client = Objects('SubType=Выбор клиента','MainEbilockObject', 'таблица', 'IsServer',)
list_work_places = Objects('SubType=Список_рабочих_мест','MainEbilockObject', 'client', 'server')
servers = WindowDiagArm('SubType=Сервер','MainEbilockObject','Coordinates')
cpu = WindowDiagArm('SubType=cpu','MainEbilockObject','Coordinates','side_1','side_2','tsap_1','tsap_2')
conn_between_servers = WindowDiagArm('SubType=Связь_между_серверами','MainEbilockObject','Coordinates', 'From', 'To')
conn_between_cpu_servers = WindowDiagArm('SubType=Связь_между_ЦП_и_сервером','MainEbilockObject','Coordinates', 'From', 'To')
conn_between_client_servers = WindowDiagArm('SubType=Связь_между_клиентом_и_сервером','MainEbilockObject','Coordinates', 'From','ServerNum')

with open(Objects.objPath[:Objects.objPath.rfind('site')]+'\\main\\addons\\server.xml',encoding='utf-8') as clients:
    clients = [Objects.val(_, 'name', end = ' obj')[1:-1] for _ in clients if '<obj objnum' in _ and 'Подсоединение_клиентов' in _]

def test_correct_diag_sys_unit():
    out = f"Не верно привязан {diag_sys_unit.typeObj}"
    assert diag_sys_unit.VarsObjs[0]['MainEbilockObject'] == 'СервОСН', out

@pytest.mark.parametrize('var', select_client.VarsObjs,ids=select_client.get_ids())
def test_correct_link_select_client(var):
    out = f"Не верный link {var['Name']}"
    assert var['таблица'] == diag_sys_unit.VarsObjs[0]['Ident'],out

@pytest.mark.parametrize('var', select_client.VarsObjs,ids=select_client.get_ids())
def test_is_server_of_select_client(var):
    out = f"Не верный параметр isServer {var['Name']}"
    if 'Серв' in var['Name']:
        assert var['IsServer'] == '1',out
    else:
        assert var['IsServer'] == '0',out

def test_correct_linked_list_work_places():
    #out = f"Не верный параметр isServer {var['Name']}"
    assert list_work_places.VarsObjs[0]['MainEbilockObject'] in clients, 'Не верно MainEbilockObject'
    assert list_work_places.VarsObjs[0]['client'] in clients, 'Не верно client'
    assert list_work_places.VarsObjs[0]['server'] == 'СервОСН', 'Не верно server'

@pytest.mark.parametrize('var', select_client.VarsObjs,ids=select_client.get_ids())
def test_is_server_of_select_client(var):
    out = f"Не верный параметр isServer {var['Name']}"
    if 'Серв' in var['Name']:
        assert var['IsServer'] == '1',out
    else:
        assert var['IsServer'] == '0',out

@pytest.mark.parametrize('var', servers.VarsObjs,ids=servers.get_ids())
def test_correct_linked_servers(var):
    assert var['MainEbilockObject'] == var['Name']

@pytest.mark.parametrize('var', cpu.VarsObjs,ids=cpu.get_ids())
def test_correct_linked_cpu(var):
    try:
        list_feu_objs = WindowDiagArm.get_feu_objs()
        list_feu_objs.remove(var['side_1'])
        list_feu_objs.remove(var['side_2'])
        list_feu_objs.remove(var['tsap_1'])
        list_feu_objs.remove(var['tsap_2'])
    except ValueError:
        assert False, 'Проверить привязку cpu'
    assert var['MainEbilockObject'] == cpu.get_name_cpu()

@pytest.mark.parametrize('var', conn_between_servers.VarsObjs,
                        ids=conn_between_servers.get_ids())
def test_correct_linked_conn_between_servers(var):
    assert var['From'] == 'СервОСН'
    assert var['To'] == 'СервРЕЗ'

@pytest.mark.parametrize('var', conn_between_cpu_servers.sorted_by_X(),
                        ids=map(lambda x: x['Ident'],
                                conn_between_cpu_servers.sorted_by_X())
                        )
def test_correct_linked_conn_between_cpu_servers(var):
    if var['count'] < 3:
        assert var['From'] == conn_between_cpu_servers.get_name_cpu() and var['To'] == 'СервОСН'
    else:
        assert var['From'] == conn_between_cpu_servers.get_name_cpu() and var['To'] == 'СервРЕЗ'

@pytest.mark.parametrize('var', clients)
def test_correct_linked_conn_between_client_servers_from(var):
    for obj in conn_between_client_servers.get_sorted_by_X('From',var):
        assert obj['From'] == var, f"Не правильная привязка From {var}"
        assert '-1' == obj['MainEbilockObject'] and obj['From'].upper() == obj['Name'].upper(), f"Проверь имя или MainEbilockObject ID={obj['Ident']}"

@pytest.mark.parametrize('var', clients)
def test_correct_linked_conn_between_client_servers_ServerNum(var):
    for obj in conn_between_client_servers.get_sorted_by_X('From',var):
        if obj['count'] == 0:
            assert obj['ServerNum'] == '0', f"Не верный параметр ServerNum {var}. Выставить 0"
        elif obj['count'] == 1:
            assert obj['ServerNum'] == '1', f"Не верный параметр ServerNum {var}. Выставить 1"
        else:
            assert False, f"Имеются повторы в клиентах {var}"