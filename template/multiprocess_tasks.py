def task_function(shared_dict, pbar_position, task_batch):
    """
    任务处理函数模板：用于处理任务并更新进度条
    :param shared_dict: 共享字典，存储进度信息
    :param pbar_position: 当前进度条的位置（每个进程有一个唯一的位置）
    :param task_batch: 当前进程处理的任务列表（可以是文件、数据等）
    """
    total_tasks = len(task_batch)  # 获取当前任务批次的任务总数
    
    # 遍历每个任务，处理并更新进度条
    for i, task in enumerate(task_batch):
        # 这里是任务的具体处理逻辑，例如处理文件、计算任务等
        process_task(task)  # 你可以在这里处理每个任务
        
        # 更新共享字典中的进度
        shared_dict[pbar_position] += 1  # 更新当前进度条的进度
        
        # 确保进度不会超过总量
        if shared_dict[pbar_position] >= total_tasks:
            shared_dict[pbar_position] = total_tasks  # 确保进度条不超过总数
            break  # 一旦进度条满了，就可以提前结束该进程

def process_task(task):
    """
    处理单个任务的具体逻辑（例如文件处理、数据计算等）
    :param task: 当前任务（例如文件名、数据项等）
    """
    # 这里可以放置每个任务的处理逻辑
    # 例如，读取文件、计算结果、进行数据处理等
    print(f"Processing {task}...")  # 这里是一个简单的模拟，可以替换为你的处理逻辑
    time.sleep(random.uniform(0.5, 2))  # 模拟任务处理的时间


# 示例用法
from multiprocess_tqdm import MultiprocessTQDM

# 假设有一组文件
files = [f"file_{i}.txt" for i in range(1, 11)]

# 将文件划分为两批
batch_size = len(files) // 2
file_batches = [files[:batch_size], files[batch_size:]]  # 划分成两批

# 进度条参数
bar_params = [
    {"desc": "Batch 1", "position": 0, "ncols": 100, "unit": "file", "total": batch_size},
    {"desc": "Batch 2", "position": 1, "ncols": 100, "unit": "file", "total": batch_size}
]

# 创建 MultiprocessTQDM 实例，并启动任务
mp_tqdm = MultiprocessTQDM(num_workers=2, bar_params=bar_params)
mp_tqdm.start(task_function, file_batches)
