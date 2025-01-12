# file_processing.py
import time
import random
from multiprocess_tqdm import MultiprocessTQDM

def file_processing(shared_dict, pbar_position, file_batch):
    """
    文件处理函数，模拟处理文件的进度更新
    :param shared_dict: 共享字典，存储进度
    :param pbar_position: 当前进度条的位置
    :param file_batch: 当前进程处理的文件列表
    """
    total_files = len(file_batch)
    
    for i, file in enumerate(file_batch):
        time.sleep(random.uniform(0.5, 2))  # 模拟文件处理的不同速度
        shared_dict[pbar_position] += 1  # 每处理一个文件，更新进度
    
        # 确保进度不会超过总量
        if shared_dict[pbar_position] >= total_files:
            shared_dict[pbar_position] = total_files
            break

if __name__ == "__main__":
    # 设置进度条的参数
    bar_params = [
        {"desc": "Batch 1", "position": 0, "ncols": 100, "unit": "file", "total": 5},
        {"desc": "Batch 2", "position": 1, "ncols": 100, "unit": "file", "total": 5}
    ]

    # 假设有10个文件
    files = [f"file_{i}.txt" for i in range(1, 11)]
    
    # 将文件划分为两批
    batch_size = len(files) // 2
    file_batches = [files[:batch_size], files[batch_size:]]  # 划分成两批
    
    # 创建 MultiprocessTQDM 实例，并启动
    mp_tqdm = MultiprocessTQDM(num_workers=2, bar_params=bar_params)
    
    # 启动文件处理任务，并显示进度条
    mp_tqdm.start(file_processing, file_batches)
