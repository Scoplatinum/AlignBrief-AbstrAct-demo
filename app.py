import os

import streamlit as st


APP_TITLE = "AlignBrief｜多方协作会议对齐助手"
APP_SUBTITLE = "从会议记录到角色化行动清单"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

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

GENERATION_MODE_OPTIONS = [
    "Demo 模板生成",
    "AI 生成（如已配置 API key）",
]

SECTION_NAMES = [
    "会议核心共识",
    "对当前角色最重要的信息",
    "下一步行动清单",
    "仍需确认的问题",
    "可复用留档卡",
    "依据与不确定性提示",
]


ROLE_BRIEFS = {
    "新加入的学生/科研助理": {
        "focus": "你现在的任务不是写完整方案，也不是先铺开大量文献综述，而是把试点判断所需的基础材料整理清楚。",
        "actions": [
            "整理现有试点流程：设备准备、动物佩戴、记录开始/结束、异常记录、数据交接。",
            "列出必须记录的观察点：动物状态、固定方式、佩戴时长、采样状态、操作耗时。",
            "形成工程方问题清单：重量能否降低、续航与采样率如何取舍、数据导出格式是什么。",
            "搭建一页纸试点判断框架：能不能继续试、怎么试、谁还需要确认什么。",
        ],
        "questions": [
            "哪些数据指标是本轮试点必须有，哪些可以暂缓？",
            "设备减重是否会影响续航或采样率？影响范围是多少？",
            "动物中心认可的固定方式和预实验边界是什么？",
        ],
        "archive": "学生/助理留档卡：当前阶段=小规模试点前判断；本周交付=流程梳理+记录点+工程问题+一页纸判断框架；不要交付=完整论文式方案。",
    },
    "项目协调者": {
        "focus": "你需要把会议共识拆成各方下周前必须交付的输入，并让一页纸 brief 能支撑项目推进判断。",
        "actions": [
            "按角色分发任务：研究侧定义最低数据指标，工程侧确认设备参数取舍，动物中心确认固定与安全边界，数据侧设计 QC 口径。",
            "建立下周前输入清单：每方要交什么、格式是什么、最晚什么时候给。",
            "把一页纸项目 brief 拆成：目标、当前判断问题、各方输入、关键风险、待确认事项、继续/暂停标准。",
            "确认会议后责任人，避免所有问题都停留在“大家再看看”。",
        ],
        "questions": [
            "下周的一页纸判断由谁汇总，谁最终确认？",
            "工程、动物中心、数据分析各自的输入截止时间是什么？",
            "如果关键参数无法确认，本轮试点是否延期或缩小范围？",
        ],
        "archive": "协调者留档卡：会议产出不是纪要，而是角色任务表+一页纸 brief 结构+待确认责任人。",
    },
    "科研负责人": {
        "focus": "你要收敛科学目标，定义试点最低可用数据和继续推进的判断标准，避免需求过宽导致试点失焦。",
        "actions": [
            "明确本轮必须获得的数据指标，区分“必要指标”和“可选指标”。",
            "定义继续推进标准：设备可佩戴、动物状态稳定、数据质量可解释、流程负担可接受。",
            "决定哪些科学问题暂不进入本轮试点，避免正式实验化。",
            "审阅一页纸判断，确认它足以支持“继续试、调整后再试、暂缓”的决策。",
        ],
        "questions": [
            "最低科学可用数据是什么？采样率下限能否接受？",
            "异常数据达到什么程度会判定设备或流程不可用？",
            "本轮是否只判断可行性，而不做效果结论？",
        ],
        "archive": "负责人留档卡：本轮决策点=是否进入小规模试点；核心标准=最低数据指标+动物状态+设备流程可行性；非目标=完整正式实验方案。",
    },
    "工程合作者": {
        "focus": "你需要把设备参数和工程取舍讲清楚，尤其是重量、续航、采样率、固定方式和数据导出对试点的影响。",
        "actions": [
            "给出当前设备重量、可减重空间，以及减重对结构稳定性的影响。",
            "说明续航和采样率的取舍：不同设置下可记录多久、数据粒度如何变化。",
            "提供固定方式建议，并标注需要动物中心验证的安全边界。",
            "确认数据导出格式、时间戳、缺失记录标记，以及是否支持异常排查。",
            "如场景涉及潮湿或清洁流程，补充防水/防护等级或限制条件。",
        ],
        "questions": [
            "减重后的续航和采样率是否仍满足研究侧最低需求？",
            "固定件是否会影响动物状态或动物中心操作流程？",
            "导出的数据能否区分设备中断、佩戴异常和记录流程问题？",
        ],
        "archive": "工程方留档卡：需提交=参数取舍表、固定建议、数据导出说明、风险限制；核心口径=不能只说“可以做”，要说明代价。",
    },
    "数据分析成员": {
        "focus": "你要把数据质量和异常归因框架提前设计好，不能只给均值，需要帮助团队判断问题来自哪里。",
        "actions": [
            "设计 QC 表：缺失率、异常值、时间戳连续性、采样稳定性、佩戴阶段标记。",
            "建立异常归因分类：设备问题、动物状态问题、记录流程问题、无法判断。",
            "要求现场记录与数据文件能对应：动物状态、佩戴时间、操作事件、异常备注。",
            "准备下周一页纸中的数据质量判断模板，而不是正式统计分析报告。",
        ],
        "questions": [
            "设备原始数据包含哪些字段？是否有时间戳和状态码？",
            "现场记录能否支持异常归因，而不是只留下数据文件？",
            "本轮 QC 的通过标准是什么：缺失率、连续时长、异常阈值如何定？",
        ],
        "archive": "数据成员留档卡：本轮重点=QC 与异常归因；输出=数据质量判断模板；不是=只汇报均值或做正式结果分析。",
    },
    "现场/动物中心合作方": {
        "focus": "你需要守住动物状态、安全和操作可行性边界，确保设备试点不会为了数据破坏动物状态或现场流程。",
        "actions": [
            "评估固定方式是否稳定、安全、可重复，并列出不接受的固定条件。",
            "明确预实验要求：佩戴时长、观察频率、停止条件、现场记录表。",
            "估算操作负担：准备时间、固定时间、观察人员需求、清洁或维护要求。",
            "向研究与工程方反馈动物状态风险，要求先小范围打样再进入正式实验。",
        ],
        "questions": [
            "设备重量和固定方式是否会改变动物自然状态？",
            "出现挣脱、应激、活动异常时的停止标准是什么？",
            "现场人员是否需要额外培训或设备维护步骤？",
        ],
        "archive": "动物中心/现场留档卡：核心关注=动物状态+固定安全+操作负担；需确认=预实验边界、停止条件、记录表。",
    },
    "后来加入的新人": {
        "focus": "你需要快速理解项目处在哪个阶段、这次会议为什么重要、先读什么、问谁，以及哪些风险不能误解。",
        "actions": [
            "先读项目背景、一页纸判断框架、设备参数表和现场记录表，不必从完整文献综述开始。",
            "向协调者确认当前阶段：不是正式实验，而是进入小规模试点前的可行性判断。",
            "向研究侧询问最低科学指标，向工程侧询问参数取舍，向动物中心询问固定和安全边界。",
            "记录关键风险：设备参数不足、动物状态受影响、数据异常无法归因、流程负担过重。",
        ],
        "questions": [
            "这个项目当前是打样判断、试点，还是正式实验？",
            "已有材料中哪一份代表最新共识？",
            "遇到设备、动物状态、数据质量问题时分别找谁确认？",
        ],
        "archive": "新人 onboarding 留档卡：项目阶段=正式实验前可行性判断；必读=背景+一页纸 brief+参数/QC/现场记录；风险=不要把试点判断当成最终实验结论。",
    },
}


