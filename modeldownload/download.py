import subprocess
import sys
import argparse

def execute_command(command):
    """
    执行传入的命令行命令
    """
    try:
        print(f"正在执行命令: {command}")
        result = subprocess.run(command, shell=True, check=True, text=True, 
                              capture_output=True, encoding='utf-8')
        print("命令执行成功!")
        if result.stdout:
            print("输出:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败，返回码: {e.returncode}")
        if e.stdout:
            print("输出:")
            print(e.stdout)
        if e.stderr:
            print("错误信息:")
            print(e.stderr)
        return False
    except Exception as e:
        print(f"执行过程中发生异常: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='命令行命令执行工具')
    parser.add_argument('--command', '-c', type=str, required=True,
                       help='要执行的命令行命令,支持modelscop和huggingface')
    
    args = parser.parse_args()
    
    if not args.command.strip():
        print("错误: 命令不能为空")
        sys.exit(1)
    
    success = execute_command(args.command)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
