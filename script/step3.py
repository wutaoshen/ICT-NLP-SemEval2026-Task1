#step3.py 根据新闻标题、新闻内容总结和关键词联想生成幽默段子
import dashscope
from dashscope import Generation
import json
from opencc import OpenCC
import time
import re

# 设置DashScope API密钥 (替换为你的实际API_KEY)
dashscope.api_key = ""

def parse_json_response(content):
    """
    解析API返回的JSON内容，支持markdown格式
    :param content: API返回的原始内容
    :return: 解析后的JSON对象
    """
    try:
        # 首先尝试直接解析JSON
        return json.loads(content)
    except json.JSONDecodeError:
        # 如果失败，尝试移除markdown代码块标记
        try:
            cleaned = content.strip()
            # 移除markdown代码块标记（```json 和 ```）
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            
            # 再次尝试解析
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # 如果仍然失败，返回错误信息
            raise json.JSONDecodeError(f"JSON解析失败: {e.msg}", e.doc, e.pos)

def news_generate_humor_joke(news_headline, news_summary, keyword1, keyword2,keyword1_associations,keyword2_associations,modelname="qwen-max"):
    """
    生成幽默笑话的核心函数
    :param news_headline: 新闻标题
    :param news_summary: 新闻内容总结
    :param keyword1: 从标题提取的关键词1
    :param keyword2: 从标题提取的关键词2
    :param keyword1_associations: 关键词1的3个联想词
    :param keyword2_associations: 关键词2的3个联想词
    :return: 生成的笑话结果
    """
    
    # 构建系统提示 (包含所有幽默类型说明)
    system_prompt = """你是一位中文幽默大师，精通17种经典笑话类型。请严格按以下规则创作：
    1.阅读新闻标题和内容总结，理解其核心信息
    2. 从以下两个关键词集合中各选1个词（共2个词），并从中文笑话类型中挑选一种，构思最具幽默感的组合：
    集合A: [{keyword1}, {association1}, {association2}, {association3}]
    集合B: [{keyword2}, {association4}, {association5}, {association6}]
    中文笑话的经典类型包括但不限于：
    (1) **文字游戏 / 双关** — 利用同音或多义造成出乎意料的幽默。
   示例：老师问：「为什么你作业没做？」学生答：「我在做人生题（题 ~ 体）……」
    (2) **设问-反转（经典一问一答）** — 先提出常规期待，再用反转的结论击中笑点。
    示例：问：「为什么猫怕水？」答：「因为它们的微博还没洗干净。」
    (3) **夸张法** — 把某事放大到荒诞程度产生喜感。
    示例：他讲笑话讲到楼下都停电了——没人受得了那电量。
    (4) **拟人化 / 拟物化** — 把无生命或抽象事物当人来写，常带反差。
    示例：手机对耳机说：「别生气，我只是多线作业而已。」
    (5) **冷笑话 / 无厘头** — 看似平淡或逻辑断裂，但正因反常产生笑点。
    示例：为什么蜗牛不参加马拉松？因为它怕被广告追着跑。
    (6) **自嘲 / 自黑** — 用自己的缺点或失败做素材，拉近观众距离。
    示例：我减肥了——每天减一包零食，钱包瘦了。
    (7) **生活观察 / 段子** — 从日常小事中提炼共鸣，然后用机智结尾。
    示例：电梯里有人按了 12 楼，大家都在默默减肥——因为都不想再停。
    (8) **讽刺 / 社会批评** — 用幽默去指出社会现象或人性的荒谬（要注意尺度）。
    示例：会议的主题是「提高效率」，结果开了三小时讨论怎么缩短开会时间。
    (9) **荒诞派 / 超现实** — 用违反常理的场景制造强烈喜感或惊讶。
    示例：他给植物唱歌，结果盆栽开出了 Spotify 订阅提示。
    (10) **比喻 / 类比幽默** — 用生动类比把复杂事物简化为有趣画面。
        示例：恋爱就像 Wi-Fi，信号好时大家笑成一团，断了就立刻开始翻路由器。
    (11) **文化梗 / 流行语致敬** — 结合时下热词、影视台词或梗，提高亲切度（注意版权与敏感话题）。
        示例：他追剧追到深夜——现在连梦都是会员专享。
    (12) **脑筋急转弯 / 谜语式** — 依靠机智与反向思考，常用于短小互动。
        示例：问：「什么东西越洗越脏？」答：「水（因为你拿它洗别的东西）。」
    (13) **职业型笑话** — 围绕特定职业的特点展开，制造职业相关的幽默。
        示例：医生对病人说：「你这病得戒烟。」病人：「可我没抽烟啊。」医生：「那正好，戒了就不会复发了。」
    (14) **造句笑话** — 用词语造句时故意曲解原意，产生意外效果。
        示例：老师让用「难过」造句，学生写：「家门口的小河很难过——每次都要绕路。」
    (15) **歇后语笑话** — 利用歇后语的前后呼应，通过谐音或双关制造幽默，是中国传统幽默形式。
        示例：泥菩萨过河——自身难保（字面意思与比喻义的反差）。
    (16) **单纯性 vs 倾向性笑话** — 前者无需特定知识就能理解，后者需要特定文化背景或语境才能领会笑点。
        示例（倾向性）：程序员说「这个bug很好找」，结果找了三天——只有同行才懂的痛。
    (17) **传统讽刺笑话** — 中国古代笑话常见形式，带点「酸酸的嘲讽」，常针对人性弱点或社会现象。
    示例：县官断案问：「谁先动手？」一人答：「他先动口。」（讽刺官僚作风）
    3. 优先使用提供的关键词集合创作一则与新闻内容相关的笑话，若所有组合效果不佳则自行进行额外的构思（需说明原因）
    4. 笑话必须与新闻内容相关，简洁新颖，真实有趣，长度40-60字
    5. 笑话中禁止包含敏感、政治、宗教等话题，以及不要出现刻板印象、低俗内容、毒性等内容
    5. 【严格遵守】输出必须是纯JSON，包含以下字段：{{"reason": "选择理由", "joke": "笑话内容"}}
    """.format(
        keyword1=keyword1,
        association1=keyword1_associations[0], association2=keyword1_associations[1], association3=keyword1_associations[2],
        keyword2=keyword2,
        association4=keyword2_associations[0], association5=keyword2_associations[1], association6=keyword2_associations[2]
    )
    # 新提示词，40字到60字之间，简洁新颖
    # 构建用户提示
    user_prompt = f"""新闻标题：{news_headline}
    新闻总结：{news_summary}
    任务：请阅读新闻标题和内容总结，按系统提示规则创作笑话"""

    max_retries = 3
    retry_delay = 1  # 重试间隔(秒)
    for attempt in range(max_retries):
        try:
            # 调用通义千问API (使用qwen-max模型)
            response = Generation.call(
                model=modelname,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                extra_body={"enable_thinking": True},
                result_format="message",
                temperature=0.85,  # 增加创意性
                top_p=0.9
            )
            
            # 解析API响应
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 尝试提取JSON结构
                try:
                    # 使用增强的JSON解析函数
                    result = parse_json_response(content)
                    return result  # 成功解析,直接返回
                except json.JSONDecodeError as json_error:
                    # JSON解析失败,记录错误信息
                    if attempt < max_retries - 1:
                        print(f"JSON解析失败 (尝试 {attempt + 1}/{max_retries}): {str(json_error)}")
                        time.sleep(retry_delay)
                        continue  # 继续下一次重试
                    else:
                        # 所有重试都失败,使用备用解析方案
                        print(f"JSON解析失败,已达最大重试次数,使用备用方案")
                        return {
                            "reason": "",
                            "joke": "",
                            "error": "JSON解析失败",
                            "raw_response": content,
                            "attempts": max_retries
                        }
            else:
                # API调用失败
                if attempt < max_retries - 1:
                    print(f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {response.code}")
                    time.sleep(retry_delay)
                    continue  # 继续下一次重试
                else:
                    # 所有重试都失败
                    return {
                        "reason": "",
                        "joke": "",
                        "error": f"API调用失败: {response.code}",
                        "message": response.message,
                        "attempts": max_retries
                    }
                
        except Exception as e:
            # 捕获其他异常
            if attempt < max_retries - 1:
                print(f"处理异常 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
                continue  # 继续下一次重试
            else:
                # 所有重试都失败
                return {
                    "reason": "",
                    "joke": "",
                    "error": "处理异常",
                    "details": str(e),
                    "attempts": max_retries
                }

def keyword_generate_humor_joke(keyword1, keyword2,keyword1_associations,keyword2_associations,modelname="qwen-max"):
    """
    仅根据关键词联想生成幽默笑话的核心函数
    :param keyword1: 关键词1
    :param keyword2: 关键词2
    :param keyword1_associations: 关键词1的3个联想词
    :param keyword2_associations: 关键词2的3个联想词
    :return: 生成的笑话结果
    """
    # 构建系统提示 (包含所有幽默类型说明)
    system_prompt = """你是一位中文幽默大师，精通17种经典笑话类型。请严格按以下规则创作：
    1.你需要生成一则与关键词{keyword1}和{keyword2}相关的幽默笑话,笑话中必须包含有这两个关键词。
    2. 从以下两个关键词集合中各选1个词（共2个词），并从中文笑话类型中挑选一种，构思最具幽默感的组合：
    集合A: [{keyword1}, {association1}, {association2}, {association3}]
    集合B: [{keyword2}, {association4}, {association5}, {association6}]
    中文笑话的经典类型包括但不限于：
    (1) **文字游戏 / 双关** — 利用同音或多义造成出乎意料的幽默。
   示例：老师问：「为什么你作业没做？」学生答：「我在做人生题（题 ~ 体）……」
    (2) **设问-反转（经典一问一答）** — 先提出常规期待，再用反转的结论击中笑点。
    示例：问：「为什么猫怕水？」答：「因为它们的微博还没洗干净。」
    (3) **夸张法** — 把某事放大到荒诞程度产生喜感。
    示例：他讲笑话讲到楼下都停电了——没人受得了那电量。
    (4) **拟人化 / 拟物化** — 把无生命或抽象事物当人来写，常带反差。
    示例：手机对耳机说：「别生气，我只是多线作业而已。」
    (5) **冷笑话 / 无厘头** — 看似平淡或逻辑断裂，但正因反常产生笑点。
    示例：为什么蜗牛不参加马拉松？因为它怕被广告追着跑。
    (6) **自嘲 / 自黑** — 用自己的缺点或失败做素材，拉近观众距离。
    示例：我减肥了——每天减一包零食，钱包瘦了。
    (7) **生活观察 / 段子** — 从日常小事中提炼共鸣，然后用机智结尾。
    示例：电梯里有人按了 12 楼，大家都在默默减肥——因为都不想再停。
    (8) **讽刺 / 社会批评** — 用幽默去指出社会现象或人性的荒谬（要注意尺度）。
    示例：会议的主题是「提高效率」，结果开了三小时讨论怎么缩短开会时间。
    (9) **荒诞派 / 超现实** — 用违反常理的场景制造强烈喜感或惊讶。
    示例：他给植物唱歌，结果盆栽开出了 Spotify 订阅提示。
    (10) **比喻 / 类比幽默** — 用生动类比把复杂事物简化为有趣画面。
        示例：恋爱就像 Wi-Fi，信号好时大家笑成一团，断了就立刻开始翻路由器。
    (11) **文化梗 / 流行语致敬** — 结合时下热词、影视台词或梗，提高亲切度（注意版权与敏感话题）。
        示例：他追剧追到深夜——现在连梦都是会员专享。
    (12) **脑筋急转弯 / 谜语式** — 依靠机智与反向思考，常用于短小互动。
        示例：问：「什么东西越洗越脏？」答：「水（因为你拿它洗别的东西）。」
    (13) **职业型笑话** — 围绕特定职业的特点展开，制造职业相关的幽默。
        示例：医生对病人说：「你这病得戒烟。」病人：「可我没抽烟啊。」医生：「那正好，戒了就不会复发了。」
    (14) **造句笑话** — 用词语造句时故意曲解原意，产生意外效果。
        示例：老师让用「难过」造句，学生写：「家门口的小河很难过——每次都要绕路。」
    (15) **歇后语笑话** — 利用歇后语的前后呼应，通过谐音或双关制造幽默，是中国传统幽默形式。
        示例：泥菩萨过河——自身难保（字面意思与比喻义的反差）。
    (16) **单纯性 vs 倾向性笑话** — 前者无需特定知识就能理解，后者需要特定文化背景或语境才能领会笑点。
        示例（倾向性）：程序员说「这个bug很好找」，结果找了三天——只有同行才懂的痛。
    (17) **传统讽刺笑话** — 中国古代笑话常见形式，带点「酸酸的嘲讽」，常针对人性弱点或社会现象。
    示例：县官断案问：「谁先动手？」一人答：「他先动口。」（讽刺官僚作风）
    3. 优先使用提供的关键词集合创作笑话，若所有组合效果均不佳则自行进行额外的构思（需说明原因）
    4. 笑话必须包含两个关键词{keyword1}和{keyword2}，简洁新颖，真实有趣，长度40-60字
    5. 笑话中禁止包含敏感、政治、宗教等话题，以及不要出现刻板印象、低俗内容、毒性等内容
    5. 【严格遵守】输出必须是纯JSON，包含以下字段：{{"reason": "选择理由", "joke": "笑话内容"}}
    """.format(
        keyword1=keyword1,
        association1=keyword1_associations[0], association2=keyword1_associations[1], association3=keyword1_associations[2],
        keyword2=keyword2,
        association4=keyword2_associations[0], association5=keyword2_associations[1], association6=keyword2_associations[2]
    )
    # 构建用户提示
    user_prompt = f"""关键词1：{keyword1}
    关键词：{keyword2}
    任务：请结合两个关键词，按系统提示规则创作笑话"""
    
    max_retries = 3
    retry_delay = 1  # 重试间隔(秒)
    for attempt in range(max_retries):
        try:
            # 调用通义千问API (使用qwen-max模型)
            response = Generation.call(
                model=modelname,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                extra_body={"enable_thinking": True},
                result_format="message",
                temperature=0.85,  # 增加创意性
                top_p=0.9
            )
            
            # 解析API响应
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                # 尝试提取JSON结构
                try:
                    # 使用增强的JSON解析函数
                    result = parse_json_response(content)
                    return result  # 成功解析,直接返回
                except json.JSONDecodeError as json_error:
                    # JSON解析失败,记录错误信息
                    if attempt < max_retries - 1:
                        print(f"JSON解析失败 (尝试 {attempt + 1}/{max_retries}): {str(json_error)}")
                        time.sleep(retry_delay)
                        continue  # 继续下一次重试
                    else:
                        # 所有重试都失败,使用备用解析方案
                        print(f"JSON解析失败,已达最大重试次数,使用备用方案")
                        return {
                            "error": "JSON解析失败",
                            "raw_response": content,
                            "attempts": max_retries
                        }
            else:
                # API调用失败
                if attempt < max_retries - 1:
                    print(f"API调用失败 (尝试 {attempt + 1}/{max_retries}): {response.code}")
                    time.sleep(retry_delay)
                    continue  # 继续下一次重试
                else:
                    # 所有重试都失败
                    return {
                        "error": f"API调用失败: {response.code}",
                        "message": response.message,
                        "attempts": max_retries
                    }
                
        except Exception as e:
            # 捕获其他异常
            if attempt < max_retries - 1:
                print(f"处理异常 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
                continue  # 继续下一次重试
            else:
                # 所有重试都失败
                return {
                    "error": "处理异常",
                    "details": str(e),
                    "attempts": max_retries
                }

def joke_gen(input_file, output_file, modelname="qwen-max"):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    processed_data = []
    for item in data:
        item_type = item.get('word_type','')
        print(item_type)
        if item.get('input_type','') == "新闻标题":
            joke_result = news_generate_humor_joke(
                news_headline=item.get("news_headline", ""),
                news_summary=item.get("news_summary", ""),
                keyword1=item.get("keyword1", ""),
                keyword2=item.get("keyword2", ""),
                keyword1_associations=item.get("keyword1_associations", []),
                keyword2_associations=item.get("keyword2_associations", []),
                modelname=modelname
            )
            if item.get('word_type','') == 'traditional':
                cc = OpenCC('s2tw')
                joke_result["reason"] = cc.convert(joke_result["reason"])
                joke_result["joke"] = cc.convert(joke_result["joke"])
            print(joke_result)
            new_item = {
                'id': item.get('id', ''),
                'news_headline': item.get('news_headline', ''),
                'keyword1': item.get('keyword1', ''),
                'keyword2': item.get('keyword2', ''),
                'input_type': item.get('input_type', ''),
                'word_type': item.get('word_type', ''),
                'news_summary': item.get('news_summary', ''),
                'keyword1_associations': item.get('keyword1_associations', []),
                'keyword2_associations': item.get('keyword2_associations', []),
                'joke_result': joke_result,
                'chosen_model': modelname
            }
            processed_data.append(new_item)
        else:
            joke_result = keyword_generate_humor_joke(
                keyword1=item.get("keyword1", ""),
                keyword2=item.get("keyword2", ""),
                keyword1_associations=item.get("keyword1_associations", []),
                keyword2_associations=item.get("keyword2_associations", []),
                modelname=modelname
            )
            print(joke_result)
            new_item = {
                'id': item.get('id', ''),
                'news_headline': item.get('news_headline', ''),
                'keyword1': item.get('keyword1', ''),
                'keyword2': item.get('keyword2', ''),
                'input_type': item.get('input_type', ''),
                'word_type': item.get('word_type', ''),
                'keyword1_associations': item.get('keyword1_associations', []),
                'keyword2_associations': item.get('keyword2_associations', []),
                'joke_result': joke_result,
                'chosen_model': modelname
            }
            processed_data.append(new_item)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"成功处理 {len(processed_data)} 条数据")

# ================== 使用示例 ==================
if __name__ == "__main__":
    input_file = "../output/step2.json"
    output_file1 = "../output/step3_qwen-max.json"
    #joke_gen(input_file, output_file1,modelname="qwen-max")

    output_file2 = "../output/step3_deepseek-v3.2.json"
    #joke_gen(input_file, output_file2,modelname="deepseek-v3.2")

    output_file3 = "../output/step3_kimi-k2-thinking-short.json"
    joke_gen(input_file, output_file3,modelname="kimi-k2-thinking")

    output_file4 = "../output/step3_glm-4.7.json"
    #joke_gen(input_file, output_file4,modelname="glm-4.7")