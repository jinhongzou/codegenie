
def find_imgpath(context):

    import re
    # 示例字符串
    #context = """{"img_path":"image.png"}"""
    
    # 提取图片路径
    match = re.search(r'{"img_path":\s*"(.*?)"}', context)
    if match:
        path =match.group(1)
        print(f"找到图片信息:{path}")
        return path
    return None


if 1:
    find_imgpath("""{"img_path":"mascot_smol.png"}""")
