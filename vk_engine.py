import requests
from pprint import pprint
import json
import time
from collections import Counter
from functools import lru_cache

TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
VERSION = '5.103'

from code import code_vk, code_get_info, code_group_info

def jprint(arg):
    print(f'{time.strftime("%H.%M.%S", time.localtime())} {arg}')

def stabilizer(decor_method):
    def wrapper(self, *args, **kwargs):
        User.request_premission = True
        User.except_counter = 0    
        while User.request_premission:
            try:
                response = decor_method(self, *args, **kwargs)
                result = response['response'] #Убеждаемся в наличии ключа response
                assert(response['response'] != None) #Убеждаемся в том, что значение ключа response не None
                User.request_premission = False 
                jprint('Ответ API VK')
                return result
            except requests.exceptions.ConnectionError:
                User.error_msg = 'ConnectionError'
                jprint(f'Ошибка соединения')
            except requests.exceptions.ReadTimeout: 
                User.error_msg = 'ReadTimeout'  
                jprint(f'Превышено время ожидания от API VK')
                User.except_counter += 2
            except KeyError:
                jprint('Ошибка ответа')
                User.error_msg = response['error']['error_msg']   
            except AssertionError:
                jprint('API VK не может обработать запрос')
                if 'execute_errors' in response:
                    User.error_msg = response['execute_errors'][0]['error_msg']
                else: 
                    User.error_msg = 'UnknownError'
            User.except_counter += 1
            if (User.except_counter > 10) or (User.error_msg == 'Invalid user id'):
                User.request_premission = False
        return None
    return wrapper
      
class User:
    
    request_premission = True
    except_counter = 0
    error_msg = 0    
    request_time = 0
          
    def __init__(self, user_ids):
        self.user_ids = user_ids
        self.token = self.get_token()
        self.user_info = self.get_info()
        self.user_id = self.user_info['id']
        self.friends_list = self.user_info['friends']
        self.groups = set(self.user_info['groups'])
        self.group_count = []
        self.group_list = []
        self.offset = 0
        
    def get_token(self):
        try:
            from secret import TOKEN as token
        except (ModuleNotFoundError, ImportError):
            jprint('Файл с секретным ключом отсутствует, использую ключ по умолчанию')
            token = TOKEN
        return token
    
    def timer(self):
        timeout = 0
        if (time.time() - User.request_time) < 0.35:
            timeout = 0.35 - (time.time() - User.request_time)
            jprint(f'Ожидание запроса: {round(timeout, 3)} сек')
            time.sleep(timeout) 
        jprint('Запрос к API VK')         
        User.request_time = time.time()
        return None
        
    def get_params(self):       
        return dict(access_token = self.token,
                    user_ids = self.user_ids,
                    v = VERSION)
                    
    @stabilizer
    def requester(self, params = None):
        if params == None:
            params = self.get_params()
        else:
            params.update(self.get_params())
        self.timer()
        return requests.get(f'https://api.vk.com/method/execute', params, timeout = 10).json()
    
    def get_info(self):
        params = dict(code = code_get_info)        
        return self.requester(params)
           
    def group_info(self, group_list):
        params = dict(code = code_group_info,
                      group_ids = str(group_list)[1: -1])
        return self.requester(params)
    
    @lru_cache(maxsize = 48)
    def friend_parser(self):                                    
        params = dict(code = code_vk,
                      user_id = self.user_id)
        resp = self.requester(params)
        if resp != None:
            self.offset = resp[1]
            if resp[1] != len(self.friends_list):
                self.friend_parser()
            self.group_count += resp[0]    
        return None
        
    def correlator(self, friends_number = 3):
        if len(self.group_count) < 1:
            self.friend_parser()
        self.group_list = list(Counter(self.groups) & Counter({key: value for key, value in Counter(self.group_count).items() if value < friends_number}))
        return self.group_list
    
    def decorrelator(self, arg = None):
        if len(self.group_count) < 1:
            self.friend_parser()
        self.group_list = list(Counter(self.groups) - Counter(self.group_count))
        return self.group_list

menu_string = f'Сменить пользователя - [r], завершить работу - [q], поиск групп пользователя, не содержащих друзей - [dc], поиск групп, содержащих заданное число друзей - [c]:\n'

sub_menu_string = f', вывод результатов на дисплей - [d], запись результатов в файл - [f]:\n'

class Menu:
    
    def __init__(self, name):
        self.name = name
        print(name)
        self.user = self.auth()
        self.loop = self.looper()
        print(f'Работа системы завершена')
        
    def auth(self):
        while True:
            try:
                user_id = input('\nВведите USER ID:')
                self.user = User(user_id)  
                break
            except TypeError:
                jprint(f'Возникла ошибка {User.error_msg}, повторите ввод')
        return self.user
    
    def greeter(self):
        print(f'\nUser ID: {self.user.user_info["id"]} Пользователь: {self.user.user_info["first_name"]} {self.user.user_info["last_name"]}') 
        print(f'Всего друзей: {len(self.user.user_info["friends"])} Всего групп: {len(self.user.user_info["groups"])}')
        return None
    
    def file_writer(self, groups_info_list, filename = 'json_file'):
        with open(filename, 'w', encoding='utf8') as write_file:
           json.dump(groups_info_list, write_file, ensure_ascii = False)
        print(f'Запись файла завершена')
        return None;
    
    def main_menu(self, instruction):
        if instruction == 'q':
            return False
            
        elif instruction == 'r':
            self.auth()
            
        elif instruction == 'c':
            self.user.correlator()
                
        elif instruction == 'dc':
            self.user.decorrelator()        
        return True
    
    def submenu(self, instruction):
        print(f'По вашему запросу найдено {len(self.user.group_list)} групп')
        if instruction == 'd':
            pprint(self.user.group_info(self.user.group_list))
                
        elif instruction == 'f':
            self.file_writer(self.user.group_info(self.user.group_list), filename = f'{self.user.user_info["last_name"]}.json')
        return None   
    
    def looper(self, loop = True):
        
        instruction_string = menu_string
        
        while loop:
             
            self.greeter()
            if len(self.user.group_list) != 0:
                self.submenu(instruction)
                instruction_string = menu_string[: -7] + sub_menu_string[5:]
            instruction = input(instruction_string)
            loop = self.main_menu(instruction)
            
        return None   
            
if __name__ == '__main__':
    
    menu = Menu('Система статистических исследований ВК')
