import time
from info import  banner
from check_system import print_system_info
from colorama import Fore, Style, init
from logger import log
import os
import param_manager
from check_ws import check_workspace_structure
from check_files import scan_and_select

# 初始化colorama
init(autoreset=True)

def main():
    # Parse command-line arguments
    args = param_manager.parse_args()

    # Print Starter Banner
    banner()
    symbols = ['-', '|', '/', '\\']
    start_time = time.time()

    while time.time() - start_time < 3:
        for symbol in symbols:
            print(f'\r{Fore.YELLOW}Loading... ' + symbol, end='')
            time.sleep(0.1)

    # Print parsed arguments
    param_manager.display_args(args)
    time.sleep(1)

    print("\r")
    print(Fore.GREEN + 'Automatic SRA to FPKM program running...')

    # Check system info
    print_system_info()
    time.sleep(1)

    # Check workspace
    check_workspace_structure(args.workspace_path)

    # Check and select files
    selected_files = scan_and_select(args.workspace_path)

    


if __name__ == "__main__":
    main()