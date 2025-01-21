#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import subprocess
import shutil
import argparse
from datetime import datetime


#使用方法：python wpt_restore.py /path/to/wpt_backup_20240318123456.tar.gz

# 配置
MYSQL_USER = "root"
MYSQL_PASSWORD = "password"
MYSQL_HOST = "xx.xx.xx.xx"  # 新服务器的 MySQL 主机
MYSQL_PORT = "3306"
DATABASE_NAME = "wpt"
RESTORE_DIR = "/opt/wpt"      # 解压目标目录
APP_STORAGE_DIR = "/app/storage"  # 应用存储目录

def restore_database(sql_file):
    """还原数据库"""
    print(f"正在还原数据库从 {sql_file}...")
    
    try:
        # 检查并创建数据库（如果不存在）
        create_db_command = [
            "mysql",
            "-u", MYSQL_USER,
            f"-p{MYSQL_PASSWORD}",
            "-h", MYSQL_HOST,
            "-P", MYSQL_PORT,
            "-e", f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"
        ]
        
        print("检查数据库状态...")
        subprocess.run(create_db_command, check=True)
        
        # 直接导入数据（会自动覆盖同名表）
        restore_command = [
            "mysql",
            "-u", MYSQL_USER,
            f"-p{MYSQL_PASSWORD}",
            "-h", MYSQL_HOST,
            "-P", MYSQL_PORT,
            DATABASE_NAME
        ]
        
        print("开始导入数据...")
        with open(sql_file, 'r') as f:
            subprocess.run(restore_command, stdin=f, check=True)
        print("数据库还原完成")
    except subprocess.CalledProcessError as e:
        print(f"还原数据库时出错：{e}")
        raise

def restore_storage(storage_backup_dir):
    """还原存储文件"""
    print(f"正在还原存储文件从 {storage_backup_dir} 到 {APP_STORAGE_DIR}...")
    
    try:
        # 确保目标目录存在
        os.makedirs(APP_STORAGE_DIR, exist_ok=True)
        
        # 复制所有文件和目录
        for item in os.listdir(storage_backup_dir):
            src = os.path.join(storage_backup_dir, item)
            dst = os.path.join(APP_STORAGE_DIR, item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
                
        print("存储文件还原完成")
    except Exception as e:
        print(f"还原存储文件时出错：{e}")
        raise

def extract_backup(backup_file, extract_dir):
    """解压备份文件"""
    print(f"正在解压备份文件 {backup_file} 到 {extract_dir}...")
    
    try:
        os.makedirs(extract_dir, exist_ok=True)
        subprocess.run(["tar", "-xzf", backup_file, "-C", extract_dir], check=True)
        print("备份文件解压完成")
    except subprocess.CalledProcessError as e:
        print(f"解压备份文件时出错：{e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='还原 WPT 备份')
    parser.add_argument('backup_file', help='备份文件路径 (.tar.gz)')
    args = parser.parse_args()
    
    if not os.path.exists(args.backup_file):
        print(f"错误：备份文件 {args.backup_file} 不存在")
        return
    
    # 添加提示
    print("注意：此操作将更新现有的 wpt 数据库数据（如果存在）。")
    print("建议在执行还原操作前先备份现有数据。")
    confirm = input("是否继续？(y/N): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        return
    
    try:
        # 创建临时解压目录
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        temp_dir = f"{RESTORE_DIR}/temp_restore_{timestamp}"
        
        # 解压备份文件
        extract_backup(args.backup_file, temp_dir)
        
        # 查找解压后的文件
        sql_file = None
        storage_dir = None
        
        for item in os.listdir(temp_dir):
            if item.endswith('.sql'):
                sql_file = os.path.join(temp_dir, item)
            elif 'storage_backup_' in item:
                storage_dir = os.path.join(temp_dir, item)
        
        if not sql_file or not storage_dir:
            raise ValueError("备份文件中未找到必要的数据库或存储文件")
        
        # 执行还原操作
        restore_database(sql_file)
        restore_storage(storage_dir)
        
    finally:
        # 清理临时文件
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print("已清理临时文件")

if __name__ == "__main__":
    main()
