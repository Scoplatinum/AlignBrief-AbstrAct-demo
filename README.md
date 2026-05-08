# AlignBrief｜多方协作会议对齐助手

一句话描述：把一段多方协作会议记录，通过 GPT API 转成不同角色能执行、能追问、能留档的行动 brief。

## 产品问题

跨学科项目会议里，不同角色真正需要带走的信息并不一样。新加入的学生需要知道先整理什么，项目协调者需要拆任务，科研负责人需要判断最低科学要求，工程合作者需要确认设备参数取舍，数据成员需要设计 QC，现场/动物中心合作方需要守住动物状态和操作边界。

普通会议纪要容易停留在“会议说了什么”，但会后推进更需要回答“我这个角色下一步该怎么做”。

## 为什么这不只是会议总结器

普通会议总结回答：“这场会说了什么？”

AlignBrief 回答：“对我这个角色来说，我需要理解什么、执行什么、确认什么、留档什么？”

它更像飞书、Notion、Teams 等会议纪要工具之后的一层会后对齐工作流，用来把同一份会议记录转成角色化行动清单。最终 Demo 使用 GPT API 实时生成，因此用户修改会议记录、项目背景、角色或会议类型后，输出会基于当前输入重新生成。

## Demo 场景

本 Demo 默认填入一个脱敏虚构场景：神经/动物行为实验室与设备公司、动物中心和数据分析成员合作，试点一款动物可穿戴记录设备。当前阶段不是正式实验，而是判断设备是否适合进入小规模试点。

你也可以直接替换为自己的会议记录和项目背景，用同一个界面测试不同角色的会后行动 brief。

## 如何本地运行

建议使用 Python 3.10 或更新版本。

```bash
pip install -r requirements.txt
streamlit run app.py
```

应用启动后会自动填入虚构会议记录和项目背景。输入 API key 后，选择角色和会议类型，点击“生成角色化行动清单”即可调用 GPT API 生成结果。

## API Key 设置

本地 Demo 支持两种方式提供 OpenAI API key：

1. 在侧边栏的 `OpenAI API Key` 密码输入框中填写。
2. 在本地环境变量中设置 `OPENAI_API_KEY`。

优先级是：UI 密码输入框优先，其次读取环境变量。

示例：

```bash
OPENAI_API_KEY=your_api_key_here
```

也可以使用仓库里的 [.env.example](.env.example) 查看变量名示例。请不要把真实 API key 提交到 GitHub。

## Key 与隐私说明

本地 Streamlit Demo 不会把 API key 写入代码、文件或 Git 仓库；UI 输入的 key 只存在于当前本地 Streamlit 会话状态中。

如果要部署到公网，不应让多人在公开页面共用或提交同一个 key。更合适的做法是使用服务端密钥、用户鉴权、权限控制、日志脱敏和调用限额等安全设计。

## 当前限制

- 当前只支持文本输入，不支持音频上传或自动转写。
- 当前 Demo 依赖 OpenAI API；没有 API key 时不会生成模拟结果。
- 输出只基于当前输入文本，不接入内部知识库或历史项目记忆。
- 输出仅作为会后复述和对齐草稿，关键决策仍需由项目负责人确认。
- 本 Demo 不包含用户登录、权限管理、数据库或部署配置。

## 未来功能

- audio transcription
- local/private deployment
- multi-meeting project memory
- role-based onboarding
- unresolved question tracking
- permission-aware retrieval from internal documents
