from fc3d_query import FC3DQuery
from typing import List, Dict, Any, Tuple

class FC3DSumSequence(FC3DQuery):
    def find_consecutive_sums(self, sum_sequence: List[int], context_periods: int = 3) -> List[Dict[str, Any]]:
        """
        查找连续几期和值符合指定序列的期数
        
        Args:
            sum_sequence: 和值序列，例如[5, 23, 15]表示连续三期和值分别为5,23,15
            context_periods: 显示前后各几期数据
            
        Returns:
            包含匹配期数及其前后期数据的列表
        """
        if not sum_sequence or not isinstance(sum_sequence, list):
            raise ValueError("和值序列必须是一个非空列表")
            
        with self._connect() as conn:
            cursor = conn.cursor()
            
            # 查找所有期数及其和值，按日期升序排列
            cursor.execute("""
                SELECT qihao, bai, shi, ge, date, (bai + shi + ge) as sum
                FROM fc3d
                ORDER BY date ASC
            """)
            
            all_periods = cursor.fetchall()
            
            # 查找匹配的期数
            matches = []
            sequence_length = len(sum_sequence)
            
            for i in range(len(all_periods) - sequence_length + 1):
                match = True
                for j in range(sequence_length):
                    if all_periods[i + j][5] != sum_sequence[j]:
                        match = False
                        break
                
                if match:
                    # 找到匹配的序列
                    match_periods = all_periods[i:i+sequence_length]
                    
                    # 获取前几期数据
                    start_index = max(0, i - context_periods)
                    previous_periods = all_periods[start_index:i]
                    
                    # 获取后几期数据
                    end_index = min(len(all_periods), i + sequence_length + context_periods)
                    next_periods = all_periods[i+sequence_length:end_index]
                    
                    # 整合所有期数数据
                    all_context_periods = previous_periods + match_periods + next_periods
                    
                    matches.append({
                        "match_start_qihao": match_periods[0][0],  # 第一个匹配期数
                        "match_end_qihao": match_periods[-1][0],   # 最后一个匹配期数
                        "all_periods": all_context_periods
                    })
            
            return matches

def format_period(period: Tuple, is_match: bool = False) -> str:
    """格式化期数数据为易读字符串"""
    qihao, bai, shi, ge, date, sum_value = period
    
    if is_match:
        return f"期号: {qihao}, 号码: [{bai}{shi}{ge}], 和值: [{sum_value}], 日期: {date}"
    return f"期号: {qihao}, 号码: {bai}{shi}{ge}, 和值: {sum_value}, 日期: {date}"

def main():
    query = FC3DSumSequence()
    
    # 示例：查找连续三期和值为5,23,15的期数
    sum_sequence = [5, 23, 15]
    print(f"查找连续三期和值为{sum_sequence}的期数及前后期数据:")
    print()
    
    results = query.find_consecutive_sums(sum_sequence, 3)
    
    if not results:
        print(f"历史上没有连续三期和值为{sum_sequence}的记录")
        return
        
    for i, result in enumerate(results, 1):
        print(f"=== 匹配记录 {i} ===")
        print(f"匹配期数范围: {result['match_start_qihao']} 至 {result['match_end_qihao']}")
        print()
        
        match_start_qihao = result["match_start_qihao"]
        match_end_qihao = result["match_end_qihao"]
        
        for period in result["all_periods"]:
            qihao = period[0]
            is_match = match_start_qihao <= qihao <= match_end_qihao
            print(format_period(period, is_match))
        
        print("-" * 50)
        print()

if __name__ == "__main__":
    main()