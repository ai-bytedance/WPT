import os
import subprocess
import shutil
from datetime import datetime

# 配置
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"
MYSQL_HOST = "xx.xx.xx.xx"
MYSQL_PORT = "3306"
DATABASE_NAME = "wpt"
BACKUP_DIR = "/opt/wpt"
STORAGE_DIR = "/opt/wpt/storage"
DATE_FORMAT = "%Y%m%d%H%M%S"  # 定义时间格式

# 生成备份文件名
def generate_backup_filename(prefix, extension="sql"):
    timestamp = datetime.now().strftime(DATE_FORMAT)
    return f"{BACKUP_DIR}/{prefix}_{timestamp}.{extension}"

# 备份数据库
def backup_database():
    backup_file = generate_backup_filename("wpt_database", "sql")
    dump_command = [
        "mysqldump", 
        "-u", MYSQL_USER, 
        f"-p{MYSQL_PASSWORD}", 
        "-h", MYSQL_HOST, 
        "-P", MYSQL_PORT, 
        "--databases", DATABASE_NAME, 
        "--replace", 
        "--single-transaction", 
        "--skip-lock-tables", 
        "--routines", 
        "--triggers"
    ]
    
    print(f"正在备份数据库到 {backup_file}...")
    with open(backup_file, "w") as f:
        subprocess.run(dump_command, stdout=f)
    print(f"数据库备份完成：{backup_file}")

# 手动备份文件夹，排除 .sock 文件
def backup_directory():
    timestamp = datetime.now().strftime(DATE_FORMAT)
    backup_folder = f"{BACKUP_DIR}/storage_backup_{timestamp}"

    print(f"正在备份文件夹 {STORAGE_DIR} 到 {backup_folder}...")

    # 创建目标文件夹
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    for root, dirs, files in os.walk(STORAGE_DIR):
        # 过滤掉 .sock 文件
        files = [f for f in files if not f.endswith('.sock')]

        # 创建子目录
        for file in files:
            src_file = os.path.join(root, file)
            relative_path = os.path.relpath(src_file, STORAGE_DIR)
            dst_file = os.path.join(backup_folder, relative_path)

            # 确保目标目录存在
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)

            # 复制文件
            shutil.copy2(src_file, dst_file)

    print(f"文件夹备份完成：{backup_folder}")

# 将备份文件打包成压缩包
def create_backup_archive():
    timestamp = datetime.now().strftime(DATE_FORMAT)
    archive_name = f"{BACKUP_DIR}/wpt_backup_{timestamp}.tar.gz"
    
    print(f"正在创建备份压缩包 {archive_name}...")
    
    # 获取最新的备份文件和文件夹
    backup_files = []
    for item in os.listdir(BACKUP_DIR):
        item_path = os.path.join(BACKUP_DIR, item)
        if os.path.isfile(item_path) and item.endswith('.sql'):
            backup_files.append(item)
        elif os.path.isdir(item_path) and 'storage_backup_' in item:
            backup_files.append(item)
    
    # 创建压缩包
    current_dir = os.getcwd()
    os.chdir(BACKUP_DIR)
    try:
        subprocess.run(["tar", "-czf", archive_name] + backup_files, check=True)
        print(f"备份压缩包创建完成：{archive_name}")
        
        # 删除已压缩的文件和文件夹
        for item in backup_files:
            item_path = os.path.join(BACKUP_DIR, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print("已清理临时备份文件")
    except subprocess.CalledProcessError as e:
        print(f"创建压缩包时出错：{e}")
    finally:
        os.chdir(current_dir)

# 执行备份操作
def main():
    backup_database()         # 备份数据库
    backup_directory()        # 备份文件夹
    create_backup_archive()   # 创建备份压缩包

if __name__ == "__main__":
    main()
