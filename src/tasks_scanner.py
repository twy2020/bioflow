import os
import subprocess
import selectors

def tasks_scanner(root_path):
    results = []  # 存储所有检测结果
    source_path = os.path.join(root_path, "source")

    if not os.path.exists(source_path):
        print(f"Error: Path {source_path} does not exist.")
        return results

    # 遍历 source 下的所有文件夹
    for dir_name in os.listdir(source_path):
        dir_path = os.path.join(source_path, dir_name)
        if not os.path.isdir(dir_path):
            continue  # 跳过非目录项

        print(f"Scanning directory: {dir_path}")
        valid_files = []
        invalid_files = []

        # 检测目录下的文件
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            if os.path.isdir(file_path):
                continue  # 跳过子目录

            # 仅检查 .sra 或无后缀的文件
            if not (file_name.endswith(".sra") or '.' not in file_name):
                print(f"Skipping non-SRA file: {file_name}")
                continue

            print(f"Checking file: {file_name}")
            try:
                process = subprocess.Popen(
                    ["vdb-validate", file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1  # 行缓冲
                )

                # 使用 selectors 处理非阻塞输出
                sel = selectors.DefaultSelector()
                sel.register(process.stdout, selectors.EVENT_READ)
                sel.register(process.stderr, selectors.EVENT_READ)

                is_valid = False
                timeout = 30  # 超时时间（秒）
                start_time = os.times().elapsed

                while True:
                    # 检查是否超时
                    if os.times().elapsed - start_time > timeout:
                        print(f"Timeout expired for file: {file_name}")
                        process.terminate()
                        break

                    # 获取就绪的事件
                    events = sel.select(timeout=1)
                    if not events:
                        continue

                    for key, _ in events:
                        line = key.fileobj.readline()
                        if not line:  # 检查流结束
                            continue

                        print(f"Output: {line.strip()}")
                        if "metadata: md5 ok" in line:
                            valid_files.append(file_name)
                            is_valid = True
                            process.terminate()  # 终止进程
                            break

                    if is_valid or process.poll() is not None:
                        break

                if not is_valid and file_name not in valid_files:
                    invalid_files.append(file_name)

            except Exception as e:
                print(f"Error validating file {file_path}: {e}")
                invalid_files.append(file_name)

        # 将目录结果加入汇总
        results.append((dir_path, valid_files, invalid_files))

    return results

# 示例调用
if __name__ == "__main__":
    root_dir = "../test_ws"  # 替换为实际路径
    scan_results = tasks_scanner(root_dir)

    print("\nScan Results:")
    for parent_dir, valid, invalid in scan_results:
        print(f"Directory: {parent_dir}")
        print(f"  Valid SRA Files: {valid}")
        print(f"  Invalid Files: {invalid}")
