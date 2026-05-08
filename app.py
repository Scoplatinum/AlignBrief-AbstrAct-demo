import os

import streamlit as st


APP_TITLE = "AlignBrief｜多方协作会议对齐助手"
APP_SUBTITLE = "从会议记录到角色化行动清单"

SAMPLE_MEETING_NOTE = """PI：这个设备先别急着上正式实验，我们先打个样。现在最重要的不是把方案写得多完整，而是判断这个方向能不能往前走。
工程这边上次说可以再轻一点，但如果续航和采样率受影响，要提前说清楚。研究这边也不要什么指标都想要，先明确哪些数据是必须有的。
动物中心这边我比较担心固定方式，不能为了数据把动物状态搞乱。数据同学不要只给均值，要能看出异常到底是设备问题、动物状态问题，还是记录流程问题。
新来的同学先别急着查一堆文献，把现有流程、要记录的点、需要问工程方的问题先拉出来。下周我们要一个一页纸判断，不是论文，也不是完整方案，重点是能不能继续试、怎么试、谁还要确认什么。"""

SAMPLE_PROJECT_BACKGROUND = """一个神经/动物行为实验室正在和设备公司、动物中心和数据分析成员合作，试点一款动物可穿戴记录设备。当前阶段不是正式实验，而是判断设备是否适合进入小规模试点。团队需要同时考虑科学目标、设备重量、续航、采样率、固定方式、动物状态、数据质量和下周汇报材料。"""

ROLE_OPTIONS = [
    "新加入的学生/科研助理",
    "项目协调者",
    "科研负责人",
    "工程合作者",
    "数据分析成员",
    "现场/动物中心合作方",
    "后来加入的新人",
]

MEETING_TYPE_OPTIONS = [
    "新设备/新方法试点",
    "横向项目推进",
    "实验方案讨论",
    "论文/报告修改",
]

MODEL_OPTIONS = [
    "gpt-4.1-mini",
    "gpt-4o-mini",
]

SECTION_NAMES = [
    "会议核心共识",
    "对当前角色最重要的信息",
    "下一步行动清单",
    "仍需确认的问题",
    "可复用留档卡",
    "依据与不确定性提示",
]


def initialize_session_state():
    if "meeting_note" not in st.session_state:
        st.session_state.meeting_note = SAMPLE_MEETING_NOTE
    if "project_background" not in st.session_state:
        st.session_state.project_background = SAMPLE_PROJECT_BACKGROUND


def restore_sample_text():
    st.session_state.meeting_note = SAMPLE_MEETING_NOTE
    st.session_state.project_background = SAMPLE_PROJECT_BACKGROUND
    st.session_state.pop("brief_markdown", None)
    st.session_state.pop("generated_role", None)


def parse_ai_response(text):
    if all(section in text for section in SECTION_NAMES):
        return text

    scaffold = []
    for index, section in enumerate(SECTION_NAMES):
        if index == 0:
            body = "AI 返回内容未能稳定拆分为六个标题，以下保留原始输出，供人工复核。"
        else:
            body = "请在原始输出中复核这一项。"
        scaffold.append(f"## {section}\n{body}")

    return "\n\n".join(scaffold) + "\n\n---\n\n" + text


def build_prompt(role, meeting_type, project_background, meeting_note):
    required_sections = "\n".join(f"## {section}" for section in SECTION_NAMES)
    return f"""
你是 AlignBrief，一个会议后的角色化对齐助手。请基于用户提供的会议记录和项目背景，为指定角色生成中文行动 brief。

这是一个会议对齐工具，不是普通会议总结器。你的输出应回答：
“对我这个角色来说，我需要理解什么、执行什么、确认什么、留档什么？”

必须遵守：
1. 必须输出且只输出以下六个二级标题：
{required_sections}
2. 每个 section 用精炼项目符号输出，适合复制到飞书、Notion、Teams 等协作工具。
3. 必须紧扣当前会议记录、项目背景、角色和会议类型。
4. 不要编造会议记录和项目背景之外的事实，不要补充不存在的公司、实验、人员、数据或日期。
5. 对缺失、不确定、需要追问的信息，放入“仍需确认的问题”。
6. 在“依据与不确定性提示”中说明输出依据、哪些内容不确定、关键决策仍需负责人确认。
7. “下一步行动清单”必须针对所选角色，不要写成所有人的通用任务。

会议类型：{meeting_type}
我的角色：{role}

项目背景：
{project_background}

会议记录：
{meeting_note}
"""


