import json
import os
import re
import shutil
import winreg
import zipfile
from io import BytesIO
from typing import Tuple

from PIL import Image
from select import select



def get_register_value(key: int, sub_key: str, name: str) -> [str | None]:
    try:
        registry_key = winreg.OpenKey(
            key,
            sub_key,
            0,
            winreg.KEY_READ
        )
        install_path, _ = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return install_path
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error accessing registry: {e}")
        return None


def user_select(options: list, hint="hint") -> str:
    hint_select_items='\n'.join(f"{k} -- {v}" for k, v in enumerate(options))
    while True:
        user_input = input(f"{hint}\n{hint_select_items}\n> ").strip()
        if user_input.isdigit():
            user_input_int = int(user_input)
            if 0 <= user_input_int < len(options):
                return options[int(user_input)]
            else:
                print("Select item out of option. Please enter again.")  # 输入无效时提示用户重新输入
        else:
            print("Invalid input. Please enter a number.")  # 输入无效时提示用户重新输入


def get_installation(program_name) -> str:
    if program_name == "Android Studio":
        installation = get_register_value(winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\{program_name}", "Path")
        return installation.replace('\\', '/') + '/'
    installation = get_register_value(winreg.HKEY_CURRENT_USER, "Environment", program_name)
    try:
        installation = installation.removesuffix('bin;').replace('\\', '/')
        return installation
    except:
        print("Can't locate installation by registry, ENTER installation manually :")
        input_installation = input().replace('\\', '/')
        if input_installation.endswith('/'):
            return input_installation
        else:
            return f'{input_installation}/'


def get_fit_image(img_path: str, size: Tuple[int, int]) -> Image.Image:
    """
    根据指定的尺寸裁剪图像并调整大小，返回图像对象
    :param img_path: 图像文件路径
    :param size: (宽, 高) 元组
    :return: 调整后的 PIL 图像对象
    """
    img = Image.open(img_path)
    original_width, original_height = img.size
    target_width, target_height = size

    # 计算目标宽高比
    target_ratio = target_width / target_height
    original_ratio = original_width / original_height

    if original_ratio > target_ratio:
        # 原始图像更宽，需要裁剪宽度
        new_width = int(original_height * target_ratio)
        offset = (original_width - new_width) // 2
        img = img.crop((offset, 0, offset + new_width, original_height))
    else:
        # 原始图像更高，需要裁剪高度
        new_height = int(original_width / target_ratio)
        offset = (original_height - new_height) // 2
        img = img.crop((0, offset, original_width, offset + new_height))

    # 调整图像大小到目标尺寸
    img = img.resize(size, Image.Resampling.LANCZOS)

    return img


def create_dir_if_not_exist(path):
    res_dir = os.path.join(os.getcwd(), path)
    if not os.path.exists(res_dir):
        os.makedirs(res_dir)
        print(f"Created directory: {res_dir}")


def extract_image(root_path: str, **config):
    """
    从 JAR 文件中提取指定图片并保存到当前文件夹
    :param root_path: JAR 文件的根路径
    :param config: 配置字典，包含 'source' 和 'items'（要提取的图片文件路径）等信息
    :return: None
    """
    jar_file = root_path + config.get('source')

    # 检查 JAR 文件是否存在
    if not os.path.exists(jar_file):
        raise FileNotFoundError(f"JAR file not found at {jar_file}")

    output_dir = "extracted"
    create_dir_if_not_exist(output_dir)

    # 要提取的目标图片路径列表
    items = config.get('items', [])

    # 解压并提取图片
    with zipfile.ZipFile(jar_file, 'r') as jar:
        for item in items:
            if item in jar.namelist():
                # 提取文件并保存到 output_dir 中，去除路径，只保留文件名
                file_data = jar.read(item)
                file_name = os.path.basename(item)  # 获取文件名部分
                output_path = '/'.join([output_dir, file_name])

                with open(output_path, 'wb') as output_file:
                    output_file.write(file_data)

                print(f"Extracted {file_name} to {output_dir}")
            else:
                print(f"{item} not found in the JAR file")


def patch(root_path: str, img_path: str, **config):
    """
    修改指定 JAR 文件中的图像资源
    :param root_path: 根路径，包含 JAR 文件的位置
    :param img_path: 替换图像的路径
    :param config: 配置字典，包含 'source', 'items', 'cache' 等信息
    :return: None
    """
    jar_file = root_path + config.get('source')
    backup_file = jar_file + '.custom.backup'

    # 检查是否已经有备份文件存在
    if not os.path.exists(backup_file):
        shutil.copy2(jar_file, backup_file)
        print(f"Backup created at {backup_file}")
    else:
        print(f"Backup file already exists at {backup_file}. Skipping backup.")

    # 读取并解压 JAR 文件内容
    with zipfile.ZipFile(jar_file, 'r') as jar:
        jar_contents = {name: jar.read(name) for name in jar.namelist()}

    items = config.get('items', [])

    for item in items:
        with zipfile.ZipFile(jar_file, 'r') as jar:
            with jar.open(item) as img_file:
                img = Image.open(img_file)
                print(f'Image {item} size: {img.size}')

        # 根据获取的尺寸生成新图像
        new_img = get_fit_image(img_path, img.size)

        # 将新图像保存到字节流
        img_byte_arr = BytesIO()
        new_img.save(img_byte_arr, format=img.format)
        img_byte_arr = img_byte_arr.getvalue()

        # 更新字典内容，保持原始的路径
        jar_contents[item] = img_byte_arr

    # 将更新后的内容写回到 JAR 文件中
    with zipfile.ZipFile(jar_file, 'w') as jar:
        for file_name, data in jar_contents.items():
            jar.writestr(file_name, data)

    print(f"Modified JAR file saved at {jar_file}")


def restore(root_path: str, **config):
    """
    恢复 JAR 文件备份
    :param root_path: 根路径，包含 JAR 文件的位置
    :return: None
    """
    source_path = config.get('source')
    jar_dir = os.path.dirname(source_path)  # 获取目录部分，例如 'lib/'
    full_dir_path = root_path + jar_dir

    jar_files = [f for f in os.listdir(full_dir_path) if f.endswith('.custom.backup')]

    if not jar_files:
        print("No backup found. Nothing to restore.")
        return

    for backup_file in jar_files:
        original_file = backup_file.replace('.custom.backup', '')
        backup_path = '/'.join([full_dir_path, backup_file])
        original_path = '/'.join([full_dir_path, original_file])

        # 移动备份文件覆盖原文件
        shutil.move(backup_path, original_path)
        print(f"Restored {original_file} from backup.")


import os
import re


def clean_cache_image(win_username, **config):
    cache = config.get('cache', [])
    path, fuzz_match_max, sub_path = cache
    path = path % win_username

    # 列出 path 中的所有文件夹
    all_dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

    # 使用正则表达式匹配以 fuzz_match_max 为前缀的文件夹
    pattern = re.compile(rf"^{re.escape(fuzz_match_max)}")

    matching_dirs = [d for d in all_dirs if pattern.match(d)]

    if not matching_dirs:
        raise FileNotFoundError(f"No matching directory found for prefix {fuzz_match_max} in {path}")

    for match_dir in matching_dirs:
        # 构建完整路径
        final_path = os.path.join(path, match_dir, sub_path)

        try:
            # 列出 final_path 中的所有文件
            all_files = os.listdir(final_path)

            # 删除所有文件
            for file in all_files:
                os.remove(os.path.join(final_path, file))

            # 删除文件夹
            os.rmdir(final_path)
            print(f"Deleted directory and files: {final_path}")

        except FileNotFoundError:
            print(f"No such path: {final_path}")
            continue


def main():
    with open("config.json", "r") as f:
        json_data = f.read()
    data_dict: dict = json.loads(json_data)

    win_user = os.getlogin()

    category = user_select(list(data_dict.keys()), "Please select category:")
    program_name = user_select(list(data_dict[category]), "Please select product:")
    operate = user_select(['extract image', 'patch', 'restore'], "Please select operate:")

    installation = get_installation(program_name)
    config = data_dict[category][program_name]

    match operate:
        case 'extract image':
            extract_image(installation, **config)
        case 'patch':
            ima_path = f"{input("image path: ")}"
            patch(installation, ima_path, **config)
            clean_cache_image(win_user, **config)
        case 'restore':
            restore(installation, **config)
            clean_cache_image(win_user, **config)


if __name__ == '__main__':
    main()
