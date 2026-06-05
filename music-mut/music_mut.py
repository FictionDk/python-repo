"""
音乐文件元数据处理模块
"""
import re
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC
from mutagen.flac import FLAC
from tinytag import TinyTag
from tqdm import tqdm
import logging
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 导入 llm 模块
from llm import music_infer

logger = logging.getLogger(__name__)

@dataclass
class MusicMetadata:
    """音乐元数据模型"""
    title: str = ""
    artist: str = ""
    album: str = ""
    date: str = ""
    
    def is_complete(self) -> bool:
        """检查元数据是否完整"""
        return all([self.title, self.artist, self.album, self.date])
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "date": self.date
        }

class MusicFile:
    """音乐文件处理器"""
    
    SUPPORTED_EXTENSIONS = {'.mp3', '.flac', '.wav'}
    
    def __init__(self, file_path: str):
        self.path = Path(file_path)
        self.extension = self.path.suffix.lower()
        self.metadata = MusicMetadata()
        self.err = ""
        
    def is_supported(self) -> bool:
        """检查文件格式是否支持"""
        return self.extension in self.SUPPORTED_EXTENSIONS
    
    def extract_metadata(self) -> MusicMetadata:
        """提取元数据"""
        try:
            if self.extension == '.mp3':
                return self._extract_mp3_metadata()
            elif self.extension == '.flac':
                return self._extract_flac_metadata()
            elif self.extension == '.wav':
                return self._extract_wav_metadata()
        except Exception as e:
            self.err = f"提取元数据失败 {self.path}: {e}"
            #logger.error(f"提取元数据失败 {self.path}: {e}")
            return MusicMetadata()
        return MusicMetadata()
    
    def _extract_mp3_metadata(self) -> MusicMetadata:
        """提取MP3元数据"""
        audio = ID3(self.path)
        metadata = MusicMetadata()
        
        if 'TIT2' in audio:
            metadata.title = str(audio['TIT2'])
        if 'TPE1' in audio:
            metadata.artist = str(audio['TPE1'])
        if 'TALB' in audio:
            metadata.album = str(audio['TALB'])
        if 'TDRC' in audio:
            metadata.date = str(audio['TDRC'])
        return metadata

    
    def _extract_flac_metadata(self) -> MusicMetadata:
        """提取FLAC元数据"""
        audio = FLAC(self.path)
        metadata = MusicMetadata()

        metadata.title = audio.get('title', [''])[0]
        metadata.artist = audio.get('artist', [''])[0]
        metadata.album = audio.get('album', [''])[0]
        metadata.date = audio.get('date', [''])[0]

        return metadata

    
    def _extract_wav_metadata(self) -> MusicMetadata:
        """提取WAV元数据"""
        tag = TinyTag.get(self.path)
        metadata = MusicMetadata()
        if tag is not None:
            metadata.title = tag.title
            metadata.artist = tag.artist
            metadata.album = tag.album
            metadata.date = ''
        return metadata
    
    def update_metadata(self, metadata: MusicMetadata) -> bool:
        """更新元数据"""
        try:
            if self.extension == '.mp3':
                return self._update_mp3_metadata(metadata)
            elif self.extension == '.flac':
                return self._update_flac_metadata(metadata)
            elif self.extension == '.wav':
                return self._update_wav_metadata(metadata)
        except Exception as e:
            self.err = f"{self.err} | 更新元数据失败 {self.path}: {e}"
            return False
        return True
    
    def _update_mp3_metadata(self, metadata: MusicMetadata) -> bool:
        """更新MP3元数据"""
        audio = ID3(self.path) if self.path.exists() else ID3()
        
        audio['TIT2'] = TIT2(encoding=3, text=metadata.title)
        audio['TPE1'] = TPE1(encoding=3, text=metadata.artist)
        audio['TALB'] = TALB(encoding=3, text=metadata.album)
        audio['TDRC'] = TDRC(encoding=3, text=metadata.date)
        
        audio.save(self.path)
        return True

    
    def _update_flac_metadata(self, metadata: MusicMetadata) -> bool:
        """更新FLAC元数据"""
        audio = FLAC(self.path) if self.path.exists() else FLAC()
        
        audio['title'] = metadata.title
        audio['artist'] = metadata.artist
        audio['album'] = metadata.album
        audio['date'] = metadata.date

        audio.save()
        return True

    
    def _update_wav_metadata(self, _: MusicMetadata) -> bool:
        """更新WAV元数据"""
        # WAV格式元数据支持有限，这里简单实现
        return True

