from os import getcwd
from sys import argv
import os
import subprocess

class Objects():
    objPath = None
    
    def __init__(self, typeObj, *varsObj):
        self.typeObj = typeObj
        self.varsObj = varsObj
        self.VarsObjs = tuple()

        self.set_dict_objs()
        if self.VarsObjs == ():
            print(ValueError(f'Не найдены объекты типа {self.typeObj}'))
    
    def grep(pattern,flag="-rl",add=''):
        grep = ["grep",flag]+list(pattern)+[Objects.objPath[:Objects.objPath.rfind('site')]+add]
        result = subprocess.run(grep, stdout = subprocess.PIPE)
        return(str(result.stdout,'utf-8')[:-1])
        
    def alarm(objtype,wayObj):
    #wayObj -путь до object.xml
    #direc - путь до main
        direc = wayObj[:wayObj.find('site')]+'main'
        objtype = Objects.grep(("'\"" + objtype + "\"'").split(' '),'-hrA7','main').split('\n')
        num = 160
        for line in objtype:
            if 'alarm' in line and 'event code="160"' not in line:
                num = line[line.find('<event code="')+13:line.find('"',line.find('<event code="')+15)]
                break
        return(str(num))
                                    
    #Значение переменной name
    def val(obj, name, end = '\n'):
        return(obj[obj.find(name+'=')+(len(name)+1):obj.find(end,obj.find(name+'='))])
    
    def get_stnPath():
        return(Objects.objPath[:Objects.objPath.rfind('site')]+'station.stn')
    
    def add_dict_vars_obj(self,dict_,obj, name):
        if name == 'Coordinates' or name == 'RightBottom':
            dict_.update({name:Objects.val(obj,name)[1:-1].split(',')})
        else:
            dict_.update({name:Objects.val(obj,name)})
    
    def get_ids(self):
        if type(self.VarsObjs) == dict:
            return [f"{_['Ident']}" for _ in self.VarsObjs.values()]
        else:
            return([f"{value['Ident']}" for value in self.VarsObjs])
    
    def get_first_obj(self):
        if len(self.VarsObjs) == 1:
            return(self.VarsObjs[0])
        else:
            raise ValueError('Не верное количество объектов ' + self.typeObj)
            
    def get_value_all_objs(self, var):
        __values = ()
        for dic in self.VarsObjs:
            __values += (dic.get(var),)
        return(__values)

    def set_dict_objs(self):
        with open(Objects.get_stnPath(), encoding='utf-8') as stn:
            for obj in stn.read().split('create universal'):
                dictVarsObj = dict()
                if self.typeObj in obj:
                    self.add_dict_vars_obj(dictVarsObj,obj, 'Name')
                    self.add_dict_vars_obj(dictVarsObj,obj, 'Ident')
                    for var in self.varsObj:
                        self.add_dict_vars_obj(dictVarsObj,obj, var)
                    self.VarsObjs +=(dictVarsObj,)

if __name__ == "__main__":
    if 'objects.xml' in argv[1]:
        os.environ.update({'pathObj':argv[1]})
    testPath = argv[0][:argv[0].rfind('main')]+ 'test'
    proc = subprocess.run(['pytest','--tb=short', testPath], stdin = subprocess.PIPE,
                            stdout = subprocess.PIPE, text= True)
    print(proc.stdout)
    input('\nPress Enter for exit')
