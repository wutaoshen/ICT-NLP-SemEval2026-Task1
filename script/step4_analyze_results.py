"""
分析 step4_evaluation_results.json 文件的统计脚本

功能：
1. 统计 final_best_joke 字段中各个模型名称出现的频次
2. 统计 vote_count 字段中各模型获得不同分数（1分、2分、3分、4分）的频次分布
"""

import json
from collections import defaultdict, Counter


def load_json_file(file_path):
    """
    读取JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        解析后的JSON数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def analyze_best_joke_frequency(data):
    """
    统计 final_best_joke 字段中各个模型名称出现的频次
    
    Args:
        data: 评估结果数据列表
        
    Returns:
        模型名称及其出现次数的字典
    """
    best_joke_counter = Counter()
    
    for item in data:
        if 'final_best_joke' in item:
            best_joke = item['final_best_joke']
            best_joke_counter[best_joke] += 1
    
    return dict(best_joke_counter)


def analyze_vote_score_distribution(data):
    """
    统计 vote_count 字段中各模型获得不同分数的频次分布
    
    Args:
        data: 评估结果数据列表
        
    Returns:
        嵌套字典，结构为 {model: {score: count}}
    """
    # 使用嵌套的defaultdict来存储统计结果
    vote_distribution = defaultdict(lambda: defaultdict(int))
    
    for item in data:
        if 'vote_count' in item:
            vote_count = item['vote_count']
            for model, score in vote_count.items():
                vote_distribution[model][score] += 1
    
    return dict(vote_distribution)


def print_best_joke_statistics(best_joke_freq):
    """
    打印 final_best_joke 统计结果
    
    Args:
        best_joke_freq: 模型名称及其出现次数的字典
    """
    print("=" * 80)
    print("统计任务 1: final_best_joke 字段中各个模型名称出现的频次")
    print("=" * 80)
    print()
    
    # 按频次降序排序
    sorted_items = sorted(best_joke_freq.items(), key=lambda x: x[1], reverse=True)
    
    total_count = sum(best_joke_freq.values())
    
    print(f"{'模型名称':<30} {'出现次数':<15} {'占比':<15}")
    print("-" * 80)
    
    for model, count in sorted_items:
        percentage = (count / total_count * 100) if total_count > 0 else 0
        print(f"{model:<30} {count:<15} {percentage:>6.2f}%")
    
    print("-" * 80)
    print(f"{'总计':<30} {total_count:<15} {'100.00%'}")
    print()


def analyze_best_joke_by_score(data):
    """
    统计获得最佳笑话时对应的投票分数分布
    
    Args:
        data: 评估结果数据列表
        
    Returns:
        字典，结构为 {score: count}，表示因获得某分数而成为最佳笑话的次数
    """
    score_to_best_counter = defaultdict(int)
    
    for item in data:
        if 'final_best_joke' in item and 'vote_count' in item:
            best_model = item['final_best_joke']
            vote_count = item['vote_count']
            
            # 获取最佳模型的投票分数
            if best_model in vote_count:
                score = vote_count[best_model]
                score_to_best_counter[score] += 1
    
    return dict(score_to_best_counter)


def print_vote_score_statistics(vote_distribution):
    """
    打印 vote_count 统计结果
    
    Args:
        vote_distribution: 嵌套字典，结构为 {model: {score: count}}
    """
    print("=" * 80)
    print("统计任务 2: vote_count 字段中各模型获得不同分数的频次分布")
    print("=" * 80)
    print()
    
    # 获取所有可能的分数并排序
    all_scores = set()
    for model_scores in vote_distribution.values():
        all_scores.update(model_scores.keys())
    sorted_scores = sorted(all_scores)
    
    # 按模型名称排序
    sorted_models = sorted(vote_distribution.keys())
    
    # 打印表头
    header = f"{'模型名称':<30}"
    for score in sorted_scores:
        header += f"{f'{score}分':<15}"
    header += f"{'总计':<15}"
    print(header)
    print("-" * 80)
    
    # 打印每个模型的统计数据
    for model in sorted_models:
        row = f"{model:<30}"
        model_total = 0
        
        for score in sorted_scores:
            count = vote_distribution[model].get(score, 0)
            row += f"{count:<15}"
            model_total += count
        
        row += f"{model_total:<15}"
        print(row)
    
    # 打印总计行
    print("-" * 80)
    total_row = f"{'各分数总计':<30}"
    grand_total = 0
    
    for score in sorted_scores:
        score_total = sum(vote_distribution[model].get(score, 0) for model in sorted_models)
        total_row += f"{score_total:<15}"
        grand_total += score_total
    
    total_row += f"{grand_total:<15}"
    print(total_row)
    print()
    
    # 打印各分数的分布详情
    print("各分数获得情况的详细统计：")
    print("-" * 80)
    for score in sorted_scores:
        score_total = sum(vote_distribution[model].get(score, 0) for model in sorted_models)
        percentage = (score_total / grand_total * 100) if grand_total > 0 else 0
        print(f"获得 {score} 分的数据项: {score_total} 个 ({percentage:.2f}%)")
    print()


def print_best_joke_by_score_statistics(score_to_best):
    """
    打印因获得某分数而成为最佳笑话的统计结果
    
    Args:
        score_to_best: 字典，结构为 {score: count}
    """
    print("=" * 80)
    print("统计任务 3: 因获得某分数而被评为最佳笑话的次数")
    print("=" * 80)
    print()
    
    # 按分数排序
    sorted_items = sorted(score_to_best.items(), key=lambda x: x[0])
    
    total_count = sum(score_to_best.values())
    
    print(f"{'投票分数':<20} {'获得最佳笑话次数':<20} {'占比':<15}")
    print("-" * 80)
    
    for score, count in sorted_items:
        percentage = (count / total_count * 100) if total_count > 0 else 0
        print(f"{f'{score}分':<20} {count:<20} {percentage:>6.2f}%")
    
    print("-" * 80)
    print(f"{'总计':<20} {total_count:<20} {'100.00%'}")
    print()
    
    # 打印详细说明
    print("说明：")
    print("-" * 80)
    for score, count in sorted_items:
        print(f"因获得 {score} 分投票而被评为最佳笑话: {count} 次")
    print()


def main():
    """
    主函数：执行完整的统计分析流程
    """
    # 设置文件路径
    file_path = r"d:\code\program\semeval2026\eval_part\output\step4_evaluation_results.json"
    
    print("开始读取数据文件...")
    try:
        # 读取JSON文件
        data = load_json_file(file_path)
        print(f"成功读取数据，共 {len(data)} 条记录")
        print()
        
        # 任务1: 统计 final_best_joke 频次
        best_joke_freq = analyze_best_joke_frequency(data)
        print_best_joke_statistics(best_joke_freq)
        
        # 任务2: 统计 vote_count 分数分布
        vote_distribution = analyze_vote_score_distribution(data)
        print_vote_score_statistics(vote_distribution)
        
        # 任务3: 统计因获得某分数而成为最佳笑话的次数
        score_to_best = analyze_best_joke_by_score(data)
        print_best_joke_by_score_statistics(score_to_best)
        
        print("=" * 80)
        print("统计分析完成！")
        print("=" * 80)
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
    except json.JSONDecodeError as e:
        print(f"错误：JSON文件格式错误 - {e}")
    except Exception as e:
        print(f"错误：发生未预期的异常 - {e}")


if __name__ == "__main__":
    main()
