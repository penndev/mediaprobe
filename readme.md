# Flv分析工具

> 使用python + PySide6 开发的适用三端 windows mac linux 的 flv媒体桌面文件分析工具

## 下载地址

如果没有python环境 [点击下载](https://github.com/penndev/flv-analyze/releases) 直接运行

## 编译为 flv-analyze 应用程式

```shell
python3 -m venv env

source env/bin/activate

pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

pyinstaller --name="Flv-Analyze" --icon icon.ico --windowed --onefile main.py
```
