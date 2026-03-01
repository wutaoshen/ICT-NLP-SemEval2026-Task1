"""
分析 step5_final_results.json 文件的统计脚本

功能：
1. 统计 final_best_joke_model 字段中各个模型名称出现的频次
2. 统计 final_best_from_gpt 字段的 true/false 分布
3. 统计各模型在不同 input_type 下的表现
4. 统计各模型在不同 word_type 下的表现
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


def analyze_best_joke_model_frequency(data):
    """
    统计 final_best_joke_model 字段中各个模型名称出现的频次
    
    Args:
        data: 评估结果数据列表
        
    Returns:
        模型名称及其出现次数的字典
    """
    model_counter = Counter()
    
    for item in data:
        if 'final_best_joke_model' in item:
            model = item['final_best_joke_model']
            model_counter[model] += 1
    
    return dict(model_counter)


def analyze_gpt_usage(data):
    """
    统计 final_best_from_gpt 字段的分布情况
    
    Args:
        data: 评估结果数据列表
        
    Returns:
        字典，包含 true 和 false 的计数
    """
    gpt_counter = Counter()
    
    for item in data:
        if 'final_best_from_gpt' in item:
            gpt_usage = item['final_best_from_gpt']
            gpt_counter[gpt_usage] += 1
    
    return dict(gpt_counter)


def analyze_model_by_input_type(data):
    """
    统计各模型在不同 input_type 下的表现
    
    Args:
        data: 评估结果数据列表
        
    Returns:
        嵌套字典，结构为 {input_type: {model: count}}
    """
    input_type_distribution = defaultdict(lambda: defaultdict(int))
    
    for item in data:
        if 'input_type' in item and 'final_best_joke_model' in item:
            input_type = item['input_type']
            model = item['final_best_joke_model']
            input_type_distribution[input_type][model] += 1
    
    return dict(input_type_distribution)


def analyze_model_by_word_type(data):
    """
    统计各模型在不同 word_type 下的表现
    
    Args:
        data: 评估结果数据列表
        
    Returns:
        嵌套字典，结构为 {word_type: {model: count}}
    """
    word_type_distribution = defaultdict(lambda: defaultdict(int))
    
    for item in data:
        if 'word_type' in item and 'final_best_joke_model' in item:
            word_type = item['word_type']
            model = item['final_best_joke_model']
            word_type_distribution[word_type][model] += 1
    
    return dict(word_type_distribution)


def print_model_frequency_statistics(model_freq):
    """
    打印 final_best_joke_model 统计结果
    
    Args:
        model_freq: 模型名称及其出现次数的字典
    """
    print("=" * 80)
    print("统计任务 1: final_best_joke_model 字段中各个模型名称出现的频次")
    print("=" * 80)
    print()
    
    # 按频次降序排序
    sorted_items = sorted(model_freq.items(), key=lambda x: x[1], reverse=True)
    
    total_count = sum(model_freq.values())
    
    print(f"{'模型名称':<30} {'出现次数':<15} {'占比':<15}")
    print("-" * 80)
    
    for model, count in sorted_items:
        percentage = (count / total_count * 100) if total_count > 0 else 0
        print(f"{model:<30} {count:<15} {percentage:>6.2f}%")
    
    print("-" * 80)
    print(f"{'总计':<30} {total_count:<15} {'100.00%'}")
    print()


def print_gpt_usage_statistics(gpt_usage):
    """
    打印 GPT 使用情况统计
    
    Args:
        gpt_usage: GPT使用情况字典
    """
    print("=" * 80)
    print("统计任务 2: final_best_from_gpt 字段的分布情况")
    print("=" * 80)
    print()
    
    total_count = sum(gpt_usage.values())
    
    print(f"{'是否使用GPT':<30} {'次数':<15} {'占比':<15}")
    print("-" * 80)
    
    # 确保 True 和 False 都显示
    for status in [False, True]:
        count = gpt_usage.get(status, 0)
        percentage = (count / total_count * 100) if total_count > 0 else 0
        status_label = "是 (GPT重评)" if status else "否 (原始评审)"
        print(f"{status_label:<30} {count:<15} {percentage:>6.2f}%")
    
    print("-" * 80)
    print(f"{'总计':<30} {total_count:<15} {'100.00%'}")
    print()


def print_model_by_input_type_statistics(input_type_dist):
    """
    打印各模型在不同输入类型下的统计
    
    Args:
        input_type_dist: 输入类型分布字典
    """
    print("=" * 80)
    print("统计任务 3: 各模型在不同 input_type 下的表现")
    print("=" * 80)
    print()
    
    for input_type in sorted(input_type_dist.keys()):
        print(f"输入类型: {input_type}")
        print("-" * 80)
        
        model_counts = input_type_dist[input_type]
        sorted_models = sorted(model_counts.items(), key=lambda x: x[1], reverse=True)
        total = sum(model_counts.values())
        
        print(f"{'模型名称':<30} {'次数':<15} {'占比':<15}")
        print("-" * 80)
        
        for model, count in sorted_models:
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{model:<30} {count:<15} {percentage:>6.2f}%")
        
        print("-" * 80)
        print(f"{'小计':<30} {total:<15} {'100.00%'}")
        print()


def print_model_by_word_type_statistics(word_type_dist):
    """
    打印各模型在不同文字类型下的统计
    
    Args:
        word_type_dist: 文字类型分布字典
    """
    print("=" * 80)
    print("统计任务 4: 各模型在不同 word_type 下的表现")
    print("=" * 80)
    print()
    
    for word_type in sorted(word_type_dist.keys()):
        word_type_label = "繁体中文" if word_type == "traditional" else "简体中文"
        print(f"文字类型: {word_type_label} ({word_type})")
        print("-" * 80)
        
        model_counts = word_type_dist[word_type]
        sorted_models = sorted(model_counts.items(), key=lambda x: x[1], reverse=True)
        total = sum(model_counts.values())
        
        print(f"{'模型名称':<30} {'次数':<15} {'占比':<15}")
        print("-" * 80)
        
        for model, count in sorted_models:
            percentage = (count / total * 100) if total > 0 else 0
            print(f"{model:<30} {count:<15} {percentage:>6.2f}%")
        
        print("-" * 80)
        print(f"{'小计':<30} {total:<15} {'100.00%'}")
        print()


def main():
    """
    主函数：执行完整的统计分析流程
    """
    # 设置文件路径
    file_path = r"d:\code\program\semeval2026\eval_part\output\step5_final_results.json"
    
    print("开始读取数据文件...")
    try:
        # 读取JSON文件
        data = load_json_file(file_path)
        print(f"成功读取数据，共 {len(data)} 条记录")
        print()
        
        # 任务1: 统计 final_best_joke_model 频次
        model_freq = analyze_best_joke_model_frequency(data)
        print_model_frequency_statistics(model_freq)
        
        # 任务2: 统计 GPT 使用情况
        gpt_usage = analyze_gpt_usage(data)
        print_gpt_usage_statistics(gpt_usage)
        
        # 任务3: 统计各模型在不同 input_type 下的表现
        input_type_dist = analyze_model_by_input_type(data)
        print_model_by_input_type_statistics(input_type_dist)
        
        # 任务4: 统计各模型在不同 word_type 下的表现
        word_type_dist = analyze_model_by_word_type(data)
        print_model_by_word_type_statistics(word_type_dist)
        
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
