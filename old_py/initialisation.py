import csv
import math
import random
import multiprocessing as mp
import os


class Problem:
    def __init__(self):
        self.name = ''
        self.KP_type = ''
        self.total_cities = 0
        self.total_items = 0
        self.W = 0
        self.min_speed = 0.00
        self.max_speed = 0.00
        self.R = 0.00
        self.city_ID = []
        self.X = []
        self.Y = []
        self.item_ID = []
        self.profit = []
        self.weight = []
        self.belongto = []
        self.dist = [[]]

    def info(self):
        print('==================================')
        print('问题的收录信息: ')
        print(f'问题名称：{self.name}')
        print(f'KP类型：{self.KP_type}')
        print(f'城市数量：{self.total_cities}')
        print(f'物品数量：{self.total_items}')
        print(f'最大重量：{self.W}')
        print(f'最小速度：{self.min_speed}')
        print(f'最大速度：{self.max_speed}')
        print(f'租金：{self.R}')
        print('==================================')
        # print('城市信息列表 (ID, X, Y)')
        # for index in range(self.total_cities):
        #     print(f'ID: {self.city_ID[index]:<5} X: {self.X[index]:<8} Y: {self.Y[index]:<8}')
        # print('==================================')
        # print('物品信息列表 (ID, profit, weight, which city?)')
        # for index in range(self.total_items):
        #     print(
        #         f'ID: {self.item_ID[index]:<5} profit: {self.profit[index]:<8} weight: {self.weight[index]:<8} city_ID:{self.belongto[index]:<5}')
        # print('==================================')
        # for row_elem in self.dist:
        #     chain = ''
        #     for col_elem in row_elem:
        #         chain += f'{str(col_elem):<35}'
        #     print(chain)
        # print(len(self.dist), len(self.dist[0]))


def read_tour(path):
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        tours = []
        for row in reader:
            tours.append([int(string_num) for string_num in row])
        return tours


def read_ttp(path):
    debug = False  # debug indicator

    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        prob = Problem()
        prob.name = next(reader)[1]
        prob.KP_type = next(reader)[0].split(': ')[1]
        prob.total_cities = int(next(reader)[1])
        prob.total_items = int(next(reader)[1])
        prob.W = int(next(reader)[1])
        prob.min_speed = float(next(reader)[1])
        prob.max_speed = float(next(reader)[1])
        prob.R = float(next(reader)[1])

        next(reader)
        next(reader)

        for _ in range(prob.total_cities):
            city = [float(number) for number in next(reader)]
            prob.city_ID.append(int(city[0]))
            prob.X.append(city[1])
            prob.Y.append(city[2])

        next(reader)

        for _ in range(prob.total_items):
            item = [int(number) for number in next(reader)]
            prob.item_ID.append(item[0])
            prob.profit.append(item[1])
            prob.weight.append(item[2])
            prob.belongto.append(item[3])

        prob.dist = [([0.00] * prob.total_cities) for _ in range(prob.total_cities)]
        if debug:
            for row in range(prob.total_cities):
                for col in range(prob.total_cities):
                    prob.dist[row][col] = ([row + 1, col + 1],
                                           math.sqrt(
                                               (prob.X[row] - prob.X[col]) ** 2 + (prob.Y[row] - prob.Y[col]) ** 2))
        else:
            for row in range(prob.total_cities):
                for col in range(prob.total_cities):
                    prob.dist[row][col] = math.sqrt(
                        (prob.X[row] - prob.X[col]) ** 2 + (prob.Y[row] - prob.Y[col]) ** 2)
            # prob.info()
        if debug:
            prob.info()

        return prob


def tour_length(tour, dist):
    length = 0
    for i in range(len(tour)):
        length += dist[tour[i - 1]][tour[i]]
    return length


def two_opt_swap(tour, i, j):
    new_tour = tour[:i] + tour[i:j + 1][::-1] + tour[j + 1:]
    return new_tour


def lk(tour, dist, tours, id):
    best_tour = tour[:]
    best_length = tour_length(best_tour, dist)
    improvement = True
    budget = 1000000
    # budget = 100
    while improvement and budget > 0:
        improvement = False
        for i in range(1, len(tour) - 1):  # 从1开始，跳过第一个城市
            for j in range(i + 1, len(tour)):
                new_tour = two_opt_swap(tour, i, j)
                new_length = tour_length(new_tour, dist)
                budget -= 1
                if new_length < best_length:
                    # print('更新')
                    print(f'{id}->{new_length}')
                    # print(new_tour)
                    best_tour = new_tour[:]
                    best_length = new_length
                    improvement = True
        tour = best_tour[:]
    print(f'处理器{id}预算用完！')
    tours.put(best_tour)


def clk(prob, pop_size):
    tours = mp.Queue()
    processes = []
    for id in range(pop_size):
        init_tour = [num - 1 for num in prob.city_ID[1:]]
        random.shuffle(init_tour)
        init_tour = [0] + init_tour
        print(f'处理器-{id}开始：')
        print(init_tour)
        p = mp.Process(target=lk, args=(init_tour, prob.dist, tours, id + 1))
        processes.append(p)
        p.start()

    exits = []
    for p in processes:
        p.join()
        exits.append(p.exitcode)

    raw_routes = []
    while not tours.empty():
        opt = tours.get()
        index_init = 0
        while opt[index_init] != 0:
            index_init += 1
        if index_init != 0:
            opt = opt[index_init:] + opt[:index_init]
        raw_routes.append(opt)
        formal_tour = [num + 1 for num in opt]
        length = tour_length(opt, prob.dist)
        print("Optimized tour:", formal_tour)
        print("Tour length:", length)
    return raw_routes


if __name__ == '__main__':
    ttp_path = 'data/dataset/a280-ttp/a280_n279_bounded-strongly-corr_01.ttp'
    problem = read_ttp(ttp_path)
    problem.info()
    inds = 40
    sub = 8
    rs = clk(problem, inds)
    processed = 0
    runtime = 0
    # while processed < inds:
    #     seg = rs[processed:processed + sub]
    #     draw(problem, seg, runtime + 1)
    #     runtime += 1
    #     processed += sub

    file = os.path.join('result', 'clk_tours', 'tsp-?.csv')
    with open(file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=' ')
        for row_main in rs:
            writer.writerow(row_main)
