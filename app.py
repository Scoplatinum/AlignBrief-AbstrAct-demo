import os

import streamlit as st


APP_TITLE = "AlignBrief — AbstrAct｜多方协作会议对齐助手"
APP_SUBTITLE = "从抽象会议记录到角色化行动清单"
APP_SLOGAN = "From abstract talk to actionable briefs."

SAMPLE_MEETING_NOTE = """PI：柔性电极这个事情先不要一下子做成正式课题，先别急。我们现在不是要把所有机制都讲清楚，也不是要马上做一个很漂亮的大方案。现在就是先看一看这个方向有没有必要往下走，先做一个小判断。
材料这边上次说基底还能再软一点，但是软了以后会不会卷、会不会贴不住、会不会影响后面封装，这些要说清楚。工程这边也别只说“可以优化”，要把能优化到什么程度、代价是什么写出来。大家先别都说“再看看”，这个再看看最后要落到谁看、看什么、怎么看。
研究这边也不要一上来就把所有脑区、所有指标、所有时间点都放进去。先定一个最低版本，最低版本就能说明问题的那种。比如信号有没有、稳定不稳定、噪声是不是能接受、植入或者贴附过程会不会把前面的状态搞乱。这个“能接受”也要先有个粗标准，不然下周还是会绕回来。
平台老师这边主要担心操作窗口和重复性。现在电极太柔，拿起来、定位、固定、记录，这几个环节到底哪个最容易出问题，要先拆开。不能只说“操作有点难”，这个难到底是手法难、时间长、固定不稳，还是后续观察不好做。这个要记下来，先记下来。
数据同学这边不要只给一张平均曲线。平均曲线当然要有，但更重要的是异常从哪里来。是电极接触问题，是接口问题，是噪声问题，是样本状态问题，还是记录流程本身没有对齐。这个要能分出来，至少要有一个标记表，哪怕第一版很粗。
工程同学刚才提到接口板可以先用临时版本，我觉得可以，但临时版本要讲清楚边界。比如线缆、连接器、封装、灭菌或者清洁方式，哪些只是为了这次小样，哪些未来一定要重做。不要让大家以为临时版本就是最终设计。
新加入的同学先不要急着查一大堆综述。综述可以后面补。现在先把现有流程拉一遍，把大家刚才说的几个“先看一看”“再问一下”“找个小样试试”翻译成问题清单。尤其是要问工程方、材料方、平台方的问题，先列出来。
协调这边下周需要一个一页纸，不是完整方案，不是论文框架，也不是最终技术路线。一页纸就回答几件事：我们现在到底在判断什么，最低可行版本是什么，谁要在下周前补什么信息，哪些地方不确定，哪些地方如果不满足就先停。
PI：我再重复一下，先不要扩大，先不要扩大。我们先把这个事情说清楚：不是证明它一定有用，而是判断它值不值得进入下一步小试。下周不要给我一个很长的文档，就一页纸，能看懂、能追问、能决定下一步。"""

SAMPLE_PROJECT_BACKGROUND = """一个神经工程协作项目正在讨论一款神经柔性电极原型。项目涉及研究团队、材料与工程合作者、实验平台支持人员和数据分析成员。"""

