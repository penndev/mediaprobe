# Flv分析工具

> 使用python + PySide6 开发的适用三端 windows mac linux 的 flv媒体桌面文件分析工具

## mac 下编译为 flv-analyze.app

```shell
python3 -m venv env

source env/bin/activate

pip install -i https://mirrors.aliyun.com/pypi/simple/ requirements.txt

# pyinstaller --clean --windowed -i icon.png -n Flv-Analyze  -F main.py

pyinstaller --windowed  -i icon.ico -n Flv-Analyze  main.py
```

pyinstaller --name="Flv-Analyze" --icon icon.ico --windowed --onefile main.py