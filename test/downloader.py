# src/downloader.py
import os
import requests
from tqdm import tqdm
from logger import Logger
from concurrent.futures import ThreadPoolExecutor

class Downloader:
    def __init__(self, download_dir):
        self.download_dir = download_dir
        self.logger = Logger()

    def download_srr(self, srr_id, ftp_url):
        try:
            # 设置保存路径
            file_path = os.path.join(self.download_dir, f"{srr_id}.sra")
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)

            # 进行文件下载
            response = requests.get(ftp_url, stream=True)
            response.raise_for_status()

            with open(file_path, 'wb') as f, tqdm(
                desc=f"Downloading {srr_id}",
                total=int(response.headers.get('Content-Length', 0)),
                unit='B', unit_scale=True) as bar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bar.update(len(chunk))
            self.logger.info(f"Download completed for {srr_id}")
        except Exception as e:
            self.logger.error(f"Failed to download {srr_id}: {str(e)}")

    def download_srrs(self, srr_ids, ftp_base_url):
        # 并行下载文件
        with ThreadPoolExecutor() as executor:
            futures = []
            for srr_id in srr_ids:
                ftp_url = f"{ftp_base_url}{srr_id}/{srr_id}.sra"
                futures.append(executor.submit(self.download_srr, srr_id, ftp_url))

            # 等待所有下载完成
            for future in futures:
                future.result()