def build_template_brief(role, meeting_type, project_background, meeting_note):
    role_brief = ROLE_BRIEFS[role]

    return {
        "会议核心共识": [
            f"本次会议类型是“{meeting_type}”，重点是判断设备方向是否值得进入小规模试点。",
            "当前不是正式实验阶段，也不是撰写完整方案阶段，而是先打样、先判断可行性。",
            "团队需要同时对齐科学最低需求、设备参数取舍、动物状态安全、数据质量和下周一页纸材料。",
        ],
        "对当前角色最重要的信息": [
            role_brief["focus"],
            "会议明确要求各角色围绕“能否继续试、怎么试、谁还要确认什么”形成可执行输入。",
        ],
        "下一步行动清单": role_brief["actions"],
        "仍需确认的问题": role_brief["questions"],
        "可复用留档卡": [
            role_brief["archive"],
            "通用留档字段：会议日期、角色、下一步责任人、关键参数、动物状态观察点、数据 QC 口径、待确认问题。",
        ],
        "依据与不确定性提示": [
            "依据来自当前输入的虚构会议记录和项目背景，未使用任何真实实验、公司或个人数据。",
            "会议中没有给出具体设备重量、续航时长、采样率数值、动物种类或实验天数，因此这些内容只能列为待确认项。",
            "输出是会后对齐草稿，不替代项目负责人、动物伦理/合规流程或工程验收结论。",
            f"输入文本长度：会议记录约 {len(meeting_note)} 字，项目背景约 {len(project_background)} 字。",
        ],
    }


