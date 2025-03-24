
import os
import inspect

def debug_print(message):
    """打印包含文件名和行号的调试信息"""
    frame = inspect.currentframe().f_back
    filename = os.path.basename(frame.f_code.co_filename)
    lineno = frame.f_lineno
    print(f">>>debug_print:{filename}:{lineno} - </ message > \n {message} \n < message/>")
