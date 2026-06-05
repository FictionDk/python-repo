import os
from dotenv import load_dotenv
load_dotenv()

from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC
from mutagen.flac import FLAC


def _extract_mp3_metadata(file_arr):
    """提取MP3元数据"""
    for f_path in file_arr:
        filename_with_ext = os.path.basename(f_path)
        name_without_ext, file_extension = os.path.splitext(filename_with_ext)

        audio, title, artlist = None, None, None
        if file_extension == '.mp3':
            audio = ID3(f_path)
            title = audio.get('TIT2')
            artlist = audio.get('TPE1')
        elif file_extension == '.flac':
            audio = FLAC(f_path)
            title = audio.get('title', [''])[0]
            artlist = audio.get('artist', [''])[0]
        else:
            print("⚠️ 警告: 不支持" + file_extension)
            continue

        if title == None or artlist == None:
            parts = str(name_without_ext).split("-")
            if len(parts) < 2:
                print("  ⚠️ 警告：按 '-' 切割后少于两部分，跳过。")
                continue
            title_by_name, artlist_by_name = parts[1].strip(), parts[0].strip()
            if file_extension == '.mp3':
                audio['TIT2'] = TIT2(encoding=3, text=title_by_name)
                audio['TPE1'] = TPE1(encoding=3, text=artlist_by_name)
                audio.save(f_path)
            elif file_extension == '.flac':
                audio['title'] = title_by_name
                audio['artist'] = artlist_by_name
                audio.save()
            else:
                print("⚠️ 严重警告: 不支持" + file_extension)
                continue
    print("metadata updated")

def traversal(dir_path) -> list[str]:
    if not os.path.isdir(dir_path):
        print(f"❌ 错误：路径 '{dir_path}' 不是一个有效的文件夹。")
        return
    file_path_arr = []
    for filename in os.listdir(dir_path):
        full_file_path = os.path.join(dir_path, filename)
        if os.path.isdir(full_file_path):
            continue
        file_path_arr.append(full_file_path)
    return file_path_arr

def rename_files_in_directory(file_arr):
    for f_path in file_arr:
        filename_with_ext = os.path.basename(f_path)
        dir_path = os.path.dirname(f_path)
        print(f"{dir_path}, {filename_with_ext}")

        print(f"\n--- 正在检查文件：{filename_with_ext}")
        
        # 1. 判定名称中是否有符号 "#"
        if '#' not in filename_with_ext:
            print("  ➡️ 跳过：文件名中不包含 '#'。")
            continue

        # 提取不包含扩展名的文件名（例如：Caldey-Manic Street Preachers#fsyUE）
        name_without_ext, file_extension = os.path.splitext(filename_with_ext)
        
        # 2. 判定不包含扩展名的名称中是否有符号 "-"
        # 此时的 name_without_ext 格式类似：'Caldey-Manic Street Preachers#fsyUE'
        if '-' not in name_without_ext:
            print("  ➡️ 跳过：文件名中不包含 '-'。")
            continue
            
        # 3. 对字符按 "#" 进行切割，只保留 # 前面的部分
        # new_name_part 将是 'Caldey-Manic Street Preachers'
        new_name_part = name_without_ext.split('#')[0]

        # 4. 对保留的部分按 "-" 进行切割
        # parts 将是 ['Caldey', 'Manic Street Preachers']
        parts = new_name_part.split('-')
        
        # 确保切割后至少有两个部分
        if len(parts) < 2:
            print("  ⚠️ 警告：按 '-' 切割后少于两部分，跳过。")
            continue
            
        # 5. 重新组合：将第二个部分放在前面，用 " - " 连接，再加上第一个部分
        # 目标格式：第二个部分 - 第一个部分.扩展名
        # 例如：Manic Street Preachers - Caldey.mp3
        # 倒序重组 parts[1] 是 'Manic Street Preachers'，parts[0] 是 'Caldey'
        new_filename = f"{parts[1].strip()} - {parts[0].strip()}{file_extension}"

        # 完整的旧文件路径和新文件路径
        new_file_path = os.path.join(dir_path, new_filename)

        # 6. 执行重命名
        try:
            os.rename(f_path, new_file_path)
            print(f"  ✅ 成功重命名：")
            print(f"     原名：{filename_with_ext}")
            print(f"     新名：{new_filename}")
        except Exception as e:
            print(f"  ❌ 重命名失败 {filename_with_ext} -> {new_filename}：{e}")

    print("\n🎉 所有文件处理完毕。")

def test():
    directory = os.getenv('DIRECTORY', '.')
    file_arr = traversal(directory)
    print(file_arr)
    #_extract_mp3_metadata(file_arr)
    #rename_files_in_directory(file_arr)

test()