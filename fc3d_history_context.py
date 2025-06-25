from fc3d_query import FC3DQuery
from typing import List, Dict, Any, Tuple, Optional
import sqlite3

class FC3DHistoryContext(FC3DQuery):
    def find_number_with_context(self, number: Tuple[int, int, int], context_periods: int = 3) -> List[Dict[str, Any]]:
        """
        查找特定号码的历史记录及其前后期数据，并将它们整合在一起显示
        
        Args:
            number: 三位数号码，格式为(百位,十位,个位)，例如(6,4,5)
            context_periods: 显示前后各几期数据
            
        Returns:
            包含匹配期数及其前后期数据的列表
        """
        if not isinstance(number, tuple) or len(number) != 3:
            raise ValueError("号码必须是一个三元组，例如(6,4,5)")
            
        bai, shi, ge = number
        
        with self._connect() as conn:
            cursor = conn.cursor()
            
            # 查找匹配的期数
            cursor.execute("""
                SELECT qihao, bai, shi, ge, date
                FROM fc3d
                WHERE bai = ? AND shi = ? AND ge = ?
                ORDER BY date DESC
            """, (bai, shi, ge))
            
            matches = cursor.fetchall()
            if not matches:
                return []
                
            results = []
            
            for match in matches:
                match_qihao = match[0]
                match_date = match[4]
                
                # 查找前几期数据
                cursor.execute("""
                    SELECT qihao, bai, shi, ge, date
                    FROM fc3d
                    WHERE date < ?
                    ORDER BY date DESC
                    LIMIT ?
                """, (match_date, context_periods))
                previous_periods = list(reversed(cursor.fetchall()))  # 反转顺序，使其按日期升序
                
                # 查找后几期数据
                cursor.execute("""
                    SELECT qihao, bai, shi, ge, date
                    FROM fc3d
                    WHERE date > ?
                    ORDER BY date ASC
                    LIMIT ?
                """, (match_date, context_periods))
                next_periods = cursor.fetchall()
                
                # 整合所有期数数据
                all_periods = previous_periods + [match] + next_periods
                
                results.append({
                    "match_qihao": match_qihao,
                    "all_periods": all_periods
                })
                
            return results

def format_period(period: Tuple, target_number: Tuple[int, int, int] = None) -> str:
    """格式化期数数据为易读字符串，如果是匹配号码则加上标记"""
    qihao, bai, shi, ge, date = period
    
    if target_number and (bai, shi, ge) == target_number:
        return f"期号: {qihao}, 号码: [{bai}{shi}{ge}], 日期: {date}"
    return f"期号: {qihao}, 号码: {bai}{shi}{ge}, 日期: {date}"

def main():
    query = FC3DHistoryContext()
    
    # 示例：查找号码645的历史记录及前后3期数据
    target_number = (6, 4, 5)
    print(f"查找号码 {target_number[0]}{target_number[1]}{target_number[2]} 的历史记录及前后期数据:")
    print()
    
    results = query.find_number_with_context(target_number, 3)
    
    if not results:
        print(f"历史上没有出现过号码 {target_number[0]}{target_number[1]}{target_number[2]}")
        return
        
    for i, result in enumerate(results, 1):
        print(f"=== 记录组 {i} ===")
        for period in result["all_periods"]:
            print(format_period(period, target_number))
        print("-" * 50)
        print()

if __name__ == "__main__":
    main()