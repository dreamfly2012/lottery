from fc3d_query import FC3DQuery
from typing import Dict, Tuple, List, Optional
from collections import defaultdict

class FC3DConditionalProbability(FC3DQuery):
    def calculate_next_digit_probability(self, position: str, digit: int) -> Dict[int, float]:
        """
        计算指定位置上某个数字后面出现各个数字的概率
        
        Args:
            position: 位置，'bai'/'shi'/'ge' 分别表示百位、十位、个位
            digit: 指定的数字(0-9)
            
        Returns:
            包含各个数字出现概率的字典
        """
        if position not in ['bai', 'shi', 'ge']:
            raise ValueError("位置必须是 'bai'、'shi' 或 'ge'")
        if not 0 <= digit <= 9:
            raise ValueError("数字必须在0-9之间")
            
        with self._connect() as conn:
            cursor = conn.cursor()
            
            # 获取所有期数，按日期升序排列
            cursor.execute(f"""
                WITH current_next AS (
                    SELECT 
                        t1.{position} as current_digit,
                        t2.{position} as next_digit
                    FROM fc3d t1
                    LEFT JOIN fc3d t2 ON t2.date = (
                        SELECT MIN(date)
                        FROM fc3d
                        WHERE date > t1.date
                    )
                    WHERE t1.{position} = ?
                    ORDER BY t1.date ASC
                )
                SELECT current_digit, next_digit
                FROM current_next
                WHERE next_digit IS NOT NULL
            """, (digit,))
            
            rows = cursor.fetchall()
            
            # 统计后续数字出现次数
            next_digit_counts = defaultdict(int)
            total_count = 0
            
            for row in rows:
                if row[1] is not None:  # 排除最后一期
                    next_digit_counts[row[1]] += 1
                    total_count += 1
            
            # 计算概率
            probabilities = {}
            if total_count > 0:
                for d in range(10):
                    probabilities[d] = next_digit_counts[d] / total_count
                    
            return probabilities
            
    def calculate_next_digits_probability(self, conditions: Dict[str, int]) -> Dict[str, Dict[int, float]]:
        """
        计算指定多个位置的数字组合后面出现各个数字的概率
        
        Args:
            conditions: 条件字典，键为位置('bai'/'shi'/'ge')，值为数字
            
        Returns:
            包含各个位置上各个数字出现概率的字典
        """
        if not conditions:
            raise ValueError("必须指定至少一个位置的数字")
            
        with self._connect() as conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            where_conditions = []
            params = []
            for pos, digit in conditions.items():
                if pos not in ['bai', 'shi', 'ge']:
                    raise ValueError(f"无效的位置: {pos}")
                if not 0 <= digit <= 9:
                    raise ValueError(f"无效的数字: {digit}")
                where_conditions.append(f"t1.{pos} = ?")
                params.append(digit)
                
            where_clause = " AND ".join(where_conditions)
            
            # 获取符合条件的期数及其后一期
            query = f"""
                WITH matched AS (
                    SELECT 
                        t1.date as current_date,
                        t2.date as next_date,
                        t1.bai as current_bai,
                        t1.shi as current_shi,
                        t1.ge as current_ge,
                        t2.bai as next_bai,
                        t2.shi as next_shi,
                        t2.ge as next_ge
                    FROM fc3d t1
                    LEFT JOIN fc3d t2 ON t2.date = (
                        SELECT MIN(date)
                        FROM fc3d
                        WHERE date > t1.date
                    )
                    WHERE {where_clause}
                    ORDER BY t1.date ASC
                )
                SELECT * FROM matched
                WHERE next_date IS NOT NULL
            """
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # 统计各个位置上后续数字出现次数
            next_counts = {
                'bai': defaultdict(int),
                'shi': defaultdict(int),
                'ge': defaultdict(int)
            }
            total_count = len(rows)
            
            for row in rows:
                next_counts['bai'][row[5]] += 1  # next_bai
                next_counts['shi'][row[6]] += 1  # next_shi
                next_counts['ge'][row[7]] += 1   # next_ge
            
            # 计算概率
            probabilities = {
                'bai': {},
                'shi': {},
                'ge': {}
            }
            
            if total_count > 0:
                for position in ['bai', 'shi', 'ge']:
                    for d in range(10):
                        probabilities[position][d] = next_counts[position][d] / total_count
                        
            return probabilities

def format_probability(prob: float) -> str:
    """格式化概率为百分比字符串"""
    return f"{prob * 100:.2f}%"

def main():
    query = FC3DConditionalProbability()
    
    # 示例1：统计百位6后面出现各个数字的概率
    print("百位6后面出现各个数字的概率:")
    probs = query.calculate_next_digit_probability('bai', 6)
    for digit, prob in sorted(probs.items()):
        print(f"数字 {digit}: {format_probability(prob)}")
    print()
    
    # 示例2：统计指定组合后面出现各个数字的概率
    conditions = {'bai': 6, 'shi': 4, 'ge': 5}
    print(f"组合 {conditions} 后面出现各个数字的概率:")
    probs = query.calculate_next_digits_probability(conditions)
    
    for position in ['bai', 'shi', 'ge']:
        print(f"\n{position}位:")
        for digit, prob in sorted(probs[position].items()):
            print(f"数字 {digit}: {format_probability(prob)}")
    
if __name__ == "__main__":
    main()