#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
main.py: RNA-seq 数据分析流水线入口，管理任务调度、动态进度显示和最终结果汇总
"""

import os
import sys
import time
import yaml
import json
import threading
import multiprocessing
from glob import glob
import subprocess
import psutil
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.live import Live
import signal

from pipeline import task_manager, process_sra, utils

def reset_tasks_timer(progress_file):
    try:
        with open(progress_file, 'r') as pf:
            data = json.load(pf)
        if "tasks" in data:
            for task_id in data["tasks"]:
                data["tasks"][task_id]["start_time"] = time.time()
        with open(progress_file, 'w') as pf:
            json.dump(data, pf, indent=4)
    except Exception as e:
        print("重置计时器失败:", e)

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def dynamic_progress_display(progress_file, stop_event, refresh_interval=2):
    console = Console()
    # 设置 transient=True，Live 退出时会清除显示区域
    with Live(refresh_per_second=4, console=console, transient=True) as live:
        while not stop_event.is_set():
            new_table = Table(title="RNA-seq 任务进度")
            new_table.add_column("任务ID", style="cyan")
            new_table.add_column("当前步骤", style="magenta")
            new_table.add_column("剩余步骤", style="green")
            new_table.add_column("状态", style="red")
            new_table.add_column("已耗时", style="yellow")
            
            try:
                with open(progress_file, 'r') as pf:
                    data = json.load(pf)
                    tasks = data.get("tasks", {})
            except Exception:
                tasks = {}
            
            if not tasks:
                new_table.add_row("N/A", "等待任务启动", "N/A", "N/A", "N/A")
            else:
                for task_id, info in tasks.items():
                    current = info.get("current_step", 0)
                    total = info.get("total_steps", 6)
                    step_name = info.get("step_name", "N/A")
                    status = info.get("status", "pending")
                    remain = total - current
                    start_time = info.get("start_time")
                    if start_time:
                        elapsed = time.time() - float(start_time)
                        hrs, rem = divmod(int(elapsed), 3600)
                        mins, secs = divmod(rem, 60)
                        elapsed_str = f"{hrs:02}:{mins:02}:{secs:02}"
                    else:
                        elapsed_str = "N/A"
                    new_table.add_row(task_id, step_name, str(remain), status, elapsed_str)
            live.update(new_table)
            time.sleep(refresh_interval)

def parse_gtf_files(output_dir):
    """
    自动解析 output_dir 下所有子目录中的 .gtf 文件，生成对应的 .FPKM 文件。
    使用 bash 解释器执行命令。
    """
    cmd = rf'''for file in $(find {output_dir} -name "*.gtf"); do 
    perl -lane 'next unless $F[2] eq "transcript"; /gene_id "([^"]+)".*FPKM "([\d.]+)"/; $count{{$1}}+=$2; END{{ for(sort keys %count){{ print join "\t", $_, $count{{$_}} }} }}' "$file" > "$file.FPKM"; 
done'''
    try:
        utils.log_message("开始解析 .gtf 文件生成 .FPKM 文件……")
        subprocess.run(cmd, shell=True, check=True, executable="/bin/bash")
        utils.log_message("所有 .gtf 文件解析完成。")
    except subprocess.CalledProcessError as e:
        utils.log_message(f".gtf 文件解析失败：{e}", level="ERROR")

def generate_fpkm_summary(output_dir):
    fpkm_files = []
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith(".FPKM"):
                fpkm_files.append(os.path.join(root, file))
    summary_list = []
    for f in fpkm_files:
        df = pd.read_csv(f, sep="\t", header=None, names=["GeneID", os.path.basename(os.path.dirname(f))])
        summary_list.append(df)
    if summary_list:
        summary_df = summary_list[0]
        for df in summary_list[1:]:
            summary_df = pd.merge(summary_df, df, on="GeneID", how="outer")
        summary_df = summary_df.fillna(0)
        output_path = os.path.join(output_dir, "FPKM_summary.xlsx")
        summary_df.to_excel(output_path, index=False)
        utils.log_message(f"最终 FPKM 汇总文件生成：{output_path}")
    else:
        utils.log_message("未找到任何 FPKM 文件，无法生成汇总文件。", level="ERROR")

def system_status_check(output_dir):
    """
    检查系统状态：CPU 核心数、空闲内存、输出路径所在磁盘的剩余空间，
    并输出日志提示。如果系统状态较差，则用警告信息提示。
    """
    cpu_count = psutil.cpu_count(logical=True)
    mem = psutil.virtual_memory()
    free_mem = mem.available
    disk = psutil.disk_usage(output_dir)
    free_disk = disk.free

    free_mem_gb = free_mem / (1024**3)
    free_disk_gb = free_disk / (1024**3)

    # 输出系统状态信息
    status_msg = (
        f"系统状态检查：CPU 核心数: {cpu_count}, "
        f"空闲内存: {free_mem_gb:.2f}GB, "
        f"输出路径磁盘剩余空间: {free_disk_gb:.2f}GB"
    )
    # 用 INFO 级别输出整体状态信息
    utils.log_message(status_msg, level="INFO")

    # 定义阈值（你可以根据实际需求调整）
    mem_threshold = 4.0      # GB
    disk_threshold = 100.0     # GB
    cpu_threshold = 4        # 核心数

    if free_mem_gb < mem_threshold:
        utils.log_message(
            f"警告：空闲内存不足，仅有 {free_mem_gb:.2f}GB！", level="WARNING"
        )
    if free_disk_gb < disk_threshold:
        utils.log_message(
            f"警告：输出路径所在磁盘剩余空间不足，仅有 {free_disk_gb:.2f}GB！", level="WARNING"
        )
    if cpu_count < cpu_threshold:
        utils.log_message(
            f"警告：CPU 核心数较少，仅有 {cpu_count} 个核心！", level="WARNING"
        )

def main():
    if len(sys.argv) < 3 or sys.argv[1] != "--config":
        print("Usage: python main.py --config config.yaml")
        sys.exit(1)
    config_path = sys.argv[2]
    config = load_config(config_path)

    os.makedirs(config.get("log_dir", "./logs"), exist_ok=True)
    os.makedirs(config.get("output_dir"), exist_ok=True)

    # 进度记录文件放在项目输出目录下
    progress_file = os.path.join(config["output_dir"], "progress.json")
    if not os.path.exists(progress_file):
        project_info = {
            "project_name": config.get("project_name", "RNA-seq Project"),
            "project_creation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_creator": config.get("project_creator", "unknown")
        }
        init_dict = {
            "project_info": project_info,
            "tasks": {}
        }
        with open(progress_file, "w") as pf:
            json.dump(init_dict, pf, indent=4)
    utils.set_progress_file(progress_file)

    # 在任务启动前检查系统状态
    system_status_check(config["output_dir"])

    # 重置所有任务的计时器，每次运行程序时都从0开始计时
    reset_tasks_timer(progress_file)

    log_file = os.path.join(config.get("log_dir", "./logs"), f"run_{time.strftime('%Y-%m-%d_%H-%M')}.log")
    utils.init_log(log_file)
    utils.log_message("任务开始", extra={"user": os.getenv("USER", "unknown")})

    tasks_dict = task_manager.get_sra_files(config["input_dir"])
    if not tasks_dict:
        utils.log_message("没有找到任何 SRA 文件。", level="ERROR")
        sys.exit(1)
    utils.log_message(f"发现 {len(tasks_dict)} 个 SRA 文件。")

    # 创建 stop_event 用于控制动态显示线程退出
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=dynamic_progress_display, args=(progress_file, stop_event), daemon=True)
    progress_thread.start()

    # 创建 Manager 锁、进程池等
    manager = multiprocessing.Manager()
    hisat2_lock = manager.Lock()

    def worker_init():
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count(), initializer=worker_init)
    results = []
    for task_id, sra_path in tasks_dict.items():
        results.append(pool.apply_async(process_sra.process_sra, args=(task_id, sra_path, config, hisat2_lock)))
    pool.close()
    try:
        pool.join()
    except KeyboardInterrupt:
        stop_event.set()
        progress_thread.join()
        # Console().clear()  # 清除 Live 显示区域
        sys.stdout.write("\n")
        sys.stdout.flush()
        utils.log_message("用户终止进程", level="ERROR")
        pool.terminate()
        pool.join()
        sys.exit(1)

    # 任务全部完成后，也结束动态显示线程
    stop_event.set()
    progress_thread.join()

    utils.log_message("所有任务处理完成！")
    
    parse_gtf_files(config["output_dir"])
    generate_fpkm_summary(config["output_dir"])
    utils.log_message("任务结束", extra={"user": os.getenv("USER", "unknown")})
    print("")  # 输出空行

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("用户终止进程")
        sys.exit(1)
