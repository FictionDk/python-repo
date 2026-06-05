# music-mut

## 功能概述
音乐文件元数据批量处理工具，支持mp3、flac、wav格式文件的元数据读取、补全、更新和重命名。

## 功能特性
1. 扫描指定目录下的mp3、flac、wav文件
2. 提取音乐文件元数据（标题、艺术家、专辑、日期）
3. 检查元数据完整性，缺失时调用大模型补全
4. 按`艺术家 - 标题 - 日期.xxx`格式重命名文件
5. 将元数据写入music.txt文件
6. 支持进度显示和日志记录

## 使用方法
```bash
python main.py /path/to/music/directory [--batch-size N] [--model-endpoint URL]
```

### 参数说明
- `directory`: 音乐文件目录路径 (必需)
- `--batch-size`: 批处理大小，默认10
- `--model-endpoint`: 大模型API端点，用于补全缺失元数据

## 输入输出格式

### 输入参数
- `directory`: 音乐文件目录路径 (str, required)
- `batch_size`: 批处理大小 (int, optional, default=10)
- `model_endpoint`: 大模型API端点 (str, optional)

### 输出格式
处理结果统计信息:
```json
{
  "total": 100,
  "processed": 95,
  "updated": 45,
  "renamed": 40,
  "failed": 5
}
```

## 方法定义

### MusicMetadata
音乐元数据模型
```python
class MusicMetadata:
    def __init__(self, title: str = "", artist: str = "", album: str = "", date: str = "")
    def is_complete(self) -> bool:  # 检查元数据是否完整
    def to_dict(self) -> Dict[str, str]:  # 转换为字典
```

### MusicFile
音乐文件处理器
```python
class MusicFile:
    def __init__(self, file_path: str)
    def extract_metadata(self) -> MusicMetadata:  # 提取元数据
    def update_metadata(self, metadata: MusicMetadata) -> bool:  # 更新元数据
```

### MusicProcessor
音乐文件批量处理器
```python
class MusicProcessor:
    def __init__(self, directory: str)
    def scan_files(self) -> List[MusicFile]:  # 扫描音乐文件
    def generate_filename(self, metadata: MusicMetadata) -> str:  # 生成标准化文件名
    def process_files(self) -> Dict[str, int]:  # 处理所有文件
```

### 工具函数
```python
def write_to_music_txt(metadata_list: List[Dict[str, str]], output_file: str = "music.txt"):  # 写入music.txt
```
