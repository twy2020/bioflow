import logging
from colorama import Fore, Style, init

# 初始化colorama
init(autoreset=True)

class CustomLogger:
    def __init__(self, log_file=None, log_level=logging.DEBUG, show_prefix=True):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.show_prefix = show_prefix  # 控制是否显示前缀

        # 控制台日志输出
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # 文件日志输出
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            self.logger.addHandler(file_handler)

        # 设置格式
        if show_prefix:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        else:
            formatter = logging.Formatter('%(message)s')

        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def color_log(self, message, color=Fore.WHITE):
        """快速格式化指定文本"""
        print(f"{color}{message}{Style.RESET_ALL}")

    def log(self, level, message):
        """通用日志方法"""
        if level == 'INFO':
            self.logger.info(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        elif level == 'DEBUG':
            self.logger.debug(message)

    def level_log(self, level, message):
        """带颜色的日志级别输出"""
        color_map = {
            'INFO': Fore.GREEN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'DEBUG': Fore.CYAN
        }
        color = color_map.get(level, Fore.WHITE)
        self.color_log(f"{level}: {message}", color)

    def log_error_to_file(self, error_message, log_file):
        """记录错误信息到文件"""
        try:
            with open(log_file, 'a') as file:
                file.write(f"{error_message}\n")
        except Exception as e:
            self.color_log(f"[ERROR] Failed to write error to file: {e}", Fore.RED)

    def log_io(self, action, path):
        """日志 IO 操作"""
        color_map = {
            'create': Fore.BLUE,
            'delete': Fore.YELLOW
        }
        symbol = '+' if action == 'create' else '-'
        self.color_log(f"[{symbol}] {action}: {path}", color_map.get(action, Fore.WHITE))

    def log_status(self, status, item):
        """日志状态输出"""
        color_map = {
            'exist': Fore.GREEN,
            'not_exist': Fore.RED
        }
        symbol = '√' if status == 'exist' else 'x'
        self.color_log(f"[{symbol}] {item} {'exists' if status == 'exist' else 'does not exist'}", color_map.get(status, Fore.WHITE))

log = CustomLogger(log_file='app.log', log_level=logging.DEBUG, show_prefix=False)

# 示例使用
if __name__ == "__main__":
    
    # 记录彩色日志
    log.level_log('INFO', '这是一个信息日志')
    log.level_log('ERROR', '这是一个错误日志')
    
    # 输出IO操作日志
    log.log_io('create', 'file.txt')
    log.log_io('delete', 'file.txt')
    
    # 输出状态日志
    log.log_status('exist', 'folder_name')
    log.log_status('not_exist', 'nonexistent_folder')
    
    # 记录错误信息到文件
    try:
        1 / 0  # 故意抛出错误
    except ZeroDivisionError as e:
        log.log_error_to_file(str(e), 'error.log')
