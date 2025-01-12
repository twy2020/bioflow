import os
from logger import log
from colorama import Fore, Back, Style, init

def check_workspace_structure(workspace_path):
    print()
    print(f"{Fore.YELLOW}* Check Workspace Structure * {Style.RESET_ALL}")
    print()
    print(f"{Fore.CYAN}Workspace: {Fore.WHITE}{workspace_path}{Style.RESET_ALL}")
    print()
    """
    检查工作目录结构是否完整，并创建缺失的目录。

    Args:
        workspace_path (str): 工作目录的路径。

    Returns:
        None
    """
    # 定义需要检查的目录列表
    required_dirs = [
        "source",
        "gff_files",
        "hista2_build/src",
        "hista2_build/index",
        "results/SRA2FASTQ",
        "results/QC_result",
        "results/CleanData",
        "results/Mapping_result",
        "results/SAM2BAM",
        "results/GTF",
        "results/FPKM",
        "results/xls",
    ]

    # 跟踪缺失的目录
    missing_dirs = []

    # 检查目录是否存在
    for rel_path in required_dirs:
        dir_path = os.path.join(workspace_path, rel_path)
        if os.path.exists(dir_path):
            log.log_status('exist', rel_path)  # 打印存在的目录日志
        else:
            log.log_status('not_exist', rel_path)  # 打印缺失的目录日志
            missing_dirs.append(dir_path)

    # 如果存在缺失的目录，开始创建
    if missing_dirs:
        print()
        log.log_io('create', "Create missing directory...")
        print()
        for dir_path in missing_dirs:
            try:
                os.makedirs(dir_path, exist_ok=True)
                log.log_status('exist', os.path.relpath(dir_path, workspace_path))  # 打印创建成功的日志
            except Exception as e:
                log.level_log('ERROR', f"Directory {dir_deth} creation failed: {str(e)}")  # 打印错误日志

    # 重新检查以确保所有目录已创建
    all_present = True
    for rel_path in required_dirs:
        dir_path = os.path.join(workspace_path, rel_path)
        if not os.path.exists(dir_path):
            all_present = False
            log.log_status('not_exist', rel_path)

    # 根据最终检查结果打印日志
    if all_present:
        print()
        log.level_log('INFO', "Workspace structure check has passed.")
    else:
        print()
        log.level_log('ERROR', "Workspace structure check did not pass, please manually check.")
