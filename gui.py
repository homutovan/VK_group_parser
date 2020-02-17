import PySimpleGUI as sg
import threading
from pprint import pprint
import json

from vk_engine import User

def file_writer(groups_info_list, filename = 'json_file'):
    try:
        with open(f'{filename}.json', 'w', encoding='utf8') as write_file:
            json.dump(groups_info_list, write_file, ensure_ascii = False)
        return f'Запись файла {filename} завершена'
        
    except PermissionError:
        return f'Укажите путь сохранения файла'
        
    except FileNotFoundError:
        return f'Неверный путь сохранения {filename}'
    

def gui():
    sg.theme(new_theme='Dark Blue 3')
    
    frame_auth_layout = [
        [sg.Text('Введите User ID пользователя VK'), sg.InputText(key = 'id', size = (15, 1)), sg.OK(key = 'ok_auth')]
    ]

    frame_user_layout = [
        [sg.Text('User ID:'), sg.Text(size = (8, 1),key = 'text_id'), sg.Text('Пользователь:'), sg.Text(size = (20, 1), key = 'text_name'), 
        sg.Button('Cменить пользователя', size = (12, 2), key = 'change')],
        [sg.Text('Всего друзей:'), sg.Text(size = (3, 1), key = 'text_friends'), sg.Text('Всего групп:'), sg.Text(key = 'text_group', size = (4, 1))]
    ]

    frame_action = [
        [sg.Button('Группы не содержашие друзей', key = 'decorrelator'),sg.Button('Группы содержащие заданное число друзей', key = 'correlator'), sg.Spin([i for i in range(1, 100)], size = (3, 1), initial_value = 1, key = 'spinner'), sg.Text('Число друзей')]
    ]

    frame_display = [
        [sg.Text('По вашему запросу найдено'), sg.Text(size = (3, 1), key = 'number_group'), sg.Text('групп')],
        [sg.Button('Вывод информации на дисплей', key = 'display'), sg.Button('Запись информации в файл', key = 'file')],
        [sg.Input(key = 'file_target'), sg.FolderBrowse(key = 'file_patch', button_text = 'Обзор')]
    ]
    
    frame_progress = [
          [sg.ProgressBar(max_value = 1000, orientation='h', size=(30, 20), key = 'progressbar'), sg.Text(size = (4, 1), key = 'percent'), sg.Text('%')]
    ]
    
    frame_output = [
        [sg.Output(key='hidden', size=(70, 10), visible=True)]
    ]

    layout = [
        [sg.Frame('Ввод пользователя', frame_auth_layout, key = 'frame_auth')],
        [sg.Frame('Данные пользователя', frame_user_layout, visible = False, key = 'frame_user_info')],
        [sg.Frame('Поиск и анализ групп пользователя', frame_action, visible = False, key = 'frame_action')],
        [sg.Frame('Получение данных', frame_progress, visible = True, key = 'progress')],
        [sg.Frame('Вывод полученной информации', frame_display, visible = True, key = 'frame_display')],
        [sg.Frame('Мониторинг процесса', frame_output, visible = True, key = 'frame_output')],
        [sg.Quit(button_text = 'Выход')],
    ]

    window = sg.Window('Программа', layout, element_justification = 'left')
    progress_bar = window['progressbar']
    
    while True:
        group_list = []       
        event, values = window.read(timeout = 100)
        
        if 'user' in locals():
            group_list = user.group_list
            window['frame_user_info'].update(visible = True)
            #window['frame_user_info'].unhide_row()
            window['frame_action'].update(visible = True)
            #window['frame_action'].unhide_row()
            #window['frame_auth'].hide_row()
            window['frame_auth'].update(visible = False)
            window['text_id'].update(user.user_info['id'])
            window['text_name'].update(user.user_info['first_name']+ ' ' + user.user_info['last_name'])
            window['text_friends'].update(len(user.user_info["friends"]))
            window['text_group'].update(len(user.user_info["groups"]))
            window['progress'].update(visible = True)
            progress_bar.UpdateBar(user.offset, max = len(user.friends_list))
            window['percent'].update(round(float(user.offset * 100 / (len(user.friends_list) + 0.0001)), 2))
            
        else:
            window['frame_user_info'].update(visible = False)
            #window['frame_user_info'].hide_row()
            window['frame_action'].update(visible = False)
            #window['frame_action'].hide_row()
            window['frame_auth'].update(visible = True)
            #window['frame_auth'].unhide_row()
            window['progress'].update(visible = False)
            
        if len(group_list) > 0:
            window['frame_display'].update(visible = True)
            window['number_group'].update(len(user.group_list))
        else:
            window['frame_display'].update(visible = False)
            
        #print(event, values)
        if event in (None, 'Exit', 'Выход', 'Cancel'):
            break
        if event == 'ok_auth':
            try:
                user = User(values['id'])
                window['change'].update(disabled = False)
            except TypeError:
                sg.Popup(f'Возникла ошибка {User.error_msg}, повторите ввод')
                continue

        if event == 'change':
            del user
            window['change'].update(disabled = True)
        
        if event == 'correlator':
            threaded = FuncThread(user.correlator, int(values['spinner']))
            threaded.start()
            
        if event == 'decorrelator':
            threaded = FuncThread(user.decorrelator, arg = None)
            threaded.start()
        if event == 'display':
            pprint(user.group_info(user.group_list))
            
        if event == 'file':
            #sg.PopupGetFile('Выберите путь сохранения файла', save_as = True, file_types = ('All files'))
            sg.Popup(file_writer(user.group_info(user.group_list), f"{values['file_target']}\{user.user_info['id']}_{user.user_info['last_name']}"))
                     
    window.close()
        
class FuncThread(threading.Thread):
    def __init__(self, foo, arg):
        threading.Thread.__init__(self)
        self.daemon = True
        self.foo = foo
        self.arg = arg
    def run(self):
        self.foo(self.arg)

if __name__ == '__main__':
    
    gui()