from tkinter import *
import tkinter as tk
from tkinter import ttk
import pydot
from PIL import ImageTk, Image
from os import listdir
from os.path import isfile, join
from collections import defaultdict
import imageio
import glob
from tkinter.messagebox import showinfo
from PIL import Image
import time


def dijkstra(graph: dict, W: str, nodes: list):
    unseen = {node: float('inf') for node in nodes}
    seen = {}
    path = 0
    unseen[W] = path
    init_W = W
    pictures = []
    while unseen:
        for vert, dist in graph[W].items():
            if vert in seen:
                continue
            if unseen[vert] > (path + dist) or unseen[vert] is float('inf'):
                unseen[vert] = (path + dist)
        seen[W] = path
        del unseen[W]
        if not unseen:
            break
        W = min(unseen, key=unseen.get)
        path = unseen[W]
        other = {**seen, **unseen}
        pictures.append(other)
    return pictures


class MyGraph:
    """ Undirected graph data structure """

    def __init__(self, connections):
        self.graph = defaultdict(set)
        self.add_connections(connections)

    def add_connections(self, connections):
        """ Add connections (list of tuple pairs) to graph """

        for node1, node2, w in connections:
            self.add(node1, node2, w)

    def add(self, node1, node2, w):
        """ Add connection between node1 and node2 """

        self.graph[node1].add(node2 + ',' + str(w))
        self.graph[node2].add(node1 + ',' + str(w))

    def is_connected(self, node1, node2):
        """ Is node1 directly connected to node2 """

        return node1 in self.graph and node2 in self.graph[node1]

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, dict(self.graph))


def show_graph(path):
    btn.pack_forget()
    show.pack_forget()
    (graph,) = pydot.graph_from_dot_file('./dot/' + path + '.dot')
    graph.write_png('./pictures/' + path + '.png')
    img = ImageTk.PhotoImage(Image.open('./pictures/'+path+'.png'))
    panel.configure(image=img)
    panel.pack(side=TOP)
    back_to_menu_btn.pack()


def run_algo(path):
    if start_vert.get() != '':
        btn.pack_forget()
        show.pack_forget()
        with open('./mygraphs/'+path+'.txt', 'r', encoding='utf-8') as f:
            data = f.readlines()
            nodes = [tuple(x.replace('\n', '').split()) for x in data]
        g = dict(MyGraph(nodes).graph)
        for k, v in g.items():
            g[k] = {x.split(',')[0]: int(x.split(',')[1]) for x in v}
        verts = list(g.keys())
        W = start_vert.get()
        pictures = dijkstra(g, W, verts)
        filenames = []
        form_str = '<{0} dist={3}> -- <{1} dist={4}> [label="{2}"];\n'
        for n, pic in enumerate(pictures):
            with open(
                    './gif_files/' + path + str(n) + '.dot',
                    'w', encoding='utf-8') as f:
                f.write('graph G{\n')
                f.write('graph [size = "7.75,10.25"]\n')
                for node in nodes:
                    f.write(
                        form_str.format(
                            *node, pic[node[0]], pic[node[1]]))
                f.write('\n}')
            (graph,) = pydot.graph_from_dot_file(
                './gif_files/' + path + str(n) + '.dot')
            graph.write_png('./gif_pics/' + path + str(n) + '.png')
            filenames.append('./gif_pics/' + path + str(n) + '.png')
        with imageio.get_writer('./gifs/{}.gif'.format(path),
                                mode='I',
                                duration=1) as writer:
            for filename in filenames:
                image = imageio.imread(filename)
                writer.append_data(image)
        back_to_menu_btn.pack()
        C = n
        frames = [PhotoImage(file='./gifs/{}.gif'.format(path),
                             format='gif -index %i' % (i)) for i in range(C)]

        def update(ind):
            time.sleep(1)
            frame = frames[ind]
            ind += 1
            if ind == C:
                ind = 0
            gif.configure(image=frame)
            window.after(n, update, ind)

        gif.pack()
        window.after(0, update, 0)
    else:
        print(start_vert.get(), 'update')
        showinfo("Message", f"Есть незаполненные поля!")
        start_vert.pack_forget()
        algos_choice()


