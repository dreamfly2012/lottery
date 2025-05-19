#!/usr/bin/env python3
import schedule
import time
from datetime import datetime
from dlt_scrapy import main as scrape_dlt
from ssq_scrapy import main as scrape_ssq
from fc3d_scrapy import main as scrape_fc3d

def update_job():
    """更新任务"""
    print(f"\n开始执行更新任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        print("\n=== 更新大乐透数据 ===")
        scrape_dlt()
    except Exception as e:
        print(f"大乐透更新失败: {e}")
    
    try:
        print("\n=== 更新双色球数据 ===")
        scrape_ssq()
    except Exception as e:
        print(f"双色球更新失败: {e}")
        
    try:
        print("\n=== 更新福彩3D数据 ===")
        scrape_fc3d()
    except Exception as e:
        print(f"福彩3D更新失败: {e}")
    
    print(f"\n更新任务完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """主函数"""
    # 设置每天凌晨2点运行
    schedule.every().day.at("02:00").do(update_job)
    
    print("定时任务已启动...")
    print("将在每天凌晨2点更新大乐透、双色球和福彩3D数据")
    print("按 Ctrl+C 停止运行")
    
    # 立即运行一次
    update_job()
    
    # 保持程序运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n程序已停止")

if __name__ == "__main__":
    main()