import os
import numpy as np
import pandas as pd

# 导入streamlit库
import streamlit as st

# 导入smolagents库
from src.smolagents  import CodeAgent,tool,LiteLLMModel
from src.tools_utils  import list_files,read_file,write_file,delete_file
from src.tools_utils  import SearchAgent

#os.environ['API_KEY'] = 'sk-XXX'
##os.environ['BASE_URL'] = 'https://api.siliconflow.cn/v1/'
##os.environ['MODEL_ID'] = 'openai/Qwen/Qwen2.5-7B-Instruct'
##os.environ['MODEL_CODE_ID'] = 'openai/Qwen/Qwen2.5-Coder-7B-Instruct'

#-----------------------------------------
st.session_state.ai="🤖"
st.session_state.user="🙋"

model= LiteLLMModel(
    model_id=os.environ.get('MODEL_ID'),
    api_key=os.environ.get('API_KEY'),
    base_url=os.environ.get('BASE_URL'),
)
code_model= LiteLLMModel(
    model_id=os.environ.get('MODEL_CODE_ID'),
    api_key=os.environ.get('API_KEY'),
    base_url=os.environ.get('BASE_URL'),
)


imports = ['seaborn','matplotlib','queue', 'time', 'math', 'datetime', 'unicodedata', 'stat', 'random', 're', 'os','pandas', 'numpy', 'itertools', 'statistics', 'collections']

search_agent=SearchAgent(model_id = os.environ.get('MODEL_ID'), 
                         api_key  = os.environ.get('API_KEY'),
                         base_url = os.environ.get('BASE_URL'),
                         tavily_api_key=os.environ.get('TAVILY_KEY'),
                         )

agent_tools = [list_files, read_file, write_file, delete_file, search_agent]

# 构造一个示例 JSON 变量
agent_tools_desc = {
    "list_files": "列出指定目录中的所有文件",
    "read_file": "读取指定文件的内容",
    "write_file": "将内容写入指定文件",
    "delete_file": "删除指定的文件",
    "general_search": "执行通用搜索操作"
}

def clear_chat_history():
    st.session_state.messages = []

def init_chat_history():

    with st.chat_message("assistant", avatar=st.session_state.ai):
        st.markdown("""您好，我叫CodeGenie，是个编程计算助手，请让我用编程解决您问题"""+
        """<br>***您可以这样提问***：<br>1. 读取 `tmp` 目录下的`SouthGermanCredit.csv`文件，保存到数据集变量`src_data`，并返回`成功`或`失败`。"""+
        """<br>2. 我计划使用`src_data`数据集进行模型训练。为此，我需要对数据进行统计分析，包括计算每个特征的均值、中位数、最大值、最小值等基本统计量，探索特征间的相关性，并识别数据分布模式，以确保数据质量和适用性，为模型构建奠定基础。""" +
        """<br>3. 删除变量：选择“代码执行”模式， 执行命令：```del src_data ``` 。""",

         unsafe_allow_html=True)

        #st.line_chart(pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"]))

    if "messages" in st.session_state:
        for message in st.session_state.messages:
            avatar = st.session_state.user if message["role"] == "user" else st.session_state.ai
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    else:
        st.session_state.messages = []

    return st.session_state.messages

def init_chat_agent():

    if "agent" in st.session_state:
        pass
    else:
        # 初始化一个CodeAgent对象

        #st.session_state.agent = CodeAgent(
        #    tools=agent_tools,
        #    model=model,
        #    additional_authorized_imports=imports
        #        )

        #search_agent = ToolCallingAgent(
        #    tools=[general_ssearch_agentearch],
        #    model=model,
        #    max_steps=5,
        #    name="search_agent",
        #    description="Runs searches for you. Example usage: search_agent(task=your_query)",
        #)

        st.session_state.agent = CodeAgent(
            tools=agent_tools,
            model=model,
            managed_agents=[],
            additional_authorized_imports=imports,
            max_steps=5,
            verbosity_level=1,
            name="manager_agent",
            description="This is a manager agent responsible for handling various tasks.",
        )

        # 设置系统提示模板，定义代理的行为和约束
        st.session_state.agent.prompt_templates["system_prompt"] = """
        Your name is CodeGenie.
        All file operations must be performed under the 'tmp' directory. If no specific path is provided, the default path is 'tmp'.
        When users request to read or save files without providing a specific path, the default directory is 'tmp'.
        Example paths: 'tmp/output.csv' or 'tmp/chart.png'.\nNote: When reading the file, only return success or failure, and avoid printing the file content directly.\n""" + st.session_state.agent.prompt_templates["system_prompt"] + "\n注意：用中文回答。"
        #print(st.session_state.agent.prompt_templates["system_prompt"])

    return st.session_state.agent

