import os
import shutil
from datetime import datetime
import subprocess   
import time
import sys



# 替换为你的 Android 应用的包名
ANDROID_PACKAGE_NAME = "com.baidu.paddle.lite.demo.ppocr_demo"
# 手机上存储照片的根目录
ANDROID_APP_DIR = f"/storage/emulated/0/android/data/{ANDROID_PACKAGE_NAME}/files/results"

def run_adb_command(command):
    """
    运行 adb 命令并捕获其输出。
    """
    try:
        result = subprocess.run(['./tools/adb/adb.exe'] + command, encoding="utf-8",capture_output=True, text=True, check=True)
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        print(f"执行 adb 命令失败: {e.stderr}")
        return None, e.returncode

def get_remote_file_list():
    """
    通过 adb 获取手机目录下的所有文件列表及修改时间。
    """
    print("正在获取手机端文件列表...")
    
    # 递归列出目录中的文件及其详细信息
    ls_result, return_code = run_adb_command(['shell', f'ls -lR {ANDROID_APP_DIR}'])
    
    if return_code != 0:
        return None
    
    # 解析 ls -lR 的输出
    # 格式可能因设备和安卓版本而异，这里处理我测试的样机的一种形式
    remote_files = {}
    current_dir = ""
    for line in ls_result.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # 识别目录行
        if line.endswith(':'):
            current_dir = line[:-1]
            continue
        
        parts = line.split()
        if len(parts) < 8:
            continue
            
        # 文件的详细信息
        permission, _, user, group, size, month_or_day, time_or_year, filename = parts
        
        # 忽略目录本身
        if permission.startswith('d'):
            continue
        
        # 构造完整路径
        full_path = os.path.join(current_dir, filename)
        # 获取修改时间戳，这里简化处理，只比较文件名
        # 实际项目中，最好使用更精确的时间戳比较
        
        remote_files[full_path] = {
            'size': size,
            'timestamp': f"{month_or_day} {time_or_year}"
        }
    return remote_files

def get_local_file_list(pc_local_dir):
    """
    获取 PC 本地目录下的文件列表。
    """
    local_files = {}
    for root, _, files in os.walk(pc_local_dir):
        for filename in files:
            full_path = os.path.join(root, filename)
            local_files[full_path] = os.path.getmtime(full_path)
    return local_files

def sync_files_with_adb(pc_local_dir):
    """
    通过 adb 同步手机上的文件到 PC。
    """
    print("正在检查设备连接...")
    devices, return_code = run_adb_command(['devices'])
    if return_code != 0 or 'device' not in devices:
        print("未找到已连接的设备。请确保设备已连接并启用了USB调试。")
        return False
    
    print(f"设备已连接。正在同步目录: {ANDROID_APP_DIR}")
    remote_files = get_remote_file_list()
    if not remote_files:
        print("无法获取远程文件列表，同步失败。")
        return False
    
    local_files = get_local_file_list(pc_local_dir)
    
    files_to_pull = []

    # 比较文件
    for remote_path in remote_files:
        # 将远程路径转换为本地路径
        relative_path = os.path.relpath(remote_path, ANDROID_APP_DIR)
        local_path = os.path.join(pc_local_dir, relative_path)
        
        # 修正：远程路径必须用正斜杠
        remote_path_fixed = remote_path.replace("\\", "/")
        
        # 检查本地文件是否存在或是否需要更新
        # 这里为了简化，仅判断文件是否存在，如果不存在则拉取
        # 实际项目中，你可以比较文件大小和修改时间
        if not os.path.exists(local_path):
            files_to_pull.append(remote_path_fixed)
            
    if not files_to_pull:
        print("本地文件已是最新，无需同步。")
        return True
    
    print(f"检测到 {len(files_to_pull)} 个新文件，开始同步...")
    
    for remote_file in files_to_pull:
        # 构造 adb pull 命令
        relative_path = os.path.relpath(remote_file, ANDROID_APP_DIR)
        local_dir = os.path.join(pc_local_dir, os.path.dirname(relative_path))
        
        os.makedirs(local_dir, exist_ok=True)
        
        pull_command = [
            'pull',
            remote_file,
            local_dir
        ]
        
        print(f"正在拉取: {remote_file}")
        pull_result, _ = run_adb_command(pull_command)
        if pull_result:
            print(f"成功拉取: {os.path.basename(remote_file)}")
        else:
            print(f"拉取失败: {remote_file}")
            
    print("增量同步完成。")
    return True


# 示例：在你的主应用中调用
if __name__ == "__main__":
    
    # 设置你的 PC 本地存储路径，设置为当前路径
    PC_BASE_DIR = os.path.join(os.path.dirname(__file__), 'SyncedPhotos')
    # 确保本地目录存在
    os.makedirs(PC_BASE_DIR, exist_ok=True)

    sync_files_with_adb(PC_BASE_DIR)