import time
from colorama import Fore, init
init()
numbers = [
    "|||||||| |||||||| |||||||| |||||||| |||||||| ||||||||",
    "||       ||    ||       || ||    || ||    || ||    ||",
    "|||||||| |||||||| |||||||| |||||||| ||    || ||||||||",
    "      ||       || ||             || ||    ||       ||",
    "|||||||| |||||||| |||||||| |||||||| |||||||| ||||||||"
]

def print_colored_matrix(matrix):
    for row in matrix:
        for idx, char in enumerate(row):
            if 0 <= idx <= 7 or 18 <= idx <= 25 or 36 <= idx <= 43:  # 设置绿色区域
                print(Fore.GREEN + char, end='', flush=True)
            elif 9 <= idx <= 16 or 27 <= idx <= 34 or 45 <= idx <= 52:  # 设置红色区域
                print(Fore.RED + char, end='', flush=True)
            else:
                print(char, end='', flush=True)
            time.sleep(0.1)  # 控制字符打印速度
        print(Fore.RESET)  # 恢复默认颜色
        time.sleep(0.1)

print_colored_matrix(numbers)

