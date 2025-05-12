import re
import os
from tqdm import tqdm

# --- 配置 ---
PINYIN_DICT_FILE = "汉字-拼音词典-完成.ini"  # 汉字-拼音字典文件
INPUT_PINYIN_SEQUENCE_FILE = "哈鲁八字表-修改完成.txt"  # 包含拼音序列的输入文件
OUTPUT_HANZI_FILE = "哈鲁八字表-转换结果.txt"  # 输出转换后汉字的文件
# -------------

def load_pinyin_to_hanzi_map(filepath):
    """
    加载拼音到汉字的映射字典。
    文件格式: [可选*]汉字拼音[可选!] (例如: 阿a 或 *阿a 或 阿a! 或 *阿a!)
    """
    pinyin_map = {}
    if not os.path.exists(filepath):
        print(f"错误：拼音字典文件 '{filepath}' 未找到。")
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                original_line_for_warning = line.strip() # 用于警告信息
                line = line.strip()

                if not line or line.startswith("//"): # 跳过空行或注释行
                    continue

                # 忽略行首的 '*'
                if line.startswith('*'):
                    line = line[1:]
                
                # 忽略行尾的 '!'
                if line.endswith('!'):
                    line = line[:-1]

                if not line: # 如果去除符号后行为空，则跳过
                    print(f"警告：字典文件 '{filepath}' 第 {line_num} 行去除可选符号后为空: '{original_line_for_warning}'")
                    continue

                if len(line) >= 2: # 至少需要一个汉字和一个拼音字符
                    hanzi = line[0]
                    pinyin = line[1:]
                    if pinyin in pinyin_map:
                        print(f"警告：在字典文件 '{filepath}' 第 {line_num} 行 ('{original_line_for_warning}'), 拼音 '{pinyin}' 已存在，原映射 '{pinyin_map[pinyin]}' 将被 '{hanzi}' 覆盖。")
                    pinyin_map[pinyin] = hanzi
                else:
                    print(f"警告：字典文件 '{filepath}' 第 {line_num} 行格式不正确 (去除符号后长度不足): '{original_line_for_warning}' -> '{line}'")
    except Exception as e:
        print(f"加载拼音字典 '{filepath}' 时出错: {e}")
        return None
    if not pinyin_map:
        print(f"警告：从 '{filepath}' 加载的拼音字典为空。")
    return pinyin_map

def process_pinyin_file(input_filepath, output_filepath, pinyin_map):
    """
    读取拼音序列文件，替换为汉字，并输出到新文件。
    """
    if not os.path.exists(input_filepath):
        print(f"错误：输入拼音序列文件 '{input_filepath}' 未找到。")
        return None, 0, 0, 0, set()

    lines_processed = 0
    total_pinyins_processed = 0
    pinyins_converted_count = 0
    unmatched_pinyins = set()
    
    try:
        with open(input_filepath, 'r', encoding='utf-8') as infile, \
             open(output_filepath, 'w', encoding='utf-8') as outfile:
            
            # 为了tqdm，先读取所有行来获取总数
            lines = infile.readlines()
            infile.seek(0) # 重置文件指针以便再次读取

            print(f"开始处理文件: {input_filepath}")
            for line in tqdm(lines, desc="处理进度", unit="行"):
                lines_processed += 1
                original_line = line.strip()
                if not original_line: # 跳过空行
                    outfile.write("\n")
                    continue

                # 使用非字母字符作为分隔符
                # re.split会保留分隔符之间的空字符串，例如行首的'_'会导致第一个元素为空
                pinyins_in_line = [p for p in re.split(r'[^a-zA-Z]+', original_line) if p]
                
                converted_sequence = []
                for pinyin in pinyins_in_line:
                    total_pinyins_processed += 1
                    hanzi = pinyin_map.get(pinyin.lower()) # 假设字典中的拼音是小写的
                    if hanzi:
                        converted_sequence.append(hanzi)
                        pinyins_converted_count += 1
                    else:
                        converted_sequence.append(f"[{pinyin}]") # 保留未匹配的拼音，并用方括号标记
                        unmatched_pinyins.add(pinyin)
                
                outfile.write("".join(converted_sequence) + "\n")
        
        print(f"处理完成。结果已保存到: {output_filepath}")
        return lines_processed, total_pinyins_processed, pinyins_converted_count, unmatched_pinyins
        
    except Exception as e:
        print(f"处理文件 '{input_filepath}' 时出错: {e}")
        return lines_processed, total_pinyins_processed, pinyins_converted_count, unmatched_pinyins

def main():
    print("--- 开始拼音转汉字脚本 ---")

    pinyin_to_hanzi = load_pinyin_to_hanzi_map(PINYIN_DICT_FILE)

    if pinyin_to_hanzi is None:
        print("未能加载拼音字典，脚本终止。")
        return
    
    if not pinyin_to_hanzi:
         print("警告：拼音字典为空，可能所有拼音都无法转换。")


    lines_count, pinyins_total, pinyins_converted, not_found_pinyins = process_pinyin_file(
        INPUT_PINYIN_SEQUENCE_FILE,
        OUTPUT_HANZI_FILE,
        pinyin_to_hanzi
    )

    print("\n--- 处理结果统计 ---")
    if lines_count is not None:
        print(f"已处理行数: {lines_count}")
        print(f"已处理拼音总数: {pinyins_total}")
        print(f"成功转换拼音数: {pinyins_converted}")
        
        if pinyins_total > 0:
            success_rate = (pinyins_converted / pinyins_total) * 100 if pinyins_total > 0 else 0
            print(f"转换成功率: {success_rate:.2f}%")

        if not_found_pinyins:
            print(f"\n以下 {len(not_found_pinyins)} 个拼音未在字典中找到 (已去重):")
            # 只显示前20个未匹配的，防止过多输出
            for i, pinyin in enumerate(list(not_found_pinyins)):
                if i < 20:
                    print(f"  - {pinyin}")
                else:
                    print(f"  ...等另外 {len(not_found_pinyins) - 20} 个未显示")
                    break
            print("请检查您的拼音字典文件或输入文件中的这些拼音。")
        else:
            if pinyins_total > 0 : # 确保确实处理了拼音
                 print("所有在输入文件中找到的拼音均已成功转换！")
            elif lines_count > 0: # 处理了行但没有拼音
                 print("输入文件中未找到可识别的拼音。")


    print("--- 脚本执行完毕 ---")

if __name__ == "__main__":
    main()