def display_value_list(agent):
    """更新并显示变量选择"""

    filtered_state = agent.python_executor.get_local_executor_state()

    # 在侧边栏中显示变量列表
    st.sidebar.markdown('---')
    st.sidebar.subheader("可用变量")
    #for var_name, var_value in filtered_state.items():
    #    st.sidebar.write(f"{var_name}: {var_value}")
    for var_name, var_value in filtered_state.items():
        # 控制 var_value 的长度，例如限制为最多显示 20 个字符
        max_length = 20
        truncated_value = str(var_value)[:max_length] + ("..." if len(str(var_value)) > max_length else "")
        st.sidebar.write(f"{var_name}: {truncated_value}")

def save_uploaded_file( work_dir):
    """保存上传的文件到指定目录"""
		# 文件上传组件
    uploaded_file = st.sidebar.file_uploader("", type=None)

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

    st.sidebar.subheader("tmp目录")
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
                        label=f" {file} ",
                        data=bytes_data,
                        file_name=file,
                        mime=None
                    )

    else:
        st.sidebar.write("没有找到任何文件。")

def display_tools_list(tools):
    """在侧边栏中显示工具列表"""
    st.sidebar.markdown('---')
    st.sidebar.subheader("可用工具")
    if tools:
        for tool_name, tool_desc in tools.items():
            st.sidebar.write(f"**{tool_name}**: {tool_desc}")

    else:
        st.sidebar.write("暂无工具可用")

# Define a callback to run when the user submits a message
def chat():
    #对话消息初始化
    messages = init_chat_history()

    #创建agent实例
    agent=init_chat_agent()

    if "mode" in st.session_state:
        pass
    else:
        # 初始化一个CodeAgent对象
       st.session_state.mode = '聊天'

    prompt = st.chat_input("Shift + Enter 换行，Enter 发送")
    if prompt:

        if st.session_state.mode == "聊天":
            with st.chat_message("user", avatar=st.session_state.user):
                st.markdown(prompt)

            with st.chat_message("assistant", avatar=st.session_state.ai):
                placeholder = st.empty()
                response = agent.run(prompt, reset=False)
                placeholder.markdown(response, unsafe_allow_html=True)  # 显示回复

            messages.append({"role": "user", "content":prompt})
            messages.append({"role": "assistant", "content": response})

        elif st.session_state.mode == "执行代码":
            with st.chat_message("user", avatar=st.session_state.user):
                st.markdown( f"执行代码: \n```{prompt}```")

            try:
                response, logs, is_final_answer = agent.python_executor(prompt)
                with st.chat_message("assistant", avatar=st.session_state.ai):
                    st.markdown(f"执行结果: \n```{response}```")
                st.success("代码运行成功！")
            except Exception as e:
                response=e
                with st.chat_message("assistant", avatar=st.session_state.ai):
                    st.markdown(f"执行结果: \n```{response}```")
                st.error("代码运行失败！")

            messages.append({"role": "user", "content": f"执行代码: \n```{prompt}```"})
            messages.append({"role": "assistant", "content": f"执行结果: \n```{response}```"})


    st.session_state.mode = st.radio("选择模式", ("聊天", "执行代码"), horizontal=True)
    st.button("清空对话", on_click=clear_chat_history)


    # 在侧边栏中显示文件列表
    display_file_list(directory='tmp')

    # 更新并显示变量列表
    display_value_list(agent)

    # 工具列表
    display_tools_list(tools=agent_tools_desc)
    


if __name__ == "__main__":

    st.title("CodeGenie")

	# 启动聊天功能
    chat()

    
    

    
    
