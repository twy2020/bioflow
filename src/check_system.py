from colorama import Fore, Style
import psutil
import platform
import cpuinfo
from logger import log 
import sys

def convert_bytes(bytes):
    """
    将字节数转换为易于阅读的格式（例如 GB, MB, KB）。
    :param bytes: 字节数
    :return: 格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"  # 如果大于TB，返回TB

def colorize_value(value, levels):
    """
    根据值设置颜色
    :param value: 要处理的值（数值，不带单位）
    :param levels: 定义不同值范围的颜色级别，如[(上限, 颜色)]
    :return: 使用颜色格式化后的字符串
    """
    for level in levels:
        if value <= level[0]:
            return f"{level[1]}{value}{Style.RESET_ALL}"
    return f"{Fore.GREEN}{value}{Style.RESET_ALL}"  # 如果都不符合，返回绿色

def get_system_info():
    """
    获取并返回操作系统和硬件的基本信息。
    """
    total_memory = psutil.virtual_memory().total
    available_memory = psutil.virtual_memory().available
    disk_usage = psutil.disk_usage('/')
    disk_free = disk_usage.free
    
    # 转换为 GB，并四舍五入保留两位小数
    total_memory_gb = round(total_memory / (1024 ** 3), 2)
    available_memory_gb = round(available_memory / (1024 ** 3), 2)
    disk_free_gb = round(disk_free / (1024 ** 3), 2)

    # 标签列表
    labels = [
        "System", "Node Name", "Release", "Version", "Machine", 
        "Processor", "CPU Count", "Total Memory", "Available Memory", "CPU Model", 
        "CPU Frequency", "Disk Usage", "Disk Free", "Uptime"
    ]
    
    # 对应的值列表
    values = [
        platform.system(), platform.node(), platform.release(), platform.version(), platform.machine(),
        platform.processor(), psutil.cpu_count(logical=True), f"{total_memory_gb} GB", 
        f"{available_memory_gb} GB", cpuinfo.get_cpu_info().get('model', 'N/A'),
    ]

    # 捕获psutil.cpu_freq()调用中的错误
    try:
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            values.append(f"{cpu_freq.current} MHz")
        else:
            values.append('N/A')
    except Exception:
        values.append('N/A')

    values.append(convert_bytes(disk_usage.total))
    # 这里将 Disk Free 作为数值传递，稍后再加上单位并颜色化
    values.append(disk_free_gb)  # 只传递数值，稍后再加单位并颜色化
    values.append(get_uptime())
    
    return labels, values

def get_uptime():
    """
    获取系统启动的时间（uptime）
    """
    uptime_seconds = psutil.boot_time()
    return format_uptime(uptime_seconds)

def format_uptime(seconds):
    """
    将秒数转换为友好的格式（天, 小时, 分钟）
    """
    days = seconds // (24 * 3600)
    hours = (seconds % (24 * 3600)) // 3600
    minutes = (seconds % 3600) // 60
    return f"{int(days)} days, {int(hours)} hours, {int(minutes)} minutes"

def print_system_info():
    print()
    print(f"{Fore.YELLOW}* Check System State *{Style.RESET_ALL}")
    print()
    labels, values = get_system_info()

    # 获取系统资源数据
    cpu_count = psutil.cpu_count(logical=True)
    available_memory = psutil.virtual_memory().available / (1024 ** 3)  # GB
    disk_free = psutil.disk_usage('/').free / (1024 ** 3)  # GB

    for label, value in zip(labels, values):
        # 先输出标签
        print(f"{Fore.BLUE}{label}{Style.RESET_ALL}:", end=" ")

        # 根据值设置颜色
        if label == "CPU Count":
            # CPU Count 根据核心数来设置颜色
            value_numeric = value  # 直接使用数值
            print(f"{colorize_value(value_numeric, [(8, Fore.RED), (20, Fore.YELLOW)])}")
        
        elif label == "Available Memory":
            # Available Memory 根据 GB 数量来设置颜色
            value_numeric = float(value.split()[0])  # 提取数值部分，转换为浮动数
            print(f"{colorize_value(value_numeric, [(8, Fore.RED), (32, Fore.YELLOW)])} GB")
        
        elif label == "Disk Free":
            # 这里传递纯数值，然后再附加单位并颜色化
            value_numeric = value  # 使用值而非字符串
            print(f"{colorize_value(value_numeric, [(500, Fore.RED), (1000, Fore.YELLOW)])} GB")
        
        else:
            # 对于没有单位的值，如 Disk Usage，直接打印
            print(value)

    print("\r")
    # 设置阈值
    cpu_warning_level = 8  # 小于 8 核心时警告
    memory_warning_level = 32  # 小于 8 GB 时警告
    disk_warning_level = 1000  # 小于 50 GB 时警告

    # 记录警告信息
    warnings = []

    # 检查 CPU 核心数
    if cpu_count <= cpu_warning_level:
        warnings.append(f"Low CPU performance: CPU core count ({cpu_count} cores) is below the recommended threshold of {cpu_warning_level} cores! Processing progress may be slow.")

    # 检查可用内存
    if available_memory <= memory_warning_level:
        warnings.append(f"Low memory: Available memory ({available_memory:.2f} GB) is below the recommended threshold {memory_warning_level} GB! May lead to collapse.")

    # 检查磁盘剩余空间
    if disk_free <= disk_warning_level:
        warnings.append(f"Low disk space: Disk free space ({disk_free:.2f} GB) is below the recommended threshold {disk_warning_level} GB! Subsequent operations may be affected.")

    # 如果有任何警告，输出警告并询问是否继续
    if warnings:
        for warning in warnings:
            log.level_log('WARNING', warning)
        
        # 询问是否强制继续
        while True:
            continue_check = input(f"Do you want to continue? (yes/no): ").strip().lower()
            if continue_check in ["yes", "no"]:
                break
            else:
                print(f"{Fore.RED}Invalid input. Please enter 'yes' or 'no'.{Style.RESET_ALL}")
        
        if continue_check != "yes":
            log.level_log('ERROR', 'Operation aborted!')
            sys.exit(0)  # 终止程序执行
    else:
        log.level_log('INFO', 'System check passed. Continue with the operation.')

    return True  # 所有检查通过，继续执行后续操作


# 调用打印系统信息函数
# print_system_info()