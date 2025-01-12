# src/srp_fetcher.py
from Bio import Entrez
from logger import Logger

class SRPFetcher:
    def __init__(self, email):
        Entrez.email = email
        self.logger = Logger()

    def fetch_srp_info(self, srp_id):
        try:
            # 使用 esearch 来查找 SRP 项目
            search_handle = Entrez.esearch(db="sra", term=srp_id, retmode="xml")
            search_record = Entrez.read(search_handle)
            search_handle.close()

            # 获取 SRP ID 是否存在
            if search_record["Count"] == "0":
                self.logger.error(f"SRP {srp_id} not found.")
                return None

            # 如果存在，继续使用 esummary 查询详细信息
            handle = Entrez.esummary(db="sra", id=srp_id, retmode="xml")
            record = Entrez.read(handle)
            handle.close()

            # 输出调试信息，查看返回的结果
            self.logger.debug(f"Fetched SRP data: {record}")

            # 解析 SRP 信息
            if "Item" in record[0] and record[0]["Item"]:
                summary = record[0]["Item"]
                return summary
            else:
                self.logger.error(f"SRP {srp_id} not found or has no items.")
                return None

        except Exception as e:
            self.logger.error(f"Error fetching {srp_id}: {str(e)}")
            return None
