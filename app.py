import streamlit as st
from openai import OpenAI

# 页面配置
st.set_page_config(
    page_title="我的 AI 助手",
    page_icon="🤖",
    layout="wide"
)

# 主标题
st.title("🤖 我的 AI 助手")

# 侧边栏
with st.sidebar:
    st.header("设置")
    
    # API Key 输入
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="请输入你的 OpenAI API 密钥",
        key="api_key_input"
    )
    
    # Base URL 输入
    base_url = st.text_input(
        "Base URL (可选)",
        value="https://api.siliconflow.cn/v1",
        help="留空则使用 OpenAI 官方地址,或填入兼容 OpenAI 格式的其他服务地址(如 DeepSeek、Moonshot)",
        key="base_url_input"
    )
    
    # 模型选择
    model = st.selectbox(
        "选择模型",
        ["deepseek-ai/DeepSeek-V3.2-Exp", "deepseek-ai/DeepSeek-V3", "deepseek-ai/DeepSeek-R1"],
        index=0
    )
    
    st.divider()
    
    # 清空对话按钮
    if st.button("清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 聊天输入
if prompt := st.chat_input("输入你的问题..."):
    # 检查是否输入了 API Key
    if not api_key:
        st.warning("请在侧边栏输入 OpenAI API Key")
        st.stop()
    
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 生成 AI 回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 创建 OpenAI 客户端
            if base_url and base_url.strip():
                client = OpenAI(api_key=api_key, base_url=base_url.strip())
            else:
                client = OpenAI(api_key=api_key)
            
            # 调用 API
            stream = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            # 流式输出
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"发生错误: {str(e)}")
            full_response = f"抱歉,发生了错误: {str(e)}"
            message_placeholder.markdown(full_response)
    
    # 添加助手消息到历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})
