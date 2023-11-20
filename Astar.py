import tkinter
import math
import numpy as np
import heapq


class Node():
    colors = {None: 'white', 'active': 'lightgreen', 'passed': 'pink', 'path': 'purple', 'start': 'green', 'end': 'red'}
    
    def __init__(self, blocked, left=None, right=None, up=None, down=None):
        self.left = left
        self.right = right
        self.up = up
        self.down = down
        self.blocked = bool(blocked)
        self.state = None
        self.obj = None


class Field():
    def __init__(self, lst, canvas, width):
        self.field = []
        self.c = canvas
        self.width = width
        self.stopped = False
        self.active = False
        for i in range(len(lst)):
            self.field.append([])
            for j in range(len(lst[0])):
                self.field[i].append(Node(lst[i][j]))
                if j > 0:
                    self.field[i][j].left = self.field[i][j - 1]
                    self.field[i][j - 1].right = self.field[i][j]
                if i > 0:
                    self.field[i][j].up = self.field[i - 1][j]
                    self.field[i - 1][j].down = self.field[i][j]
                    
    @classmethod
    def gen(cls, N=50, p=0.8, start=(0, 0), stop=(49, 49)):
        lst = np.random.choice((0, 1), p=(p, 1 - p), size=N ** 2).reshape(N, N)
        lst[start] = 0
        lst[stop] = 0
        return lst
                    
    def draw_all(self):
        if self.stopped:
            return
        field.apply_state(*START, 'start')
        field.apply_state(*END, 'end')
        self.c.delete('all')
        for i in range(len(self.field)):
            for j in range(len(self.field)):
                if self.field[i][j].blocked:
                    self.field[i][j].obj = self.c.create_oval(self.width * i, self.width * j, self.width * (i + 1) + 1, self.width * (j + 1) + 1, fill='black')
                else:
                    self.field[i][j].obj = self.c.create_oval(self.width * i, self.width * j, self.width * (i + 1) + 1, self.width * (j + 1) + 1, fill=Node.colors[self.field[i][j].state])
            
    def draw(self, i, j):
        self.c.delete(self.field[i][j].obj)
        self.field[i][j].obj = self.c.create_oval(self.width * i, self.width * j, self.width * (i + 1) + 1, self.width * (j + 1) + 1, fill=Node.colors[self.field[i][j].state])
    
    def apply_state(self, i, j, state):
        self.field[i][j].state = state
        self.draw(i, j)
    
    def find_way(self, start, end):
        graph = {}

        for i in range(len(self.field)):
            for j in range(len(self.field[0])):
                neigb = []
                if self.field[i][j].left and not self.field[i][j - 1].blocked:
                    neigb.append((i, j - 1))
                if self.field[i][j].right and not self.field[i][j + 1].blocked:
                    neigb.append((i, j + 1))
                if self.field[i][j].up and not self.field[i - 1][j].blocked:
                    neigb.append((i - 1, j))
                if self.field[i][j].down and not self.field[i + 1][j].blocked:
                    neigb.append((i + 1, j))
                graph[(i, j)] = dict.fromkeys(neigb, 1)

        def astar(graph, start, end):
            open_set = []
            closed_set = set()
            came_from = {}
            g_score = {node: float('inf') for node in graph}
            g_score[start] = 0
            f_score = {node: float('inf') for node in graph}
            f_score[start] = heuristic(start, end)
            heapq.heappush(open_set, (f_score[start], start))

            while open_set:
                if self.stopped:
                    return
                current_f, current_node = heapq.heappop(open_set)
                if current_node == end:
                    return reconstruct_path(came_from, end)

                closed_set.add(current_node)
                self.apply_state(*current_node, 'passed')
                window.update()

                for neighbor in graph[current_node]:
                    if self.stopped:
                        return
                    if neighbor in closed_set:
                        continue
                    self.apply_state(*neighbor, 'active')
                    window.update()
                    tentative_g_score = g_score[current_node] + graph[current_node][neighbor]
                    if tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current_node
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, end)
                        if neighbor not in open_set:
                            heapq.heappush(open_set, (f_score[neighbor], neighbor))
            return None

        def heuristic(node, end):
            return abs(node[0] - end[0]) + abs(node[1] - end[1])

        def reconstruct_path(came_from, current_node):
            path = [current_node]
            while current_node in came_from:
                current_node = came_from[current_node]
                path.append(current_node)
            path.reverse()
            for i in path:
                self.field[i[0]][i[1]].state = 'path'
                self.draw(*i)
                window.update()
            return path
        
        path = astar(graph, start, end)


window = tkinter.Tk()
window.title('Tkinter')
window.geometry('1000x700')

c = tkinter.Canvas(width=700, height=700)
c.pack(side='left')

N = 50
P = 0.8
WIDTH = 700 / N
START = (0, 0)
END = (N - 1, N - 1)
startend_state = True

field = Field(Field.gen(N, P, START, END), c, WIDTH)

def click(event):
    global START, END, startend_state
    coords = int(event.x // WIDTH), int(event.y // WIDTH)
    if field.field[coords[0]][coords[1]].blocked:
        return
    if field.active:
        return
    if startend_state:
        field.apply_state(*START, None)
        START = coords
        field.apply_state(*START, 'start')
    else:
        field.apply_state(*END, None)
        END = coords
        field.apply_state(*END, 'end')
    startend_state = not(startend_state)

c.bind("<Button-1>", click)


def start():
    global field
    if not field.active:
        bstart.config(bg='lightgreen')
        field.draw_all()
        field.active = True
        field.find_way(START, END)
    
bstart = tkinter.Button(text='Start ▶', command=start, width=40, height=4, bg='lightgrey')
bstart.place(x=705, y=5)

def restart():
    global field, startend_state
    startend_state = True
    field.stopped = True
    field = Field(Field.gen(N, P, START, END), c, WIDTH)
    field.draw_all()
    bstart.config(bg='lightgrey')
    
brestart = tkinter.Button(text='Rebuild ↻', command=restart, width=40, height=4, bg='lightgrey')
brestart.place(x=705, y=85)


def number(event):
    global N, WIDTH, END, START
    if N != scN.get():
        N = scN.get()
        WIDTH = 700 / N
        START = (0, 0)
        END = (N - 1, N - 1)
        restart()
    
scN = tkinter.Scale(window, from_=5, to=100, length=100, label='NxN', command=number)
scN.set(N)
scN.place(x=705, y=200)


def prob(event):
    global P
    if P != scP.get() / 100:
        P = scP.get() / 100
        restart()
    
scP = tkinter.Scale(window, from_=0, to=100, length=100, label='Probability', command=prob)
scP.set(P * 100)
scP.place(x=855, y=200)


def main():
    field.draw_all()

main()
    
window.mainloop()