class MusicProcessor:
    """音乐文件处理器"""
    
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.music_files: List[MusicFile] = []
        
    def scan_files(self) -> List[MusicFile]:
        """扫描音乐文件"""
        if not self.directory.exists():
            raise FileNotFoundError(f"目录不存在: {self.directory}")
            
        music_files = []
        for file_path in self.directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in MusicFile.SUPPORTED_EXTENSIONS:
                music_file = MusicFile(str(file_path))
                music_file.metadata = music_file.extract_metadata()
                music_files.append(music_file)
                
        self.music_files = sorted(music_files, key=lambda x: x.path.name)
        return self.music_files
    
    def generate_filename(self, mf: MusicFile) -> str:
        """生成标准化文件名"""        
        metadata = mf.metadata
        return f"{metadata.artist} - {metadata.title}{mf.extension}"
    
    def set_meta(self, mf: MusicFile, infer_result: dict):
        if not mf.metadata.title:
            mf.metadata.title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', infer_result.get('title', ''))
        if not mf.metadata.artist:
            mf.metadata.artist = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', infer_result.get('artist', ''))
        if not mf.metadata.album:
            mf.metadata.album = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', infer_result.get('album', ''))
        if not mf.metadata.date:
            mf.metadata.date = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', infer_result.get('data', ''))

    def process_files(self) -> Dict[str, int]:
        """处理所有音乐文件"""
        if not self.music_files:
            self.scan_files()
            
        results = {
            "total": len(self.music_files),
            "processed": 0,
            "updated": 0,
            "renamed": 0,
            "failed": 0,
            "wav": 0,
        }
        
        # 使用进度条
        with tqdm(total=len(self.music_files), desc="处理音乐文件", unit="file") as pbar:
            for music_file in self.music_files:
                # if music_file.metadata.is_complete() or music_file.extension == '.wav':
                #     results['processed'] += 1
                #     continue
                if music_file.extension == '.wav':
                    results['wav'] += 1
                    continue
                try:
                    if music_file.err == '':
                        try:
                            infer_result = music_infer(str(music_file.path))
                            print(f"{music_file.path}, {infer_result}")
                            self.set_meta(music_file, infer_result)
                        except Exception as e:
                            results["failed"] += 1
                            music_file.err = f"{music_file.err}| music_infer_err: {e}"
                            continue

                    if music_file.update_metadata(music_file.metadata):
                        results["updated"] += 1
                    else:
                        results["failed"] += 1

                    new_filename = self.generate_filename(music_file)
                    new_path = music_file.path.parent / new_filename
                    
                    if new_path != music_file.path and not new_path.exists():
                        music_file.path.rename(new_path)
                        results["renamed"] += 1
                    results["processed"] += 1

                except Exception as e:
                    logger.error(f"处理文件失败 {music_file.path}: {e}")
                    results["failed"] += 1
                finally:
                    pbar.update(1)
                    pbar.set_postfix({
                        '更新': results["updated"],
                        '重命名': results["renamed"],
                        '失败': results["failed"] + results['wav']
                    })
        print(results)
        return results

def write_to_music_txt(metadata_list: List[Dict[str, str]], output_file: str = "music.txt"):
    """将元数据写入music.txt"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in metadata_list:
                f.write(f"{item['artist']} - {item['title']} - {item['album']} - {item['date']} -{item['err']}\n")
        logger.info(f"元数据已写入 {output_file}")
    except Exception as e:
        logger.error(f"写入music.txt失败: {e}")
