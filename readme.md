# VFA

> Video Format Analysis. 视频格式分析


- [Mpeg2-TS 数据结构](./ts.py)

x 解决sdt pat pmt package问题

- [Flv 数据结构](./flv.py)



## 拆分视频

```bash
ffmpeg -i .\i.mp4 out.h264

ffmpeg -i .\i.mp4 out.aac

ffmpeg -i out.h264 -i out.aac -c:v copy -c:a copy output.mp4
```

## 帧的类型
- I帧：I帧指的是一副完整的画面，他不需要参考任何帧就可以解码出来。
- P帧：P帧指的是前向参考帧，它需要参考前一帧的图片才能够正确把数据解码出来。
- B帧：B帧指的是双向参考帧，它需要参考前一帧数据和后一帧数据才能够正常把数据解码出来。

- SP帧 （Switching P Pic⁃ture）
- SI帧 （Switching I Picture） 


- **H.26X官方文档**

- https://www.itu.int/itu-t/recommendations/rec.aspx?rec=H.264
- https://www.itu.int/itu-t/recommendations/rec.aspx?rec=H.265