def get_error_message(error):
    status_code = getattr(error, "status_code", None)
    error_code = getattr(error, "code", None)
    message = str(error).lower()

    if error_code == "insufficient_quota" or "insufficient_quota" in message:
        return "API 额度不足。请检查 OpenAI Platform 的 Billing/Usage，充值或更换有额度的 key。"

    if status_code == 401 or "invalid_api_key" in message or "authentication" in message:
        return "API Key 无效或无权限，请检查 key 是否复制完整。"

    error_type = error.__class__.__name__
    return f"生成失败：{error_type}。请检查网络、模型名称或输入内容后重试。"


def generate_ai_brief(api_key, model, role, meeting_type, project_background, meeting_note):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一个谨慎的中文会议对齐助手，只根据给定材料生成角色化行动 brief。",
            },
            {
                "role": "user",
                "content": build_prompt(role, meeting_type, project_background, meeting_note),
            },
        ],
        temperature=0.2,
    )
    text = response.choices[0].message.content or ""
    return parse_ai_response(text.strip())


def render_comparison_block():
    st.markdown("### 为什么这不是普通会议总结？")
    st.markdown(
        """
- 普通会议纪要回答：“这场会说了什么？”
- AlignBrief 回答：“对我这个角色来说，我需要理解什么、执行什么、确认什么、留档什么？”
- 它可以作为飞书、Notion、Teams 等会议纪要工具之后的一层会后对齐工作流。
"""
    )


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="AB", layout="wide")
    initialize_session_state()

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    st.write("把一段多方协作会议记录，转成不同角色能执行、能追问、能留档的行动 brief。")
    st.info("本 Demo 不是会议总结器，而是会议后的角色化对齐层。")

    with st.sidebar:
        st.header("生成设置")
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            help="仅用于本地 Demo 调用，不会写入代码或 GitHub。请不要在公开录屏中展示。",
        )
        st.caption(
            "本地 Streamlit Demo 不保存 API key；如果部署到公网，请不要让多人共用同一个 key，"
            "应改用服务端密钥和用户鉴权。"
        )

        model = st.selectbox("模型", MODEL_OPTIONS, index=0)
        role = st.selectbox("我的角色", ROLE_OPTIONS)
        meeting_type = st.selectbox("会议类型", MEETING_TYPE_OPTIONS)
        st.caption("当前版本使用 GPT API 实时生成。")

        api_key = api_key_input.strip() or os.getenv("OPENAI_API_KEY", "").strip()
        has_api_key = bool(api_key)
        if not has_api_key:
            st.warning("请先输入 OpenAI API Key，或在本地设置 OPENAI_API_KEY。")

        generate_clicked = st.button(
            "生成角色化行动清单",
            type="primary",
            use_container_width=True,
            disabled=not has_api_key,
        )

    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        input_header, restore_button_col = st.columns([1, 1])
        with input_header:
            st.subheader("输入")
        with restore_button_col:
            st.button("恢复示例文本", on_click=restore_sample_text, use_container_width=True)

        meeting_note = st.text_area("会议记录", key="meeting_note", height=300)
        project_background = st.text_area("项目背景", key="project_background", height=180)

    if generate_clicked:
        with st.spinner("正在使用 GPT API 生成角色化行动清单..."):
            try:
                st.session_state.brief_markdown = generate_ai_brief(
                    api_key=api_key,
                    model=model,
                    role=role,
                    meeting_type=meeting_type,
                    project_background=project_background,
                    meeting_note=meeting_note,
                )
                st.session_state.generated_role = role
                st.session_state.generated_model = model
            except Exception as error:
                st.session_state.pop("brief_markdown", None)
                st.session_state.pop("generated_role", None)
                st.error(get_error_message(error))

    with col_output:
        st.subheader("角色化行动清单")
        if not has_api_key:
            st.info("请先输入 OpenAI API Key，或在本地设置 OPENAI_API_KEY。")
        elif "brief_markdown" in st.session_state:
            st.caption(
                f"当前 brief 角色：{st.session_state.generated_role} ｜ 模型：{st.session_state.generated_model}"
            )
            st.markdown(st.session_state.brief_markdown)
        else:
            st.info("输入 API key 后，点击“生成角色化行动清单”查看 GPT 实时生成结果。")

    st.divider()
    render_comparison_block()

    st.divider()
    st.caption(
        "本 Demo 使用脱敏虚构案例。实际使用时应在合规授权和内部权限范围内处理会议内容。"
        "输出仅作为会后复述和对齐草稿，关键决策仍需由项目负责人确认。"
    )


if __name__ == "__main__":
    main()
