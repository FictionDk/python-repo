import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from music_mut import MusicProcessor, write_to_music_txt
import llm

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # 从环境变量获取配置
    directory = os.getenv('DIRECTORY', '.')

    try:
        # 初始化处理器
        processor = MusicProcessor(directory)
        
        # 扫描文件
        logger.info(f"正在扫描目录: {directory}")
        music_files = processor.scan_files()
        logger.info(f"找到 {len(music_files)} 个音乐文件")

        # for mf in processor.music_files:
        #     print("*"*40)
        #     print(f"{mf.path},{mf.err}")
        #     #print(llm.music_infer(str(mf.path)))
        #     #print(f"{mf.metadata}, {mf.extension}")

        # 处理文件
        logger.info("开始处理文件...")
        results = processor.process_files()

        # 写入music.txt
        metadata_list = []
        for music_file in processor.music_files:
            r = music_file.metadata.to_dict()
            r['err'] = music_file.err
            metadata_list.append(r)

        if metadata_list:
            write_to_music_txt(metadata_list)

        # 输出结果
        logger.info("处理完成!")
        logger.info(f"总计: {results['total']} 个文件")
        logger.info(f"成功处理: {results['processed']} 个")
        logger.info(f"元数据更新: {results['updated']} 个")
        logger.info(f"文件重命名: {results['renamed']} 个")
        logger.info(f"处理失败: {results['failed']} 个")
        
    except Exception as e:
        logger.error(f"处理失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
