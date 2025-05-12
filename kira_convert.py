import os
import json
import shutil  # 用于备份文件

PINYIN_DICT_FILE = "汉字-拼音词典-完成.ini"  # 汉字-拼音字典文件

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
                original_line_for_warning = line.strip()  # 用于警告信息
                line = line.strip()

                if not line or line.startswith("//"):  # 跳过空行或注释行
                    continue

                # 忽略行首的 '*'
                if line.startswith('*'):
                    line = line[1:]

                # 忽略行尾的 '!'
                if line.endswith('!'):
                    line = line[:-1]

                if not line:  # 如果去除符号后行为空，则跳过
                    print(f"警告：字典文件 '{filepath}' 第 {line_num} 行去除可选符号后为空: '{original_line_for_warning}'")
                    continue

                if len(line) >= 2:  # 至少需要一个汉字和一个拼音字符
                    hanzi = line[0]
                    pinyin = line[1:]
                    if pinyin in pinyin_map:
                        print(f"警告：在字典文件 '{filepath}' 第 {line_num} 行 ('{original_line_for_warning}'), 拼音 '{pinyin}' 已存在，原映射 '{pinyin_map[pinyin]}' 将被 '{hanzi}' 覆盖。")
                    pinyin_map[hanzi] = pinyin
                else:
                    print(f"警告：字典文件 '{filepath}' 第 {line_num} 行格式不正确 (去除符号后长度不足): '{original_line_for_warning}' -> '{line}'")
    except Exception as e:
        print(f"加载拼音字典 '{filepath}' 时出错: {e}")
        return None
    if not pinyin_map:
        print(f"警告：从 '{filepath}' 加载的拼音字典为空。")
    return pinyin_map

def convert_file_name_to_pinyin(file_name, pinyin_map):
    """
    将文件名中的汉字还原为拼音，并在拼音之间加入下划线。
    非汉字字符直接保留并加上下划线。
    """
    result = [""]
    prev_in_map = False  # 上一个字符是否在拼音映射中
    never_in_map = True  # 是否从未在拼音映射中找到字符
    for char in file_name:
        if char in pinyin_map:
            result.append(pinyin_map[char])
            prev_in_map = True
        else:
            if prev_in_map:
                result.append(char)
                never_in_map = False
            else:
                if never_in_map: 
                    result[len(result) - 1] = "_"
                    never_in_map = False
                result[len(result) - 1] += char  # 将非汉字字符与前一个拼音连接
            prev_in_map = False
    return ("_".join(result).replace("_.wav", ".wav"))  # 替换空格为下划线

def process_json_file(json_file_path, pinyin_map):
    """
    读取 JSON 文件并处理其中的 descriptions，转换 file_name 中的汉字为拼音。
    处理完成后备份源文件并写入转换后的内容。
    """
    if not os.path.exists(json_file_path):
        print(f"错误：JSON 文件 '{json_file_path}' 未找到。")
        return

    try:
        # 读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "descriptions" not in data:
            print("错误：JSON 文件中缺少 'descriptions' 字段。")
            return

        # 转换文件名
        for description in data["descriptions"]:
            file_name = description.get("file_name", "")
            if file_name:
                converted_name = convert_file_name_to_pinyin(file_name, pinyin_map)
                print(f"原文件名: {file_name} -> 转换后: {converted_name}")
                description["file_name"] = converted_name
            else:
                print("警告：description 中缺少 'file_name' 字段或字段为空。")

        # 备份源文件
        backup_path = json_file_path + ".bak"
        shutil.copy(json_file_path, backup_path)
        print(f"已备份源文件到: {backup_path}")

        # 写入转换后的内容
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"已将转换后的内容写入文件: {json_file_path}")

    except Exception as e:
        print(f"处理 JSON 文件 '{json_file_path}' 时出错: {e}")

if __name__ == "__main__":
    # 加载拼音字典
    pinyin_map = load_pinyin_to_hanzi_map(PINYIN_DICT_FILE)
    if not pinyin_map:
        exit(1)

    # 指定 JSON 文件路径
    json_file_path = "合并.kirawavtar-desc.json"  # 替换为你的 JSON 文件路径

    # 处理 JSON 文件
    process_json_file(json_file_path, pinyin_map)