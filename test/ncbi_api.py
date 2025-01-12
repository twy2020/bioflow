import os
import requests
from Bio import Entrez

# 设置 Entrez email
Entrez.email = "tenwonyun@gmail.com"

# NCBI FTP 根目录（用来下载 SRR 文件）
NCBI_FTP_BASE_URL = "ftp://ftp.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByRun/sra/"

# 查询 SRP 项目，根据关键字筛选描述
def search_srp_by_keyword(keyword):
    handle = Entrez.esearch(db="sra", term=keyword, retmax=1000)
    record = Entrez.read(handle)
    handle.close()
    return record["IdList"]

# 获取 SRP 项目下的所有 SRR 记录
def fetch_srr_from_srp(srp_id):
    handle = Entrez.esummary(db="sra", id=srp_id, retmode="xml")
    record = Entrez.read(handle)
    handle.close()

    # 打印记录，查看返回的数据结构
    print(record)

    srr_list = []
    # 安全地检查 'DocumentSummary' 是否存在
    if "DocumentSummary" in record[0]:
        for docsum in record[0]["DocumentSummary"]:
            srr_list.extend(docsum["Run"].split(","))
    else:
        print(f"No DocumentSummary found for SRP: {srp_id}")
    return srr_list

# 过滤 SRR 列表（根据数据类型、实验类型等条件）
def filter_srr_by_criteria(srr_list, criteria):
    filtered_srr = []
    for srr in srr_list:
        if criteria.lower() in srr.lower():  # 这里可以添加更多复杂的过滤条件
            filtered_srr.append(srr)
    return filtered_srr

# 下载指定的 SRR 文件
def download_srr_file(srr, download_dir):
    # 构建 FTP 下载路径
    ftp_url = f"{NCBI_FTP_BASE_URL}{srr[:3]}/{srr[:6]}/{srr}/{srr}.sra"
    print(f"Downloading {srr} from {ftp_url}")
    
    # 下载文件
    response = requests.get(ftp_url, stream=True)
    if response.status_code == 200:
        # 创建目录
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        # 保存文件
        with open(f"{download_dir}/{srr}.sra", 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"{srr} downloaded successfully.")
    else:
        print(f"Failed to download {srr}, status code: {response.status_code}")

# 主程序
def main():
    # 输入关键字和过滤条件
    keyword = input("Enter a keyword to search SRP (e.g. 'cancer'): ")
    criteria = input("Enter filter criteria for SRR (e.g. 'RNA'): ")

    # 查询 SRP 项目
    print(f"Searching for SRP projects related to '{keyword}'...")
    srp_ids = search_srp_by_keyword(keyword)
    print(f"Found {len(srp_ids)} SRP projects.")
    
    # 遍历每个 SRP，获取其 SRR 记录
    all_srr = []
    for srp_id in srp_ids:
        print(f"Fetching SRR records for SRP: {srp_id}")
        srr_list = fetch_srr_from_srp(srp_id)
        all_srr.extend(srr_list)

    # 过滤 SRR 记录
    print(f"Filtering SRR records with criteria: '{criteria}'")
    filtered_srr = filter_srr_by_criteria(all_srr, criteria)
    print(f"Found {len(filtered_srr)} SRR records after filtering.")

    # 下载过滤后的 SRR 文件
    download_dir = f"SRP_{keyword}"
    for srr in filtered_srr:
        download_srr_file(srr, download_dir)

# 执行主程序
if __name__ == "__main__":
    main()
