# 文件操作样例

### os包常见函数

函数 | 描述
--- | ---
`os.getcwd()`  |  获取当前路径
`os.path.join(...)`  |  文件/目录路径连接(避免不同系统的连接符)
`os.makedirs( ... )`  |  创建文件夹
`os.path.exists(dir_name)`  |  判断文件夹是否存在
`os.path.isfile(full_name)`  |  判断文件是否存在


### pyinstall

```
pyinstaller [-F/-D] [-w/-c] [-i xxx.ico] xxx.py/xxx.spec

xxx.py/xxx.spec：需要打包的程序main文件或者spec文件。spec文件在使用py文件进行打包时会在相同路径下自动生成，spec中的内容也是根据命令行中输入的内容来生成的，也可以使用命令pyi-makespec [options] xxx.py来生成一个纯粹的spec文件，而不会去执行打包的操作。
-F/--onefile：将整个程序打包为一个exe文件，需要注意的是，与-D模式生成的exe程序相比，在启动速度上会慢一点，原因是它需要先解压exe文件并生成一个唯一的临时环境来运行程序，关闭环境时也会自动删除这个临时环境，-D模式的程序本身就是解压好的，运行完也不需要执行删除操作，当程序比较大时，这个差别就很明显了。
-D/--onedir：默认选项，与F/--onefile参数作用相反，将程序打包为一个文件夹，文件夹中包含启动程序的exe文件和其他依赖的资源文件和DLL文件等。
-w：表示程序运行后隐藏命令行窗口，当你不需要使用命令行窗口作为程序的I/O时，比如GUI程序，可以使用这个参数选项。
-c：默认选项，与-w相反，提供一个命令行窗口进行I/O。
-i/--icon：指定exe程序图标(注意: icon必须使用 .icon的文件,否则会有attributeerror-module-win32ctypes-pywin32-win32api-has-no-attribute-error的错误)
```

示例:
`pyinstaller -F -i ./assert/upload.ico -n upfile app.py`

调试:
可以在主函数结束前调用`time.sleep(20)`来帮助命令行的停留

读取文件路径:
1. 采用`-F`打包后的exe在执行时首先是解压,然后临时运行目录环境下执行程序,完成了删除临时文件
2. 可以通过`getattr`获取当前环境是打包前还是打包后--(PyInstaller文档)[https://pythonhosted.org/PyInstaller/runtime-information.html#run-time-information]
3. 可以通过`os.path.dirname(os.path.realpath(sys.argv[0]))`获取当前exe所在文件夹路径
