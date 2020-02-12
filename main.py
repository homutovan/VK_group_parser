import requests
from pprint import pprint
import json
import time
from collections import Counter
from colorama import Fore
from colorama import Style

TOKEN = '73eaea320bdc0d3299faa475c196cfea1c4df9da4c6d291633f9fe8f83c08c4de2a3abf89fbc3ed8a44e1'
VERSION = '5.103'

from code import code_vk, code_get_info, code_group_info
                
def progress(count, end_count):
    try:
        rate = (90 * count) // end_count
    except ZeroDivisionError:
        rate = 0    
    print(f'Ввполнено {rate} %','#' * rate, end = '')
    return

def stabilizer(decor_method):
    def wrapper(self, *args, **kwargs):    
        while True:
            try:
                result = decor_method(self, *args, **kwargs)['response']
                break
            except Exception as e:
                print(f'{Fore.RED}При обработке запроса возникла ошибка: {e}, повторяю запрос{Style.RESET_ALL}')
                print(decor_method(self, *args, **kwargs)['error'])
        return result
    return wrapper

class User:

    request_time = 0
          
    def __init__(self, user_ids):
        self.user_ids = user_ids
        self.token = self.get_token()
        self.user_info = self.get_info()
        self.user_id = self.user_info['id']
        self.friends_list = self.user_info['friends']
        self.groups = set(self.user_info['groups'])
        self.group_count = 0
        self.group_list = 0
        
    def get_token(self):
        try:
            from ssecret import TOKEN as token
        except (ModuleNotFoundError, ImportError):
            print(f'{Fore.RED}Файл с секретным ключом отсутствует, использую ключ по умолчанию{Style.RESET_ALL}')
            token = TOKEN
        return token
    
    def timer(self):
        timeout = 0
        if (time.time() - User.request_time) < 0.35:
            timeout = 0.35 - (time.time() - User.request_time)
            print(f'{Fore.CYAN}Ожидание запроса: {round(timeout, 3)} сек{Style.RESET_ALL}')
            time.sleep(timeout) 
        print(f'{Fore.BLUE}Запрос к API VK{Style.RESET_ALL}\r', end = '')         
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
        return requests.get(f'https://api.vk.com/method/execute', params).json()
    
    def get_info(self):
        params = dict(code = code_get_info)        
        return self.requester(params)
           
    def group_info(self, group_list):
        params = dict(code = code_group_info,
                      group_ids = str(group_list)[1: -1])
        return self.requester(params)
    
    def friend_parser(self, group_count = Counter()):
        params = dict(code = code_vk,
                      user_id = self.user_id)
        resp = self.requester(params)
        group_count += Counter(resp[0])
        if resp[1] != len(self.friends_list):
            progress(resp[1], len(self.friends_list))
            self.friend_parser(group_count)    
        self.group_count = group_count
        return None
    
    def correlator(self, friends_number = 3):
        if self.group_count == 0:
            self.friend_parser()
        self.group_list = list(Counter(self.groups) & Counter({key: value for key, value in self.group_count.items() if value < friends_number}))
        return self.group_list
    
    def decorrelator(self):
        if self.group_count == 0:
            self.friend_parser()
        self.group_list = list(Counter(self.groups) - self.group_count)
        return self.group_list

menu_string = f'{Fore.YELLOW}Сменить пользователя - [r], завершить работу - [q], поиск групп пользователя, не содержащих друзей - [dc], поиск групп, содержащих заданное число друзей - [c]: {Style.RESET_ALL}\n'

sub_menu_string = f'{Fore.YELLOW}, вывод результатов на дисплей - [d], запись результатов в файл - [f]: {Style.RESET_ALL}\n'

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
            except:
                print(f'{Fore.RED}Пользователь с указанным USER ID отсутствует в системе, повторите ввод{Style.RESET_ALL}')
        return self.user
    
    def greeter(self):
        print(f'\nUser ID: {Fore.GREEN}{self.user.user_info["id"]}{Style.RESET_ALL} Пользователь: {Fore.GREEN}{self.user.user_info["first_name"]} {self.user.user_info["last_name"]}{Style.RESET_ALL}') 
        print(f'Всего друзей: {Fore.GREEN}{len(self.user.user_info["friends"])}{Style.RESET_ALL} Всего групп: {Fore.GREEN}{len(self.user.user_info["groups"])}{Style.RESET_ALL}')
        return None
    
    def file_writer(self, groups_info_list, filename = 'json_file'):
        with open(filename, 'w', encoding='utf8') as write_file:
           json.dump(groups_info_list, write_file, ensure_ascii = False)
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
            if self.user.group_list != 0:
                self.submenu(instruction)
                instruction_string = menu_string[: -7] + sub_menu_string[5:]
            instruction = input(instruction_string)
            loop = self.main_menu(instruction)
            
        return None
    
if __name__ == '__main__':
    
    menu = Menu('Система статистических исследований ВК')


