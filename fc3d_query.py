import sqlite3
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class FC3DResult:
    """3D开奖结果数据类"""
    id: int
    qihao: str
    bai: int
    shi: int
    ge: int
    date: str
    created_at: str

class FC3DQuery:
    def __init__(self, db_path: str = "/root/code/lottery/lottery.db"):
        """初始化查询器"""
        self.db_path = db_path
        
    def _connect(self):
        """创建数据库连接"""
        return sqlite3.connect(self.db_path)
        
    def get_recent_results(self, limit: int = 10) -> List[FC3DResult]:
        """
        查询最近limit期开奖结果
        :param limit: 查询期数，默认10期
        :return: 开奖结果列表
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, qihao, bai, shi, ge, date, created_at 
                FROM fc3d 
                ORDER BY date DESC 
                LIMIT ?
            """, (limit,))
            return [FC3DResult(*row) for row in cursor.fetchall()]
            
    def count_occurrences(self, number: Tuple[int, int, int]) -> int:
        """
        统计指定号码出现次数
        :param number: 要查询的号码，格式为(百位, 十位, 个位)
        :return: 出现次数
        """
        bai, shi, ge = number
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM fc3d 
                WHERE bai = ? AND shi = ? AND ge = ?
            """, (bai, shi, ge))
            return cursor.fetchone()[0]
            
    def get_adjacent_records(self, qihao: str) -> Dict[str, Optional[FC3DResult]]:
        """
        获取指定期号的前后开奖记录
        :param qihao: 要查询的期号
        :return: 包含前后记录的字典 {'prev': 上期结果, 'next': 下期结果}
        """
        result = {'prev': None, 'next': None}
        with self._connect() as conn:
            cursor = conn.cursor()
            
            # 查询上期记录
            cursor.execute("""
                SELECT id, qihao, bai, shi, ge, date, created_at
                FROM fc3d 
                WHERE date < (SELECT date FROM fc3d WHERE qihao = ?)
                ORDER BY date DESC 
                LIMIT 1
            """, (qihao,))
            prev_row = cursor.fetchone()
            if prev_row:
                result['prev'] = FC3DResult(*prev_row)
                
            # 查询下期记录
            cursor.execute("""
                SELECT id, qihao, bai, shi, ge, date, created_at
                FROM fc3d 
                WHERE date > (SELECT date FROM fc3d WHERE qihao = ?)
                ORDER BY date ASC 
                LIMIT 1
            """, (qihao,))
            next_row = cursor.fetchone()
            if next_row:
                result['next'] = FC3DResult(*next_row)
                
        return result

    def get_by_qihao(self, qihao: str) -> Optional[FC3DResult]:
        """
        按期号查询开奖结果
        :param qihao: 期号
        :return: 开奖结果，如果不存在返回None
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, qihao, bai, shi, ge, date, created_at 
                FROM fc3d 
                WHERE qihao = ?
            """, (qihao,))
            row = cursor.fetchone()
            return FC3DResult(*row) if row else None


    def find_position_sequence(self, position: str, seq: List[int]) -> List[str]:
        """
        查找历史上指定位置出现指定数字序列的中间期号
        :param position: 'bai'、'shi' 或 'ge'
        :param seq: 长度为3的数字序列，如 [9, 1, 4]
        :return: 满足条件的中间期号列表
        """
        if position not in ('bai', 'shi', 'ge'):
            raise ValueError("position 必须为 'bai', 'shi' 或 'ge'")
        col = position
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT t2.qihao
                FROM fc3d t1
                JOIN fc3d t2 ON t2.id = t1.id + 1
                JOIN fc3d t3 ON t3.id = t2.id + 1
                WHERE t1.{col} = ? AND t2.{col} = ? AND t3.{col} = ?
                ORDER BY t2.id
            """, (seq[0], seq[1], seq[2]))
            return [row[0] for row in cursor.fetchall()]

    def get_surrounding_results(self, qihao: str, n: int = 5) -> List[FC3DResult]:
        """
        获取指定期号前后n期的开奖结果（包含自身）
        :param qihao: 期号
        :param n: 前后期数
        :return: 结果列表
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            # 先查出当前id
            cursor.execute("SELECT id FROM fc3d WHERE qihao = ?", (qihao,))
            row = cursor.fetchone()
            if not row:
                return []
            cur_id = row[0]
            # 查前后n期
            cursor.execute("""
                SELECT id, qihao, bai, shi, ge, date, created_at
                FROM fc3d
                WHERE id BETWEEN ? AND ?
                ORDER BY id
            """, (cur_id - n, cur_id + n))
            return [FC3DResult(*r) for r in cursor.fetchall()]

if __name__ == "__main__":
    # 使用示例
    #query = FC3DQuery()
    
    # print("=== 最近5期开奖结果 ===")
    # for result in query.get_recent_results(5):
    #     print(f"期号: {result.qihao}, 号码: {result.bai}{result.shi}{result.ge}, 开奖日期: {result.date}")
    
    # print("\n=== 号码统计示例 ===")
    # test_number = (1, 2, 3)
    # count = query.count_occurrences(test_number)
    # print(f"号码 {test_number} 历史出现次数: {count}")
    
    # print("\n=== 前后记录查询示例 ===")
    # sample_qihao = "2023001"  # 替换为实际存在的期号
    # adjacent = query.get_adjacent_records(sample_qihao)
    # print(f"期号 {sample_qihao} 的上期记录: {adjacent['prev'].qihao if adjacent['prev'] else '无'}")
    # print(f"期号 {sample_qihao} 的下期记录: {adjacent['next'].qihao if adjacent['next'] else '无'}")
    query = FC3DQuery()
    output_lines = []

    print("=== 最近10期开奖结果 ===")
    output_lines.append(f"\n=== 最近10期开奖结果 ===\n")    
    for result in query.get_recent_results(10):
        print(f"期号: {result.qihao}, 号码: {result.bai}{result.shi}{result.ge}, 开奖日期: {result.date}")
        output_lines.append(f"期号: {result.qihao}, 号码: {result.bai}{result.shi}{result.ge}, 开奖日期: {result.date}")

    

    # 自动获取最近3期的百、十、个位数字序列
    recent3 = query.get_recent_results(3)

  

    
    if len(recent3) == 3:
        bai_seq = [r.bai for r in recent3]
        shi_seq = [r.shi for r in recent3]
        ge_seq = [r.ge for r in recent3]

        

        for pos, seq, label in zip(
            ['bai', 'shi', 'ge'],
            [bai_seq, shi_seq, ge_seq],
            ['百位', '十位', '个位']
        ):
            output_lines.append(f"\n=== 最近三期{label}连号 {seq} 的历史中间期号及前后5期 ===")
            qihaos = query.find_position_sequence(pos, seq)
           
            for qihao in qihaos:
                output_lines.append(f"\n--- {label}连号中间期号: {qihao} 前后5期 ---")
                results = query.get_surrounding_results(qihao, 5)
                
                for r in results:
                    output_lines.append(f"期号: {r.qihao}, 百位: {r.bai}, 十位: {r.shi}, 个位: {r.ge}, 日期: {r.date}")

        # 输出到屏幕
        for line in output_lines:
            print(line)

       
        # 写入文件
        with open("out.txt", "w", encoding="utf-8") as f:
            for line in output_lines:
                f.write(line + "\n")
        print("\n结果已写入文件：out.txt")
    else:
        print("数据不足3期，无法自动查询连号。")
