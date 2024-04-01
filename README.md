# 999py
import time
from colorama import Fore, init
init()
numbers = [
    "------------|||||||| |||||||| |||||||| |||||||| |||||||| ||||||||------------",
    "------------||       ||    ||       || ||    || ||    || ||    ||------------",
    "------------|||||||| |||||||| |||||||| |||||||| ||    || ||||||||------------",
    "------------      ||       || ||             || ||    ||       ||------------",
    "------------|||||||| |||||||| |||||||| |||||||| |||||||| ||||||||------------"
]

def print_colored_matrix(matrix):
    for row in matrix:
        for idx, char in enumerate(row):
            if 12 <= idx <= 19 or 30 <= idx <= 37 or 48 <= idx <= 55:  # 设置绿色区域
                print(Fore.GREEN + char, end='', flush=True)
            elif 21 <= idx <= 28 or 39 <= idx <= 46 or 57 <= idx <= 64:  # 设置红色区域
                print(Fore.RED + char, end='', flush=True)
            else:
                print(Fore.RESET + char, end='', flush=True)
            time.sleep(0.1)  # 控制字符打印速度
        print(Fore.RESET)  # 恢复默认颜色
        time.sleep(0.1)

print_colored_matrix(numbers)