ROLE_OPTIONS = [
    "新加入的学生/科研助理",
    "项目协调者",
    "科研负责人",
    "工程合作者",
    "数据分析成员",
    "现场/动物中心合作方",
    "后续进行对接工作的新人",
    "其他部门概况了解者",
    "非直接执行的相关观察者",
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

GLOSSARY_SECTION = "名词解释与背景补充建议"


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


def get_expected_sections(include_glossary):
    if include_glossary:
        return SECTION_NAMES + [GLOSSARY_SECTION]
    return SECTION_NAMES


def parse_ai_response(text, include_glossary):
    expected_sections = get_expected_sections(include_glossary)
    if all(section in text for section in expected_sections):
        return text

    scaffold = []
    for index, section in enumerate(expected_sections):
        if index == 0:
            body = "AI 返回内容未能稳定拆分为指定标题，以下保留原始输出，供人工复核。"
        else:
            body = "请在原始输出中复核这一项。"
        scaffold.append(f"## {section}\n{body}")

    return "\n\n".join(scaffold) + "\n\n---\n\n" + text


def build_prompt(role, meeting_type, project_background, meeting_note, include_glossary):
    expected_sections = get_expected_sections(include_glossary)
    required_sections = "\n".join(f"## {section}" for section in expected_sections)
    glossary_instruction = ""
    if include_glossary:
        glossary_instruction = (
            "\n10. 用户勾选了“名词解释与背景补充建议”。请额外输出“## 名词解释与背景补充建议”。"
            "这个 section 要用大白话解释重要术语、缩写、内部黑话或专业概念。"
            "如果某个词在当前材料里含义不明确，请标记为“需结合项目内部语境确认”。"
        )

    return f"""
你是 AlignBrief — AbstrAct，一个会议后的角色化对齐助手。请基于用户提供的会议记录和项目背景，为指定角色生成中文行动 brief。

这是一个会议对齐工具，不是普通会议总结器。你的输出应回答：
“对我这个角色来说，我需要理解什么、执行什么、确认什么、留档什么？”

必须遵守：
1. 必须输出且只输出以下二级标题：
{required_sections}
2. 每个 section 用精炼项目符号输出，适合复制到飞书、Notion、Teams 等协作工具。
3. 必须紧扣当前会议记录、项目背景、角色和会议类型。
4. 不要编造会议记录和项目背景之外的事实，不要补充不存在的公司、实验、人员、数据或日期。
5. 对缺失、不确定、需要追问的信息，放入“仍需确认的问题”。
6. 在“依据与不确定性提示”中说明输出依据、哪些内容不确定、关键决策仍需负责人确认。
7. “下一步行动清单”必须针对所选角色，不要写成所有人的通用任务。
8. 请尽量使用大白话解释，不要把会议里的抽象词直接换成另一组抽象词。遇到专业术语时，如果用户勾选了名词解释，请用新人能看懂的话解释。
9. 请体现跨时间协作价值：让参会者能执行，让未参会者能理解上下文，让后续接手者能知道项目阶段、关键共识、风险和应该找谁确认。{glossary_instruction}

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


def generate_ai_brief(
    api_key,
    model,
    role,
    meeting_type,
    project_background,
    meeting_note,
    include_glossary,
):
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
                "content": build_prompt(
                    role,
                    meeting_type,
                    project_background,
                    meeting_note,
                    include_glossary,
                ),
            },
        ],
        temperature=0.2,
    )
    text = response.choices[0].message.content or ""
    return parse_ai_response(text.strip(), include_glossary)


def render_comparison_block():
    st.markdown("### 为什么这不是普通会议总结？")
    st.markdown(
        """
- 普通会议纪要回答：“这场会说了什么？”
- AlignBrief 回答：“对我这个角色来说，我需要理解什么、执行什么、确认什么、留档什么？”
- 它可以作为飞书、Notion、Teams 等会议纪要工具之后的一层会后对齐工作流。
"""
    )


def render_cross_time_block():
    st.markdown("### 它也解决“后来的人怎么接上”的问题")
    st.markdown(
        """
- 参会者需要会后行动清单。
- 未参会者需要快速理解上下文。
- 后续接手者需要知道项目阶段、关键共识、风险和应该找谁确认。
- 团队需要把一次会议沉淀成可交接、可复用的项目知识资产。
"""
    )


def render_story_expanders():
    with st.expander("为什么叫 AbstrAct？"):
        st.write(
            "AbstrAct 把 Abstract 和 Act 放在一起：前半段承认会议里常常有很多抽象判断、模糊共识和没说完的背景；"
            "后半段提醒我们，会后真正需要的是能行动、能追问、能交接的 brief。"
        )

    with st.expander("灵感来源：听不懂玄之又玄的会，也想贯彻落实"):
        st.write(
            "有时候一句“这个先推进一下”“下周给个判断”“你们再对一对”，听起来很短，背后却可能藏着目标、责任人、交付物、判断标准和历史背景。"
            "AlignBrief — AbstrAct 不替人做决定，只帮团队把这些话拆成可确认、可执行、可交接的行动入口。"
        )


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="AB", layout="wide")
    initialize_session_state()

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    st.caption(APP_SLOGAN)
    st.write("把一段抽象、分散、跨角色的会议记录，转成不同角色能执行、能追问、能交接、能留档的行动 brief。")
    st.info("本 Demo 不是会议总结器，而是会议后的角色化对齐层，也是一层给后来加入者看的项目接续说明。")
    render_story_expanders()

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
        include_glossary = st.checkbox("需要名词解释与背景补充建议", value=False)
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

        st.warning("请使用脱敏文本测试。当前版本会把输入内容发送到所选模型服务进行生成。")
        meeting_note = st.text_area("会议记录", key="meeting_note", height=300)
        st.caption(
            "案例是虚拟场景，仅供参考。我们更鼓励输入你实际需要整理的交谈文本。"
            "“项目背景”后续可以拓展为接入项目背景材料、内部文档或知识库。"
        )
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
                    include_glossary=include_glossary,
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
    render_cross_time_block()

    st.divider()
    st.caption(
        "本 Demo 使用脱敏虚构案例。实际使用时应在合规授权和内部权限范围内处理会议内容。"
        "输出仅作为会后复述、行动拆解和待确认问题整理，不作为最终决策、责任分配或专业判断依据。"
    )


if __name__ == "__main__":
    main()
