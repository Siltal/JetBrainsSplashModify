# JetBrainsSplashModify

## 简介
> [!TIP]
> Windows only.
`JetBrainsSplashModify` 是一个用于修改 JetBrains IDE 启动画面（Splash Screen）和其他相关资源的 Python 工具。通过这个工具，用户可以轻松替换 JetBrains 软件中的默认图片。

## 使用方法

1. **准备工作**:
   - 将你希望替换的图片文件放置在项目根目录下的 `res` 文件夹中。如果 `res` 文件夹不存在，请自行创建。

2. **修改 Windows 用户名**:
   - 在`config.json`中，将 `win_user` 参数替换为你当前使用的 Windows 用户名。这通常是你的 `C:\Users\` 目录下的文件夹名称。

3. **修改图片路径**:
   - 打开 `main.py` 文件，在代码中的最后一行将图片的相对路径填写为 `res` 目录下的文件路径。例如：
     ```python
     main("res/your_image.png")
     ```

4. **运行脚本**:
   - 确保所有配置都已正确设置后，运行 `main.py`。脚本将通过选项引导您操作。

## 注意事项

- 确保提供的图片尺寸与目标替换图片的宽高比相匹配，以避免显示异常。
  - 若宽高比不相同则裁切中心的部分。
- 替换操作可能需要管理员权限，确保你在具有足够权限的环境中运行此脚本。