def format_brief_markdown(brief):
    blocks = []
    for section in SECTION_NAMES:
        items = brief.get(section, [])
        if isinstance(items, str):
            body = items
        else:
            body = "\n".join(f"- {item}" for item in items)
        blocks.append(f"## {section}\n{body}")
    return "\n\n".join(blocks)


def parse_ai_response(text):
    # Keep AI output simple: show it verbatim under the required section scaffold if parsing is uncertain.
    if all(section in text for section in SECTION_NAMES):
        return text

    fallback_lines = [
        "AI 返回内容未能稳定拆分为六个标题，以下保留原始输出，供人工复核：",
        "",
        text,
    ]
    return "\n\n".join(
        f"## {section}\n{fallback_lines[0] if index == 0 else '请在原始输出中复核这一项。'}"
        for index, section in enumerate(SECTION_NAMES)
    ) + "\n\n---\n\n" + "\n".join(fallback_lines)


def generate_ai_brief(role, meeting_type, project_background, meeting_note):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("未检测到 OPENAI_API_KEY，已自动使用 Demo 模板生成。")
        return format_brief_markdown(
            build_template_brief(role, meeting_type, project_background, meeting_note)
        )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = f"""
你是 AlignBrief，一个会议后的角色化对齐助手。请基于用户提供的会议记录和项目背景，为指定角色生成中文行动 brief。

要求：
1. 必须输出且只输出以下六个二级标题：
## 会议核心共识
## 对当前角色最重要的信息
## 下一步行动清单
## 仍需确认的问题
## 可复用留档卡
## 依据与不确定性提示
2. 这不是普通会议总结。请聚焦这个角色需要理解什么、执行什么、确认什么、留档什么。
3. 不要编造会议记录和项目背景之外的事实。
4. 信息不确定时，放入“仍需确认的问题”或“依据与不确定性提示”。
5. 用精炼项目符号输出，适合会后复制到协作工具。

会议类型：{meeting_type}
我的角色：{role}

项目背景：
{project_background}

会议记录：
{meeting_note}
"""
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个谨慎的中文会议对齐助手，只根据给定材料生成角色化行动 brief。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        text = response.choices[0].message.content or ""
        return parse_ai_response(text.strip())
    except Exception as error:
        st.warning(f"AI 生成失败，已自动切换为 Demo 模板生成。错误信息：{error}")
        return format_brief_markdown(
            build_template_brief(role, meeting_type, project_background, meeting_note)
        )


def generate_brief(role, meeting_type, generation_mode, project_background, meeting_note):
    if generation_mode == "AI 生成（如已配置 API key）":
        return generate_ai_brief(role, meeting_type, project_background, meeting_note)

    return format_brief_markdown(
        build_template_brief(role, meeting_type, project_background, meeting_note)
    )


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

    st.title(APP_TITLE)
    st.caption(APP_SUBTITLE)
    st.write("把一段多方协作会议记录，转成不同角色能执行、能追问、能留档的行动 brief。")
    st.info("本 Demo 不是会议总结器，而是会议后的角色化对齐层。")

    with st.sidebar:
        st.header("生成设置")
        role = st.selectbox("我的角色", ROLE_OPTIONS)
        meeting_type = st.selectbox("会议类型", MEETING_TYPE_OPTIONS)
        generation_mode = st.selectbox("生成模式", GENERATION_MODE_OPTIONS)
        generate_clicked = st.button("生成角色化行动清单", type="primary", use_container_width=True)

    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("输入")
        meeting_note = st.text_area("会议记录", value=SAMPLE_MEETING_NOTE, height=300)
        project_background = st.text_area("项目背景", value=SAMPLE_PROJECT_BACKGROUND, height=180)

    if generate_clicked or "brief_markdown" not in st.session_state:
        st.session_state.brief_markdown = generate_brief(
            role=role,
            meeting_type=meeting_type,
            generation_mode=generation_mode,
            project_background=project_background,
            meeting_note=meeting_note,
        )
        st.session_state.generated_role = role

    with col_output:
        st.subheader("角色化行动清单")
        st.caption(f"当前 brief 角色：{st.session_state.get('generated_role', role)}")
        st.markdown(st.session_state.brief_markdown)

    st.divider()
    render_comparison_block()

    st.divider()
    st.caption(
        "本 Demo 使用脱敏虚构案例。实际使用时应在合规授权和内部权限范围内处理会议内容。"
        "输出仅作为会后复述和对齐草稿，关键决策仍需由项目负责人确认。"
    )


if __name__ == "__main__":
    main()
