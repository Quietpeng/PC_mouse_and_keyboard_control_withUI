# 自定义电脑自动操作项目

## 项目简介

该项目旨在通过图像识别和自动化（鼠标、键盘）操作，实现自定义电脑自动操作的功能。项目主要分为三个部分：校正类、指令编辑类和操作执行类。

## 文件结构

```
│  README.md
│  requirements.txt
│  start_exe.bat
│  start_python.bat
│
├─exe
│  │  Coomputer_control.exe
│  │  offset_params.txt
│  │  rule.json
│
└─src
    │  Coomputer_control.py
    │  offset_params.txt
    │  rule.json

```

## 依赖安装

在运行该项目之前，请确保已安装以下依赖库：

```bash
pip install -r requirements
```

## 使用说明

### 1. 校正类

校正类用于校正鼠标坐标偏差，并提供鼠标点击测试和键盘输入测试功能。

### 2. 指令编辑类

指令编辑类用于读取和编辑操作流程配置。用户可以通过图形界面添加、编辑和删除命令。

### 3. 操作执行类

操作执行类根据操作流程配置执行相应的操作。

## 运行步骤（图形界面python）

1. 转到src文件夹运行 `Coomputer_control.py` 文件：

```bash
python Coomputer_control.py
```

或者直接运行start_python.bat

2. 在弹出的图形界面中，选择命令类型并输入相应的参数，点击“添加命令”按钮添加命令。
3. 添加完成后，点击“确认并运行”按钮，程序将按照配置的命令顺序执行操作。

## 运行步骤（图形界面exe）

1. 转到exe文件夹运行 `Coomputer_control.exe 文件：

```bash
Coomputer_control.exe
```

或者直接运行start_exe.bat

2. 在弹出的图形界面中，选择命令类型并输入相应的参数，点击“添加命令”按钮添加命令。

3. 添加完成后，点击“确认并运行”按钮，程序将按照配置的命令顺序执行操作。

## 示例（修改调用）

以下是一个简单的示例，展示如何使用该项目：

```python
if __name__ == "__main__":
    try:
        calibration = Calibration()
        # 开始校正
        calibration.calibrate()
        calibration.test_click()
        calibration.test_keyboard_input("测试文本")
        print("校正完成")

        command_editor = CommandEditor()
        command_editor.show_ui()
        print("添加命令...")

        executor = OperationExecutor(calibration, command_editor)
        print("执行命令...")
        executor.execute_commands()
        print("命令执行完成")
    except Exception as e:
        print(f"发生错误: {e}")
```

## 注意事项

- 在使用鼠标移动命令时，可以选择输入坐标或图片路径。如果输入图片路径，程序将根据图片识别坐标。
- 在使用键盘快捷键命令时，请确保输入的按键组合正确。

## 贡献

欢迎提交问题和贡献代码。如果有任何建议或改进，请提交 Pull Request 或 Issue。

## 许可证

该项目采用 Apache2.0 许可证，详情请参阅 LICENSE 文件。