def algos_choice():
    btn.pack_forget()
    show.pack_forget()
    algos_button.pack_forget()
    title.configure(text='Алгоритмы')
    w3.pack()
    start_vert.configure(text='Начальная вершина')
    start_vert_lbl.pack()
    start_vert.pack()
    onlyfiles = [f for f in listdir('./dot') if isfile(join('./dot', f))]
    button_dict = {}
    for f in onlyfiles:
        def make_path(x=f.split('.')[0]):
            for b in button_dict.values():
                b.pack_forget()
            return run_algo(x)

        button_dict[f] = Button(
            window, text=f.split('.')[0], command=make_path)
        button_dict[f].pack(pady=5)


def graph_choice():
    btn.pack_forget()
    show.pack_forget()
    algos_button.pack_forget()
    title.configure(text='Сохраненные графы')
    onlyfiles = [f for f in listdir('./dot') if isfile(join('./dot', f))]
    button_dict = {}
    for f in onlyfiles:
        def make_path(x=f.split('.')[0]):
            for b in button_dict.values():
                b.pack_forget()
            return show_graph(x)
        button_dict[f] = Button(
            window, text=f.split('.')[0], command=make_path)
        button_dict[f].pack(pady=5)


def end_building():
    with open('./mygraphs/'+graph_name.get()+'.txt',
              'w', encoding='utf-8') as f:
        for t in vertices:
            line = ' '.join(str(x) for x in t)
            f.write(line + '\n')
    with open('./mygraphs/'+graph_name.get()+'.txt',
              'r', encoding='utf-8') as f:
        data = f.readlines()
        nodes = [x.replace('\n', '').split() for x in data]
    if mode.get() == 'Ориентированный':
        if weight.get() == 'С весами':
            with open('./dot/'+graph_name.get()+'.dot',
                      'w', encoding='utf-8') as f:
                f.write('digraph G{\n')
                for node in nodes:
                    f.write('{} -> {} [label="{}"];\n'.format(*node))
                f.write('\n}')
        elif weight.get() == 'Без весов':
            with open('./dot/'+graph_name.get()+'.dot', 'w',
                      encoding='utf-8') as f:
                f.write('digraph G{\n')
                for node in nodes:
                    f.write('{} -> {};\n'.format(*node))
                f.write('\n}')
    elif mode.get() == 'Неориентированный':
        if weight.get() == 'С весами':
            with open('./dot/'+graph_name.get()+'.dot', 'w',
                      encoding='utf-8') as f:
                f.write('graph G{\n')
                for node in nodes:
                    f.write('{} -- {} [label="{}"];\n'.format(*node))
                f.write('\n}')
        elif weight.get() == 'Без весов':
            with open('./dot/'+graph_name.get()+'.dot', 'w',
                      encoding='utf-8') as f:
                f.write('graph G{\n')
                for node in nodes:
                    f.write('{} -- {};\n'.format(*node))
                f.write('\n}')

    btn.configure(text="Создать граф", command=name_graph)
    title.configure(text="ZGraph")
    title.pack()
    btn.pack(side=TOP)
    show.pack()
    algos_button.pack()

    vertn_name_lbl.pack_forget()
    graph_name_lbl.pack_forget()
    edges_lbl.pack_forget()
    graph_name.pack_forget()
    vert_name.pack_forget()
    edges.pack_forget()
    back_to_menu_btn.pack_forget()
    panel.pack_forget()
    start_vert.pack_forget()
    start_vert_lbl.pack_forget()
    gif.pack_forget()
    end_building_btn.pack_forget()

    w.pack_forget()
    w2.pack_forget()
    w3.pack_forget()


def back_to_menu():
    time.sleep(0)
    window.update()
    gif.destroy()
    btn.pack_forget()
    btn.pack()
    btn.configure(text="Создать граф", command=name_graph)
    title.configure(text="ZGraph")
    title.pack()
    btn.pack()
    show.pack()
    algos_button.pack()
    algos_button.pack()

    vertn_name_lbl.pack_forget()
    graph_name_lbl.pack_forget()
    edges_lbl.pack_forget()
    graph_name.pack_forget()
    vert_name.pack_forget()
    edges.pack_forget()
    back_to_menu_btn.pack_forget()
    panel.pack_forget()
    start_vert.pack_forget()
    start_vert_lbl.pack_forget()
    gif.pack_forget()
    dir_man.pack_forget()

    w.pack_forget()
    w2.pack_forget()
    w3.pack_forget()


