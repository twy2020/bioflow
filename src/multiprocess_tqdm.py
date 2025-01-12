# multiprocess_tqdm.py
import time
import multiprocessing
from tqdm import tqdm
from typing import List, Dict, Any

class MultiprocessTQDM:
    def __init__(self, num_workers: int, bar_params: List[Dict[str, Any]]):
        """
        初始化 MultiprocessTQDM 对象
        :param num_workers: 子进程数量
        :param bar_params: 每个进度条的参数，包含 desc, position, ncols, unit 等
        """
        self.num_workers = num_workers
        self.bar_params = bar_params
        self.manager = multiprocessing.Manager()
        self.shared_dict = self.manager.dict()

        # 初始化进度条的状态
        for i in range(num_workers):
            self.shared_dict[i] = 0  # 初始化每个进度条的进度

    def progress_bar(self):
        """
        创建并显示多个进度条
        """
        bars = [
            tqdm(total=param.get("total", 10), position=i, desc=param.get("desc", f"Progress {i+1}"), 
                 ncols=param.get("ncols", 100), unit=param.get("unit", "file"), leave=True)
            for i, param in enumerate(self.bar_params)
        ]

        try:
            while True:
                all_done = True  # 用于检查是否所有进度条已完成
                for i, bar in enumerate(bars):
                    bar.n = self.shared_dict[i]  # 获取当前进度
                    bar.last_print_n = bar.n  # 保证进度条显示更新
                    bar.update(0)  # 更新进度条显示

                    # 检查是否所有进度条都已完成
                    if self.shared_dict[i] < self.bar_params[i]["total"]:
                        all_done = False

                # 如果所有进度条都已完成，则跳出循环
                if all_done:
                    break

                time.sleep(0.1)  # 每隔一段时间更新一次进度条
        except KeyboardInterrupt:
            # 在用户按 Ctrl+C 时关闭进度条
            for bar in bars:
                bar.close()

    def start(self, worker_function, tasks):
        """
        启动进程并开始任务
        :param worker_function: 任务函数
        :param tasks: 每个进程处理的任务列表
        """
        processes = []
        
        # 启动每个工作进程
        for i, task_batch in enumerate(tasks):
            p = multiprocessing.Process(target=self._worker_wrapper, args=(worker_function, self.shared_dict, i, task_batch))
            processes.append(p)
            p.start()
        
        # 启动进度条显示更新
        self.progress_bar()
        
        # 等待所有进程完成
        for p in processes:
            p.join()

        print("All processes have completed.")

    def _worker_wrapper(self, worker_function, shared_dict, pbar_position, task_batch):
        """
        包装器，用于将共享字典传递给任务函数并执行
        :param worker_function: 任务函数
        :param shared_dict: 共享字典
        :param pbar_position: 当前进度条的位置
        :param task_batch: 当前进程处理的任务列表
        """
        worker_function(shared_dict, pbar_position, task_batch)
