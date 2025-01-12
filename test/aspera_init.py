import os
import subprocess

# 定义Aspera Connect的下载链接和安装路径
aspera_download_url = "https://d3gcli72yxqn2z.cloudfront.net/downloads/connect/latest/bin/ibm-aspera-connect_4.2.8.540_linux_x86_64.tar.gz"
aspera_install_path = os.path.expanduser("~/Aspera")
aspera_tarball = "ibm-aspera-connect_4.2.8.540_linux_x86_64.tar.gz"

# 创建Aspera安装目录
if not os.path.exists(aspera_install_path):
    os.makedirs(aspera_install_path)

# 下载Aspera Connect
print("Downloading Aspera Connect...")
subprocess.run(["wget", "-P", aspera_install_path, aspera_download_url])

# 解压Aspera Connect
print("Extracting Aspera Connect...")
subprocess.run(["tar", "-xvf", os.path.join(aspera_install_path, aspera_tarball), "-C", aspera_install_path])

# 安装Aspera Connect
print("Installing Aspera Connect...")
subprocess.run(["bash", os.path.join(aspera_install_path, "ibm-aspera-connect_4.2.8.540_linux_x86_64.sh")])

# 添加环境变量
aspera_bin_path = os.path.join(aspera_install_path, ".aspera", "connect", "bin")
print("Adding Aspera Connect to PATH...")
with open(os.path.expanduser("~/.bashrc"), "a") as bashrc_file:
    bashrc_file.write(f"export PATH={aspera_bin_path}:$PATH\n")

# 激活环境变量更改
subprocess.run(["source", "~/.bashrc"])

# 检查Aspera Connect是否安装成功
print("Checking if Aspera Connect is installed...")
ascp_help = subprocess.run(["ascp", "-h"], capture_output=True, text=True)
if "Aspera Connect" in ascp_help.stdout:
    print("Aspera Connect is installed and configured successfully.")
else:
    print("Aspera Connect installation failed.")