def save_graph():
    if vert_name_box.get() != '' and edges != '':
        edges_box.get()
        graph[vert_name_box.get()] = edges_box.get().split(' ')

        if weight.get() == 'С весами':
            for edge in edges_box.get().split(' '):
                vertices.append((vert_name_box.get(),
                                 edge.split('-')[0], edge.split('-')[1]))
        elif weight.get() == 'Без весов':
            for edge in edges_box.get().split(' '):
                vertices.append((vert_name_box.get(), edge))
        btn.configure(text="Добавить вершину", command=add_node)
        vertn_name_lbl.pack_forget()
        edges_lbl.pack_forget()
        vert_name.pack_forget()
        edges.pack_forget()
        end_building_btn.pack(side=RIGHT)
    else:
        print(vert_name_box.get(), 'edges?')
        showinfo("Message", f"Есть незаполненные поля!")


def add_node():
    dir_man.pack()
    btn.configure(text="Сохранить", command=save_graph)
    vertn_name_lbl.configure(text='Вершина')
    edges_lbl.configure(text='Грани')
    vertn_name_lbl.pack()
    vert_name.pack()
    edges_lbl.pack()
    edges.pack()
    btn.pack()
    end_building_btn.pack_forget()


def name_graph():
    show.pack_forget()
    graph_name_lbl.configure(text='Навзвание графа')
    graph_name_lbl.pack()
    graph_name.pack()
    w.pack()
    w2.pack()

    btn.configure(text="Сохранить", command=build_graph)
    btn.pack(side=BOTTOM)
    back_to_menu_btn.pack(side=LEFT)

    vertn_name_lbl.pack_forget()
    edges_lbl.pack_forget()
    vert_name.pack_forget()
    edges.pack_forget()
    panel.pack_forget()
    end_building_btn.pack_forget()
    algos_button.pack_forget()
    start_vert.pack_forget()
    start_vert_lbl.pack_forget()


def build_graph():
    if graph_name.get() != '':
        graph_name.configure(state='disabled')
        w.configure(state='disabled')
        w2.configure(state='disabled')
        btn.configure(text="Добавить вершину", command=add_node)
        title.configure(text="Создание графа")
    else:
        print(graph_name.get(), 'build')
        showinfo("Message", f"Есть незаполненные поля!")


graph = {}
vertices = []
path = ''


window = Tk()
window.geometry('1000x700')
window.title("ZGraph alpha v0.2")
style = ttk.Style(window)
style.theme_use('winnative')
window.configure()

img = ''
panel = tk.Label(window)


title = Label(window, text="ZGraph", font=("Arial Bold", 30))
title.pack()

btn = Button(window, text="Создать граф", command=name_graph)
show = Button(window, text="Показать граф", command=graph_choice)
back_to_menu_btn = Button(window,
                          text="Вернуться в меню", command=back_to_menu)
end_building_btn = Button(window,
                          text="Закончить создание", command=end_building)
algos_button = Button(window,
                      text="Запустить алгоритм", command=algos_choice)


btn.pack()
show.pack()
algos_button.pack()

modes = ['Ориентированный', 'Неориентированный']
mode = StringVar(window)
mode.set('Ориентированный')
w = OptionMenu(window, mode, *modes)

weights = ['С весами', 'Без весов']
weight = StringVar(window)
weight.set('С весами')
w2 = OptionMenu(window, weight, *weights)

algos = ['Дийкстра']
algo = StringVar(window)
algo.set('Дийкстра')
w3 = OptionMenu(window, algo, *algos)

gif = Label(window)

start_vert = StringVar()
vert_name_box = StringVar()
edges_box = StringVar()
graph_name_box = StringVar()

start_vert_lbl = Label(window, text='Начальная вершина')
vertn_name_lbl = Label(window)
edges_lbl = Label(window)
graph_name_lbl = Label(window)
info = '''Введите вершину и грани.
Вершины перечисляются через пробел.
При взвешенном графе также через "-" указывается вес ребра.
Пример ввода граней для взвешенного графа: A-13 B-4 C-6 D-15.
Пример ввода граней без весов: A B C D'''
dir_man = Label(window, text=info)

start_vert = Entry(window, width=5, textvariable=start_vert)
vert_name = Entry(window, width=5, textvariable=vert_name_box)
edges = Entry(window, width=20, textvariable=edges_box)
graph_name = Entry(window, width=10, textvariable=graph_name_box)
window.mainloop()
