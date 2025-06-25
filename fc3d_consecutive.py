from fc3d_query import FC3DQuery
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class ConsecutiveResult:
    qihao: str
    number: int
    next_qihao: str
    next_number: int

class FC3DConsecutiveQuery(FC3DQuery):
    def find_consecutive_numbers(self, position: str, limit: int = 100) -> List[Tuple[str, int, str, int]]:
        """
        查找指定位置的连号
        :param position: 位置 ('bai', 'shi', 'ge')
        :param limit: 查询最近多少期数据
        :return: 连号列表，每项包含 (期号1, 数字1, 期号2, 数字2)
        """
        if position not in ('bai', 'shi', 'ge'):
            raise ValueError("position must be one of 'bai', 'shi', 'ge'")
            
        with self._connect() as conn:
            cursor = conn.cursor()
            # 查询最近limit期的数据，按日期降序排列
            cursor.execute(f"""
                WITH recent AS (
                    SELECT qihao, {position}, date
                    FROM fc3d 
                    ORDER BY date DESC 
                    LIMIT ?
                )
                SELECT 
                    r1.qihao,
                    r1.{position},
                    r2.qihao,
                    r2.{position}
                FROM recent r1
                JOIN recent r2 ON r1.date > r2.date
                WHERE ABS(r1.{position} - r2.{position}) = 1
                AND r1.date = (
                    SELECT MIN(date)
                    FROM recent r3
                    WHERE r3.date > r2.date
                )
                ORDER BY r1.date DESC
            """, (limit,))
            
            return cursor.fetchall()

def main():
    query = FC3DConsecutiveQuery()
    positions = ['bai', 'shi', 'ge']
    position_names = {'bai': '百位', 'shi': '十位', 'ge': '个位'}
    
    for pos in positions:
        print(f"\n=== {position_names[pos]}连号情况 ===")
        results = query.find_consecutive_numbers(pos)
        for qihao1, num1, qihao2, num2 in results:
            if num1 > num2:
                print(f"期号: {qihao2} -> {qihao1}, 号码: {num2} -> {num1}")
            else:
                print(f"期号: {qihao1} -> {qihao2}, 号码: {num1} -> {num2}")

if __name__ == "__main__":
    main()