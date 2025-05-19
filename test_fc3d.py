from fc3d_query import FC3DQuery

def main():
    query = FC3DQuery()
    
    print("测试1: 查询最近5期开奖结果")
    recent = query.get_recent_results(5)
    for i, result in enumerate(recent, 1):
        print(f"{i}. 期号: {result.qihao}, 号码: {result.bai}{result.shi}{result.ge}, 日期: {result.date}")
    
    if not recent:
        print("没有查询到开奖结果，请确保数据库中有数据")
        return
    
    print("\n测试2: 号码出现次数统计")
    test_number = (recent[0].bai, recent[0].shi, recent[0].ge)
    count = query.count_occurrences(test_number)
    print(f"号码 {test_number} 出现次数: {count}")
    
    print("\n测试3: 前后记录查询")
    sample_qihao = recent[0].qihao
    adjacent = query.get_adjacent_records(sample_qihao)
    
    print(f"期号 {sample_qihao} 的上期记录:")
    print(f" - {adjacent['prev'].qihao if adjacent['prev'] else '无'}")
    
    print(f"期号 {sample_qihao} 的下期记录:")
    print(f" - {adjacent['next'].qihao if adjacent['next'] else '无'}")

if __name__ == "__main__":
    main()