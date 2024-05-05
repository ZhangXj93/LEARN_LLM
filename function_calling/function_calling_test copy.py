import os
from openai import OpenAI

# 加载 .env 到环境变量
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# 配置 OpenAI 服务

client = OpenAI()


import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.transform import Rotation as Rot

show_animation = True


# 计算角度
def mod2pi(theta):
    return theta - 2.0 * math.pi * math.floor(theta / 2.0 / math.pi)


# 转角
def pi_2_pi(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi


# 定义dubins曲线集合里的各个元素,dubins只能直行
# 1.左转-直行-左转
def left_straight_left(alpha, beta, d):
    sa = math.sin(alpha)
    sb = math.sin(beta)
    ca = math.cos(alpha)
    cb = math.cos(beta)
    c_ab = math.cos(alpha - beta)
    tmp0 = d + sa - sb
    mode = ["L", "S", "L"]
    p_squared = 2 + (d * d) - (2 * c_ab) + (2 * d * (sa - sb))
    if p_squared < 0:
        return None, None, None, mode
    tmp1 = math.atan2((cb - ca), tmp0)
    t = mod2pi(-alpha + tmp1)
    p = math.sqrt(p_squared)
    q = mod2pi(beta - tmp1)
    return t, p, q, mode


# 2.右转-直行-右转
def right_straight_right(alpha, beta, d):
    sa = math.sin(alpha)
    sb = math.sin(beta)
    ca = math.cos(alpha)
    cb = math.cos(beta)
    c_ab = math.cos(alpha - beta)
    tmp0 = d - sa + sb
    mode = ["R", "S", "R"]
    p_squared = 2 + (d * d) - (2 * c_ab) + (2 * d * (sb - sa))
    if p_squared < 0:
        return None, None, None, mode
    tmp1 = math.atan2((ca - cb), tmp0)
    t = mod2pi(alpha - tmp1)
    p = math.sqrt(p_squared)
    q = mod2pi(-beta + tmp1)

    return t, p, q, mode


# 3.左转-直行-右转
def left_straight_right(alpha, beta, d):
    sa = math.sin(alpha)
    sb = math.sin(beta)
    ca = math.cos(alpha)
    cb = math.cos(beta)
    c_ab = math.cos(alpha - beta)

    p_squared = -2 + (d * d) + (2 * c_ab) + (2 * d * (sa + sb))
    mode = ["L", "S", "R"]
    if p_squared < 0:
        return None, None, None, mode
    p = math.sqrt(p_squared)
    tmp2 = math.atan2((-ca - cb), (d + sa + sb)) - math.atan2(-2.0, p)
    t = mod2pi(-alpha + tmp2)
    q = mod2pi(-mod2pi(beta) + tmp2)

    return t, p, q, mode


# 4.右转-直行-左转
def right_straight_left(alpha, beta, d):
    sa = math.sin(alpha)
    sb = math.sin(beta)
    ca = math.cos(alpha)
    cb = math.cos(beta)
    c_ab = math.cos(alpha - beta)

    p_squared = (d * d) - 2 + (2 * c_ab) - (2 * d * (sa + sb))
    mode = ["R", "S", "L"]
    if p_squared < 0:
        return None, None, None, mode
    p = math.sqrt(p_squared)
    tmp2 = math.atan2((ca + cb), (d - sa - sb)) - math.atan2(2.0, p)
    t = mod2pi(alpha - tmp2)
    q = mod2pi(beta - tmp2)
    return t, p, q, mode


# 5.右转-左转-右转
def right_left_right(alpha, beta, d):
    sa = math.sin(alpha)
    sb = math.sin(beta)
    ca = math.cos(alpha)
    cb = math.cos(beta)
    c_ab = math.cos(alpha - beta)

    mode = ["R", "L", "R"]
    tmp_rlr = (6.0 - d * d + 2.0 * c_ab + 2.0 * d * (sa - sb)) / 8.0
    if abs(tmp_rlr) > 1.0:
        return None, None, None, mode

    p = mod2pi(2 * math.pi - math.acos(tmp_rlr))
    t = mod2pi(alpha - math.atan2(ca - cb, d - sa + sb) + mod2pi(p / 2.0))
    q = mod2pi(alpha - beta - t + mod2pi(p))
    return t, p, q, mode


# 6.左转-右转-左转
def left_right_left(alpha, beta, d):
    sa = math.sin(alpha)
    sb = math.sin(beta)
    ca = math.cos(alpha)
    cb = math.cos(beta)
    c_ab = math.cos(alpha - beta)

    mode = ["L", "R", "L"]
    tmp_lrl = (6.0 - d * d + 2.0 * c_ab + 2.0 * d * (- sa + sb)) / 8.0
    if abs(tmp_lrl) > 1:
        return None, None, None, mode
    p = mod2pi(2 * math.pi - math.acos(tmp_lrl))
    t = mod2pi(-alpha - math.atan2(ca - cb, d + sa - sb) + p / 2.0)
    q = mod2pi(mod2pi(beta) - alpha - t + mod2pi(p))

    return t, p, q, mode


def dubins_path_planning_from_origin(end_x, end_y, end_yaw, curvature,
                                     step_size):
    dx = end_x
    dy = end_y
    D = math.hypot(dx, dy)
    d = D * curvature

    theta = mod2pi(math.atan2(dy, dx))
    alpha = mod2pi(- theta)
    beta = mod2pi(end_yaw - theta)
    # 遍历，比较路径代价，得到最短路径
    planners = [left_straight_left, right_straight_right, left_straight_right,
                right_straight_left, right_left_right,
                left_right_left]
    best_cost = float("inf")
    bt, bp, bq, best_mode = None, None, None, None
    for planner in planners:
        t, p, q, mode = planner(alpha, beta, d)
        if t is None:
            continue
        cost = (abs(t) + abs(p) + abs(q))
        if best_cost > cost:
            bt, bp, bq, best_mode = t, p, q, mode
            best_cost = cost
    lengths = [bt, bp, bq]

    x_list, y_list, yaw_list, directions = generate_local_course(
        sum(lengths), lengths, best_mode, curvature, step_size)

    return x_list, y_list, yaw_list, best_mode, best_cost

    # 数据处理，得到路径


# 插入并更新数据
def interpolate(ind, length, mode, max_curvature, origin_x, origin_y,
                origin_yaw, path_x, path_y, path_yaw, directions):
    if mode == "S":
        path_x[ind] = origin_x + length / max_curvature * math.cos(origin_yaw)
        path_y[ind] = origin_y + length / max_curvature * math.sin(origin_yaw)
        path_yaw[ind] = origin_yaw
    else:  # curve
        ldx = math.sin(length) / max_curvature
        ldy = 0.0
        if mode == "L":  # 左转
            ldy = (1.0 - math.cos(length)) / max_curvature
        elif mode == "R":  # 右转
            ldy = (1.0 - math.cos(length)) / -max_curvature
        gdx = math.cos(-origin_yaw) * ldx + math.sin(-origin_yaw) * ldy
        gdy = -math.sin(-origin_yaw) * ldx + math.cos(-origin_yaw) * ldy
        path_x[ind] = origin_x + gdx
        path_y[ind] = origin_y + gdy

    if mode == "L":  # 左转
        path_yaw[ind] = origin_yaw + length
    elif mode == "R":  # 右转
        path_yaw[ind] = origin_yaw - length

    if length > 0.0:
        directions[ind] = 1
    else:
        directions[ind] = -1

    return path_x, path_y, path_yaw, directions


def dubins_path_planning(s_x, s_y, s_yaw, g_x, g_y, g_yaw, c, step_size=0.1):
    """
        s_x 起始点位置x
        s_y 起始点位置y
        s_yaw 起始点位姿角度
        g_x x 终止点位置x
        g_y y 终止点位置y
        g_yaw 终止点位姿角度
        c 曲率 [1/m]

    """
    g_x = g_x - s_x
    g_y = g_y - s_y
    l_rot = Rot.from_euler('z', s_yaw).as_matrix()[0:2, 0:2]
    le_xy = np.stack([g_x, g_y]).T @ l_rot
    le_yaw = g_yaw - s_yaw
    lp_x, lp_y, lp_yaw, mode, lengths = dubins_path_planning_from_origin(
        le_xy[0], le_xy[1], le_yaw, c, step_size)
    rot = Rot.from_euler('z', -s_yaw).as_matrix()[0:2, 0:2]
    converted_xy = np.stack([lp_x, lp_y]).T @ rot
    x_list = converted_xy[:, 0] + s_x
    y_list = converted_xy[:, 1] + s_y
    yaw_list = [pi_2_pi(i_yaw + s_yaw) for i_yaw in lp_yaw]
    return x_list, y_list, yaw_list, mode, lengths


def generate_local_course(total_length, lengths, mode, max_curvature,
                          step_size):
    n_point = math.trunc(total_length / step_size) + len(lengths) + 4

    path_x = [0.0 for _ in range(n_point)]
    path_y = [0.0 for _ in range(n_point)]
    path_yaw = [0.0 for _ in range(n_point)]
    directions = [0.0 for _ in range(n_point)]
    index = 1

    if lengths[0] > 0.0:
        directions[0] = 1
    else:
        directions[0] = -1

    ll = 0.0

    for (m, l, i) in zip(mode, lengths, range(len(mode))):
        if l > 0.0:
            d = step_size
        else:
            d = -step_size

        # 设置最初的状态
        origin_x, origin_y, origin_yaw = \
            path_x[index], path_y[index], path_yaw[index]

        index -= 1
        if i >= 1 and (lengths[i - 1] * lengths[i]) > 0:
            pd = - d - ll
        else:
            pd = d - ll

        while abs(pd) <= abs(l):
            index += 1
            path_x, path_y, path_yaw, directions = interpolate(
                index, pd, m, max_curvature, origin_x, origin_y, origin_yaw,
                path_x, path_y, path_yaw, directions)
            pd += d

        ll = l - pd - d  # calc 为长度

        index += 1
        path_x, path_y, path_yaw, directions = interpolate(
            index, l, m, max_curvature, origin_x, origin_y, origin_yaw,
            path_x, path_y, path_yaw, directions)

    if len(path_x) <= 1:
        return [], [], [], []
    while len(path_x) >= 1 and path_x[-1] == 0.0:
        path_x.pop()
        path_y.pop()
        path_yaw.pop()
        directions.pop()
    return path_x, path_y, path_yaw, directions


def plot_arrow(x, y, yaw, length=0.5, width=0.2, fc="r",
               ec="k"):
    # 绘制箭头
    if not isinstance(x, float):
        for (i_x, i_y, i_yaw) in zip(x, y, yaw):
            plot_arrow(i_x, i_y, i_yaw)
    else:
        plt.arrow(x, y, length * math.cos(yaw), length * math.sin(yaw),
                  fc=fc, ec=ec, head_width=width, head_length=width)
        plt.plot(x, y)

def start_yaw(x):
    s_yaw = np.deg2rad(x)
    return s_yaw

def end_yaw(x):
    e_yaw = np.deg2rad(x)
    return e_yaw
def plot_dubins(start_x ,start_y ,start_yaw ,end_x,end_y,end_yaw ,curvature):
    print("Dubins路径规划")
    # 输入起始终止点

    path_x, path_y, path_yaw, mode, path_length = dubins_path_planning(start_x, start_y, start_yaw,
                                                                       end_x, end_y, end_yaw, curvature)
    if show_animation:
        plt.plot(path_x, path_y, label="Dubins " + "".join(mode))
        plot_arrow(start_x, start_y, start_yaw)
        plot_arrow(end_x, end_y, end_yaw)
        plt.legend()
        plt.grid(True)
        plt.axis("equal")
        plt.show()
#函数描述对象
tools = [
    {
        "type": "function",
        "function": {
            "name": "plot_dubins",
            "description": "Perform path planning",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_x": {
                        "type": "string",
                        "description": "The abscissa of the initial position of object motion,e.g. 1.0",
                    },
                    "start_y": {
                        "type": "string",
                        "description": "The vertical coordinate of the initial position of object motion,e.g. 1.0",
                    },
                    "start_yaw":{
                        "type": "string",
                        "description":"The initial heading of object motion,e.g. 45°"
                    },
                    "end_x":{
                        "type": "string",
                        "description":"The abscissa of the final position of object motion,e.g. 50.0"
                    },
                    "end_y":{
                        "type":"string",
                        "description":"The vertical coordinate of the final position of object motion,e.g. 60.0"
                    },
                    "end_yaw":{
                        "type":"string",
                        "description":"The final heading of object motion,e.g. -45°"
                    },
                    "curvature":{
                        "type":"string",
                        "description":"The turning radius of object motion,e.g. 3.0"
                    },
                },
                "required": ["start_x", "start_y","start_yaw","end_x", "end_y", "end_yaw","curvature"],
            },
        }
    }
]

response = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "You are an excellent expert in path planning. Currently, there is an object with a starting position at (0.0,1.0), a starting direction of 45 °, an ending direction of -45 °, and an ending position of (50.0,50.0). The minimum turning radius for the object is 3.0. Please plan the path so that the object can move from the starting point to the ending point"
                       ,
        }
    ],
    model="gpt-3.5-turbo",
    tools=tools
)

print(response)

print(print(response.choices[0].message.content))  # 更具体的的打印