import requests
import sys

# Данные авторизации в API Trello
auth_params = {
    'key': input('Введите свой ключ TrelloAPI '),
    'token': input('Введите свой токен TrelloAPI '), }

# Адрес, на котором расположен API Trello, # Именно туда мы будем отправлять
# HTTP запросы.
base_url = "https://api.trello.com/1/{}"
board_id = "ZkgSIVPr"


class Task:
    def __init__(self, name_of_task, name_of_column, number_task_in_column,
                 id_of_task):
        self.name_of_task = name_of_task
        self.name_of_column = name_of_column
        self.number_task_in_column = number_task_in_column
        self.id_of_task = id_of_task

    def __repr__(self):
        return 'Имя: {}, Название колонки: {}, Номер в колонке: {}'.format(self.name_of_task, self.name_of_column, self.number_task_in_column)


def read():
    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards') + '/' + board_id +
                               '/lists', params=auth_params).json()
    # Теперь выведем название каждой колонки и всех заданий, которые к ней
    # относятся:
    for column in column_data:
        column_name = column['name']
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' +
                                 column['id'] + '/cards',
                                 params=auth_params).json()
        print(str(column_name) + ' В колонке {} задач'.format(len(task_data)))
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'])


def create_column(name):
    current_board = requests.get(base_url.format('boards') + '/' + board_id,
                                 params=auth_params).json()
    requests.post(base_url.format('lists'),
                  data={'name': name, 'idBoard': current_board['id'],
                        'pos': "bottom", **auth_params})


def create(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id +
                               '/lists', params=auth_params).json()

    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая
    # нам нужна
    for column in column_data:
        if column['name'] == column_name:
            # Создадим задачу с именем _name_ в найденной колонке
            requests.post(base_url.format('cards'), data={'name': name,
                                                          'idList': column[
                                                              'id'],
                                                          **auth_params})
            break


def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(
        base_url.format('boards') + '/' + board_id + '/lists',
        params=auth_params).json()

    # Среди всех колонок нужно найти задачу по имени и получить её id
    task_id = None
    i = 1
    list_items = []
    for column in column_data:
        column_tasks = requests.get(
            base_url.format('lists') + '/' + column['id'] + '/cards',
            params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                list_items.append(Task(task['name'], column["name"], i, task["id"]))
                i += 1
        i = 1
    if len(list_items) > 1:
        for item in list_items:
            print(item)
        a = input("Из какой колонки вы хотите переместить задачу? ")
        b = int(input("Какой номер имеет задача в этой колонке? "))
        for item in list_items:
            if (item.number_task_in_column == b) and (item.name_of_column == a):
                task_id = item.id_of_task
    elif len(list_items) == 1:
        task_id = list_items[0].id_of_task

    # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы
    # будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + task_id + '/idList',
                         data={'value': column['id'], **auth_params})
            break


if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_column':
        create_column(sys.argv[2])
