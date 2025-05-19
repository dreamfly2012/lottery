#!/usr/bin/env python3
import schedule
import time
from dlt_scrapy import main as scrape_dlt
from datetime import datetime

def job():
    """定时任务"""
    print(f"\n开始执行更新任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        scrape_dlt()
    except Exception as e:
        print(f"更新任务执行失败: {e}")
    print(f"更新任务完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主函数"""
    # 设置每天凌晨2点运行
    schedule.every().day.at("02:00").do(job)
    
    print("定时任务已启动，将在每天凌晨2点更新数据...")
    print("按 Ctrl+C 停止运行")
    
    # 立即运行一次
    job()
    
    # 保持程序运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n程序已停止")

if __name__ == "__main__":
    main()