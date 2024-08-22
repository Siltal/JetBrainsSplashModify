# JetBrainsSplashModify

## 简介
> [!NOTE]
> Windows only.

`JetBrainsSplashModify` 是一个用于修改 JetBrains IDE 启动画面（Splash Screen）和其他相关资源的 Python 工具。通过这个工具，用户可以轻松替换 JetBrains 软件中的默认图片。

## 使用方法

1. **准备工作**:
   - 将你希望替换的图片文件放置在项目根目录下。

2. **运行脚本**:
   - 确保所有配置都已正确设置后，运行 `main.py`或 [Release](https://github.com/Siltal/JetBrainsSplashModify/releases) 中的exe。
   - 选择要修改的软件类别，选择软件，选择操作，提供图片路径
   - 如果无法获取到安装地址，请手动提供安装地址。

## 注意事项

- 确保提供的图片尺寸与目标替换图片的宽高比相匹配，以避免显示异常。
  - 若宽高比不相同则裁切中心的部分。
- 替换操作可能需要管理员权限，确保你在具有足够权限的环境中运行此脚本。
- 无法获取通常是由于通过Toolbox安装导致的。
