import os

# 导入streamlit库
import streamlit as st

# 导入smolagents库
from src.smolagents.agents import CodeAgent
from src.smolagents.tools import tool
#rom src.smolagents.models import LiteLLMModel
from src.utils.openaimodel import OpenAIModel
from src.smolagents.prompts import CODE_SYSTEM_PROMPT
import src.smolagents.global_vars as global_vars


model= OpenAIModel(
    model_id=os.environ.get('MODEL_ID'),
    api_key=os.environ.get('API_KEY'),
    base_url=os.environ.get('BASE_URL'),
)

system_prompt = (
            "Your name is CodeGenie.\n"
            "All file operations must be performed under the 'tmp' directory. If no specific path is provided, the default path is 'tmp'.\n"
            "When users request to read or save files without providing a specific path, the default directory is 'tmp'.\n"
            "Example paths: 'tmp/output.csv' or 'tmp/chart.png'.\n" + CODE_SYSTEM_PROMPT +"\n注意：用中文回答。"
        )

imports = ['seaborn','matplotlib','queue', 'time', 'math', 'datetime', 'unicodedata', 'stat', 'random', 're', 'os','pandas', 'numpy', 'itertools', 'statistics', 'collections']

@tool
def tavily_search(query: str) -> str:

    """
    一个搜索引擎工具，当你需要互联网信息检索服务时候使用。

    Args:
        query: 要搜索的问题描述或关键词。

    Returns:
        response: 返回的结果，通常是一段短文。
    """

    from tavily import TavilyClient

    tavily_client = TavilyClient(api_key=os.environ.get('TAVILY_KEY'))
    
    # 执行搜索
    response = tavily_client.qna_search(query) 
    
    return response


def clear_chat_history():
    st.session_state.messages = []

def init_chat_history():
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("""您好，我叫CodeGenie，是个编程计算助手，请让我用编程解决您的数学问题💖 """+
        """<br>***您可以这样提问***：<br>1. 请简短对SouthGermanCredit.csv文件的数据内容进行描述。"""+
        """<br>2. 我计划使用SouthGermanCredit.csv这份数据集进行模型训练。为了更好地理解数据，我需要对其中包含的各项特征进行统计分析。这包括计算每个特征的基本统计量，如均值、中位数、最大最小值等，并探索特征之间的相关性，以及识别可能的数据分布模式。这样做能够帮助确保数据的质量和适用性，为构建准确有效的模型奠定基础。""",
         unsafe_allow_html=True)

    if "messages" in st.session_state:
        for message in st.session_state.messages:
            avatar = "🙋‍♂️" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])
    else:
        st.session_state.messages = []

    return st.session_state.messages

def init_chat_agent():

    if "agent" in st.session_state:
    	pass
    else:
    	st.session_state.agent = CodeAgent(tools=[], model=model, system_prompt=system_prompt, additional_authorized_imports=imports)

    return st.session_state.agent


def update_variable_filter():
    """更新并显示变量选择"""
    common_types = (int, float, str, list, dict, bool)  # 定义常见类型
    # 过滤出常用类型的变量
    filtered_state = {k: v for k, v in global_vars.gl_state.items() if isinstance(v, common_types) and k != 'print_outputs'}

    # 在侧边栏中显示变量列表
    st.sidebar.markdown('---')
    st.sidebar.subheader("当前变量")
    for var_name, var_value in filtered_state.items():
        st.sidebar.write(f"{var_name}: {var_value}")

def save_uploaded_file( work_dir):
    """保存上传的文件到指定目录"""
		# 文件上传组件
    uploaded_file = st.sidebar.file_uploader("上传文件", type=["csv", "txt", "xlsx"])

    if uploaded_file is not None:
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)

        file_path = os.path.join(work_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 显示上传文件的信息
        st.write(f"已上传文件：{uploaded_file.name}, 文件大小： {uploaded_file.size} 字节")


def display_file_list(directory='.'):
    """在侧边栏中显示文件列表"""
    save_uploaded_file( work_dir=directory)
    st.sidebar.markdown('---')
    st.sidebar.subheader("文件列表")
    try:
        files = os.listdir(directory)
        files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
    except Exception as e:
        st.error(f"无法读取目录 {directory}: {e}")
        files= []

    if files:
        for file in files:
                    file_path = os.path.join(directory, file)
                    with open(file_path, "rb") as f:
                        bytes_data = f.read()

                    st.sidebar.download_button(
                        label=f"{file}",
                        data=bytes_data,
                        file_name=file,
                        mime=None
                    )

    else:
        st.sidebar.write("没有找到任何文件。")


# Define a callback to run when the user submits a message
def chat():
    
    messages = init_chat_history()
    agent=init_chat_agent()
		
    prompt = st.chat_input("Shift + Enter 换行，Enter 发送")
    if prompt:
        with st.chat_message("user", avatar="🙋‍♂️"):
            st.markdown(prompt)
            messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            response = agent.run(prompt, reset=False)
            placeholder.markdown(response, unsafe_allow_html=True)  # 显示回复

        messages.append({"role": "assistant", "content": response})
        st.button("清空对话", on_click=clear_chat_history)

if __name__ == "__main__":

    st.title("CodeGenie")

		# 启动聊天功能
    chat()

    # 在侧边栏中显示文件列表
    display_file_list(directory='tmp')

    # 更新并显示变量列表
    update_variable_filter()
