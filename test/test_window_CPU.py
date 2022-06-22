import pytest
from TEST_BD_ARM.main import Objects

class WindowCPU(Objects):
    def get_name_cpu(self):
        with open(Objects.objPath[:Objects.objPath.rfind('site')]+'site\\ipu1\\objects.xml', encoding='utf-8') as objs:
            for line in objs:
                if 'objtype="ЦП"' in line:
                    return Objects.val(line, 'name', end = ' ob')[1:-1]
                    
    def get_feu_objs(self):
        with open(Objects.objPath[:Objects.objPath.rfind('site')]+'site\\ipu1\\feu_objects.xml', encoding='utf-8') as FO:
            return [Objects.val(_, 'name', end = ' ob')[1:-1] for _ in FO if '"ЦП_side"' in _ or '"Межпроцессорная_связь"' in _]
            
    def window_cpu():
        window ,= [(x['Coordinates'],x['RightBottom']) for x in Objects('SubType=Экран','Coordinates','RightBottom').VarsObjs if 'Диагностика ЦП' in x['Name']]
        return window
        
    def add_dict_vars_obj(self,dict_,obj, name, title=False):
        if name == 'Coordinates' or name == 'RightBottom':
            dict_[Objects.val(obj,'Name')].update({name:Objects.val(obj,name)[1:-1].split(',')})
        elif title == True:
            dict_.update({Objects.val(obj,name):{}})
        else:
            dict_[Objects.val(obj,'Name')].update({name:Objects.val(obj,name)})

    def set_dict_objs(self):
        self.VarsObjs = dict()
        with open(Objects.get_stnPath(), encoding='utf-8') as stn:
            #stn = stn.read().split('create universal')
            for obj in stn.read().split('create universal'):
                #dictVarsObj = dict()
                if self.typeObj in obj:
                    self.add_dict_vars_obj(self.VarsObjs,obj, 'Name', title=True)
                    self.add_dict_vars_obj(self.VarsObjs,obj, 'Name')
                    for var in self.varsObj:
                        self.add_dict_vars_obj(self.VarsObjs,obj, var)
                    if int(self.VarsObjs[Objects.val(obj,'Name')]['Coordinates'][0]) < int(WindowCPU.window_cpu()[0][0]) or int(self.VarsObjs[Objects.val(obj,'Name')]['Coordinates'][1]) < int(WindowCPU.window_cpu()[0][1]):
                        continue
                    if int(self.VarsObjs[Objects.val(obj,'Name')]['Coordinates'][0]) > int(WindowCPU.window_cpu()[1][0]) or int(self.VarsObjs[Objects.val(obj,'Name')]['Coordinates'][1]) > int(WindowCPU.window_cpu()[1][1]):
                        continue
                    #self.VarsObjs +=(dictVarsObj,)





cpu = WindowCPU('SubType=cpu','MainEbilockObject', 'Coordinates','Ident')
diag_tables = WindowCPU('SubType=Диагностическая_таблица_ЦП','MainEbilockObject', 'Coordinates','Ident','Side2','LAN_side','Межпроцессорная_связь')
diag_cpu = WindowCPU('SubType=Диагностика_ЦПУ-ЭЛ','MainEbilockObject', 'Coordinates','Ident','Side2','ЦП')
table_conn_between_cpu = WindowCPU('SubType=Таблица_связей_между_ЦП','MainEbilockObject', 'Coordinates','Ident','Таблица')

@pytest.mark.parametrize('var', diag_tables.VarsObjs.values())
def test_correct_linked_diag_tables(var):
    out = f"Проверь привязку диагностической таблицы ЦП {var['Name'], var['MainEbilockObject']}"
    assert var['MainEbilockObject'] in diag_tables.get_feu_objs() and var['MainEbilockObject'].startswith('IPU') and var['MainEbilockObject'].endswith(var['Name']), out

@pytest.mark.parametrize('var', diag_tables.VarsObjs.values())
def test_correct_link_diag_tables(var):
    out = f"Проверь links диагностической таблицы ЦП {var['Name'], var['MainEbilockObject']}"
    assert (var['Side2'] == diag_tables.VarsObjs[str(int(var['Name'])%2+1)]['Ident'] and 
            var['LAN_side'] == diag_cpu.VarsObjs[var['Name']]['Ident'] and 
            var['Межпроцессорная_связь'] == table_conn_between_cpu.VarsObjs[var['Name']]['Ident']), out

@pytest.mark.parametrize('var', diag_cpu.VarsObjs.values())
def test_correct_linked_diag_cpu(var):
    out = f"Проверь привязку диагностики ЦП {var['Name'], var['MainEbilockObject']}"
    assert var['MainEbilockObject'] in diag_tables.get_feu_objs() and var['MainEbilockObject'].startswith('IPU') and var['MainEbilockObject'].endswith(var['Name']) and var['ЦП'] == diag_tables.get_name_cpu(), out

@pytest.mark.parametrize('var', diag_cpu.VarsObjs.values())
def test_correct_link_diag_cpu(var):
    out = f"Проверь links диагностики ЦП {var['Name'], var['MainEbilockObject']}"
    assert var['Side2'] == diag_cpu.VarsObjs[str(int(var['Name'])%2+1)]['Ident'], out

@pytest.mark.parametrize('var', table_conn_between_cpu.VarsObjs.values())
def test_correct_linked_table_conn_between_cpu(var):
    out = f"Проверь привязку таблицы связей между ЦП {var['Name'], var['MainEbilockObject']}"
    assert var['MainEbilockObject'] in diag_tables.get_feu_objs() and var['MainEbilockObject'].startswith('Межпроцессорная_связь_') and var['MainEbilockObject'].endswith(var['Name']), out

@pytest.mark.parametrize('var', table_conn_between_cpu.VarsObjs.values())
def test_correct_link_table_conn_between_cpu(var):
    out = f"Проверь links диагностики ЦП {var['Name'], var['MainEbilockObject']}"
    assert var['Таблица'] == table_conn_between_cpu.VarsObjs[str(int(var['Name'])%2+1)]['Ident'], out