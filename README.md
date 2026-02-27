# paddleocr_for_PC

## 目的

端侧实现OCR识别，满足关于所要求定制信息的识别。

## 结构

```
├─main.py	   //实现OCR功能的模块
├─README.md  
├─sync_module.py   //文件同步模块(样板)
├─test1.jpg        //测试图片
├─tools		   //辅助工具(可选)
|   ├─adb	   
├─SyncedPhotos     //通过辅助工具从移动端拉取的图片   
|      ├─铭牌
|      	    ├─柜号
├─output_matched.jpg //测试OCR功能的结果图
```

## OCR环境配置

有多种安装方式，这里我选择pip安装：

安装paddlepaddle：

```
# CPU 版本
python -m pip install paddlepaddle==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/

# GPU 版本，需显卡驱动程序版本 ≥450.80.02（Linux）或 ≥452.39（Windows）
python -m pip install paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu118/

# GPU 版本，需显卡驱动程序版本 ≥550.54.14（Linux）或 ≥550.54.14（Windows）
 python -m pip install paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
```

安装paddleOCR推理包：

```
# 只希望使用基础文字识别功能（返回文字位置坐标和文本内容）
python -m pip install paddleocr
# 希望使用文档解析、文档理解、文档翻译、关键信息抽取等全部功能
# python -m pip install "paddleocr[all]"
```

对于安装过程有疑问可以参考[官方安装教程](https://www.paddleocr.ai/main/version3.x/installation.html)

## OCR功能

代码详见main.py。

主要就是调用paddleOCR库，使用OCRv5的检测和识别模型(本地，满足离线要求)，对于图片进行检测后对结果进行模式识别，提取出对应的定制信息。

因为PC端对于定制信息的识别要求较高，并且经过我的测试发现即使是OCRv5这类最先进的模型面对我们的需求也存在精度不足的情况(例如字母I识别为工)，可能需要进行模型微调训练。

对于paddleOCR处理结果result的表现形式，以及更多的用法包括模型微调训练方法详见[官方教程](https://www.paddleocr.ai/main/version3.x/module_usage/text_recognition.html#_4)。

## 同步模块

通过adb调试工具实现，要求通过USB连接移动设备，同时移动设备打开开发者模式。
