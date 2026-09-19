"""Wizard schema: steps, fields, genre presets. No third-party names."""

from __future__ import annotations

APP_VERSION = "1.3.0"
PRODUCT_ZH = "框架策划台"
PRODUCT_EN = "Framework Brief Desk"


def L(zh: str, en: str) -> dict:
    return {"zh": zh, "en": en}


def field(key: str, kind: str, label: dict, hint: dict, **extra) -> dict:
    item = {"key": key, "kind": kind, "label": label, "hint": hint}
    item.update(extra)
    return item


GENRES = [
    {"id": "asymmetric_social", "zh": "不对称社交推理", "en": "Asymmetric social deduction"},
    {"id": "squad_tactical", "zh": "小队战术射击", "en": "Squad tactical shooter"},
    {"id": "objective_team", "zh": "团队目标争夺", "en": "Team objective contest"},
    {"id": "infil_defense", "zh": "建筑潜入与据守", "en": "Infiltration and holdout"},
    {"id": "extraction_survival", "zh": "撤离生存对抗", "en": "Extraction survival"},
    {"id": "lane_arena", "zh": "分路竞技对战", "en": "Lane arena"},
    {"id": "deck_roguelike", "zh": "卡组构筑冒险", "en": "Deck-building adventure"},
    {"id": "idle_growth", "zh": "放置成长", "en": "Idle growth"},
    {"id": "coop_sandbox", "zh": "合作沙盒生存", "en": "Co-op sandbox survival"},
    {"id": "sim_ops", "zh": "模拟经营", "en": "Operations simulation"},
    {"id": "puzzle_story", "zh": "解谜叙事", "en": "Puzzle narrative"},
    {"id": "action_growth", "zh": "动作角色成长", "en": "Action growth"},
    {"id": "turn_strategy", "zh": "回合策略", "en": "Turn strategy"},
    {"id": "session_party", "zh": "轻量聚会对局", "en": "Session party"},
    {"id": "auto_batch", "zh": "自动编队对局", "en": "Auto-battler"},
    {"id": "stealth_horror", "zh": "潜行压迫", "en": "Stealth pressure"},
    {"id": "city_ops", "zh": "城邦经营建设", "en": "City operations"},
    {"id": "sports_season", "zh": "赛季竞技体育", "en": "Seasonal sports"},
]


def opts(*pairs):
    return [{"id": a, "zh": b, "en": c} for a, b, c in pairs]


CURVE = opts(
    ("linear", "线性", "Linear"),
    ("ease_in", "前期慢后期快", "Slow then fast"),
    ("ease_out", "前期快后期慢", "Fast then slow"),
    ("s_curve", "S 形", "S-curve"),
    ("step", "台阶突破", "Stepped gates"),
)

TYPE_LABEL = {
    "game": L("游戏框架策划案", "game framework brief"),
    "business": L("商业计划书", "investor plan"),
    "unknown": L("无法识别类型", "file of an unrecognized type"),
}

MODE_STEP = {
    "id": "mode",
    "no": "01",
    "title": L("文档类型", "Document type"),
    "lead": L("先决定产出物类型。类型决定后续步骤。", "Choose the deliverable first. The type unlocks the remaining steps."),
    "fields": [
        field(
            "docType",
            "radio",
            L("产出类型", "Deliverable"),
            L("游戏框架策划案面向研发内部对齐；商业计划书面向投资判断。", "A game brief aligns the studio. An investor plan aligns funding."),
            required=True,
            options=opts(
                ("game", "游戏框架策划案", "Game framework brief"),
                ("business", "商业计划书", "Investor plan"),
            ),
        ),
    ],
}

CHARTER_STEP = {
    "id": "charter",
    "no": "02",
    "title": L("立项身份", "Project identity"),
    "lead": L(
        "写入项目身份，或导入与当前类型一致的 JSON。类型不符将拒绝写入。",
        "Write the project identity, or import JSON that matches the current deliverable type.",
    ),
    "fields": [
        field("projectName", "text", L("项目名称", "Project name"), L("对内使用的工作名，将出现在导出封面。", "Internal working title used on the cover."), required=True, placeholder=L("例如：夜航计划", "e.g. Night Ferry")),
        field("oneLiner", "text", L("一句话定位", "One-line pitch"), L("用一句可被复述的话说明玩家或投资人为什么要在意。", "One repeatable sentence for why this matters.")),
        field(
            "orientation",
            "radio",
            L("设计导向", "Design orientation"),
            L("导向决定取舍。产品导向以未满足的情感需求为先。", "Orientation decides trade-offs. Product work starts from unmet feeling."),
            options=opts(
                ("product", "产品导向", "Product"),
                ("art", "表达导向", "Authorial"),
                ("tech", "技术或美术展示", "Tech / art showcase"),
                ("edu", "教育手段", "Education vehicle"),
                ("other", "其他约束优先", "Other constraint first"),
            ),
        ),
        field(
            "genre",
            "select",
            L("品类预设", "Category preset"),
            L("选择后可套用该品类更完整的体验、循环、上瘾与数值侧重点。可再改。", "Applies a denser library of experience, loop, habit and numeric emphasis. Editable after."),
            options=GENRES,
            when="game",
        ),
        field(
            "platforms",
            "check",
            L("目标平台", "Platforms"),
            L("平台约束手感、对局时长与变现通道。", "Platforms constrain feel, session length and revenue rails."),
            options=opts(
                ("mobile", "移动端", "Mobile"),
                ("pc", "个人电脑", "PC"),
                ("console", "主机", "Console"),
                ("web", "网页", "Web"),
            ),
        ),
        field(
            "playShape",
            "radio",
            L("对局形态", "Play shape"),
            L("单人、短局多人与长线在线会导向完全不同的系统与循环。", "Solo, session multiplayer and persistent online imply different systems."),
            options=opts(
                ("solo", "单人为主", "Mostly solo"),
                ("session", "短局多人", "Session multiplayer"),
                ("persistent", "长线在线", "Persistent online"),
                ("hybrid", "单人与多人并存", "Solo plus multiplayer"),
            ),
        ),
    ],
}


def _game_body():
    return [
        {
            "id": "market",
            "no": "03",
            "title": L("市场空白与用户", "Gap and audience"),
            "lead": L("先写清谁未被满足、缺口有多痛，再谈自己能提供什么。", "Name the unserved feeling and how acute it is before naming features."),
            "fields": [
                field("gap", "textarea", L("市场空白或问题", "Market gap"), L("几句话写清缺口。不要堆行业报告。", "A few sentences. Do not paste industry reports.")),
                field("severity", "radio", L("问题严重程度", "Severity"), L("用于判断是否值得立项。", "Used to judge whether a project is warranted."), options=opts(("mild", "有但不尖锐", "Present but mild"), ("clear", "明确且反复被抱怨", "Clear and recurring"), ("acute", "尖锐到足以换品类", "Acute enough to switch category"))),
                field("audience", "textarea", L("目标用户群划分", "Audience segments"), L("必须分组，而不是“所有玩家”。", "Must be segmented. Not “everyone”.")),
                field("needPrimary", "text", L("第一核心需求", "Primary need"), L("只写一条主需求。", "One primary need only.")),
                field("needSecondary", "text", L("第二核心需求", "Secondary need"), L("优先级低于第一条。", "Ranked below the first.")),
                field("whyNow", "textarea", L("为何是现在", "Why now"), L("技术、习惯或供给结构里，哪一层刚刚变得可做。", "Which layer of tech, habit or supply just became feasible.")),
                field("selfFit", "textarea", L("自身能力匹配", "Why this team"), L("哪一项让你比别人更适合做。", "Which asset makes this team a better fit.")),
            ],
        },
        {
            "id": "strategy",
            "no": "04",
            "title": L("战略控制点", "Strategic control"),
            "lead": L("把洞察收成控制点、阶段目标与获客/留存/付费策略。", "Turn insight into a control point, milestones and acquire / retain / pay bets."),
            "fields": [
                field("controlPoint", "text", L("战略控制点", "Control point"), L("别人难以复制的那一层。", "The hard-to-copy layer.")),
                field("positioning", "text", L("项目定位", "Positioning"), L("在品类坐标里站哪一格。", "Which cell on the category map.")),
                field("milestone", "textarea", L("阶段里程碑", "Milestones"), L("按可验证体验写。", "Write verifiable experiences.")),
                field("acqBet", "textarea", L("获客策略要点", "Acquisition bet"), L("低成本可持续的进入方式。", "A repeatable cheap entry.")),
                field("shortStay", "textarea", L("短留策略", "Short retention"), L("首日到首周靠什么回来。", "Day one to week one.")),
                field("longStay", "textarea", L("长留策略", "Long retention"), L("季度与赛季如何不散。", "What holds a season-scale population.")),
                field("payBet", "textarea", L("付费策略要点", "Monetization bet"), L("付费对应哪一种情绪。", "Which emotion payment serves.")),
            ],
        },
        {
            "id": "experience",
            "no": "05",
            "title": L("核心情感体验", "Core feelings"),
            "lead": L("先排体验优先级。机制是手段，体验是目的。", "Rank feelings first. Rules are means."),
            "fields": [
                field("feelPrimary", "text", L("主体验", "Primary feeling"), L("最想反复品尝的情绪。", "The feeling they re-enter to taste again.")),
                field("feelList", "check", L("体验簇", "Feeling cluster"), L("可多选，必须能排出先后。", "Multi-select, then order below."), options=opts(("mastery", "掌握与成长", "Mastery"), ("tension", "紧张与压迫", "Tension"), ("social", "同场与默契", "Togetherness"), ("deduce", "推理与识破", "Deduction"), ("role", "身份扮演", "Role-play"), ("fear", "恐惧与孤独", "Fear / solitude"), ("care", "照料与牵挂", "Care"), ("status", "展示与地位", "Status"), ("flow", "流畅操作快感", "Flow of control"), ("wonder", "发现与奇观", "Discovery"))),
                field("feelOrder", "textarea", L("体验优先级说明", "Priority note"), L("写清主次与不可妥协项。", "What is non-negotiable.")),
                field("identityPlay", "text", L("身份体验", "Identity to wear"), L("扮演何种未曾做过的角色。", "A role they have not lived.")),
                field("emotionOnce", "text", L("单次强烈情感", "One-shot emotion"), L("适合前期吸引，通常不支撑长线。", "Good for first contact, rarely a live spine.")),
                field("instinct", "check", L("可借用的本能", "Instincts in play"), L("大型产品里本能不作主轴。", "Not the spine of a large product."), options=opts(("instant", "即时行为即时反馈", "Instant act, instant feedback"), ("idle", "少操作仍有收获", "Gain with little input"), ("pair", "与吸引人的对象同场", "Play beside an attractive other"), ("lonely", "怕独处，要分工与交流", "Fear of solitude"))),
            ],
        },
        {
            "id": "mechanics",
            "no": "06",
            "title": L("核心机制", "Core mechanics"),
            "lead": L("用挑战类型描述手段，并写清互动与规则取舍。", "Describe the challenge type, then the rule trade-offs."),
            "fields": [
                field("challengeMode", "check", L("挑战类型", "Challenge types"), L("标明谁主谁辅。", "Mark which leads."), options=opts(("react", "敏捷反应", "Reaction"), ("muscle", "肌肉记忆", "Muscle memory"), ("parse", "复杂信息筛选", "Signal from noise"), ("knowledge", "掌握复杂知识", "Dense knowledge"), ("optimize", "完全信息求优", "Full-info optimum"), ("hidden", "不完全信息判断", "Hidden information"), ("multi", "多方博弈与心理", "Multi-party mind games"))),
                field("opDetail", "textarea", L("操作层设计要点", "Operation notes"), L("反应、记忆、意识各占多少。", "Share of reaction, memory and read.")),
                field("stratDetail", "textarea", L("策略层设计要点", "Strategy notes"), L("知识量、计算深度、隐藏信息与心理战。", "Knowledge, calculation, fog and psychology.")),
                field("dynamicsPve", "textarea", L("人机互动", "Player–system dynamics"), L("与系统反复发生的互动。", "Repeating player-to-system exchange.")),
                field("dynamicsPvp", "textarea", L("人际互动", "Player–player dynamics"), L("合作、对抗或误导。", "Cooperation, contest or deception.")),
                field("ruleTrade", "textarea", L("规则冲突与取舍", "Rule trade-offs"), L("为保住主体验准备放弃什么。", "What you drop to protect the main feeling.")),
                field("nonlinear", "radio", L("情绪结构", "Emotion structure"), L("完全可预期会让熟手疲劳。", "A fully expected slope tires veterans."), options=opts(("linear", "线性可预期", "Linear expected"), ("broken", "打破预期的峰谷", "Broken-expectation peaks"), ("mixed", "宏观可预期、微观突发", "Predictable macro, sudden micro"))),
                field("rhythmNote", "textarea", L("战斗或对局节奏", "Session rhythm"), L("波峰间距、振幅与随机源。", "Peak spacing, amplitude and randomness.")),
            ],
        },
        {
            "id": "loops",
            "no": "07",
            "title": L("循环玩法", "Play loops"),
            "lead": L("闭环回答：此刻、今晚、明天、本周为什么还要继续。", "Why they continue now, tonight, tomorrow and this week."),
            "fields": [
                field("coreLoop", "textarea", L("核心循环（分钟级）", "Core loop (minutes)"), L("输入、判定、反馈、再进入。", "Input, resolve, feedback, re-enter.")),
                field("coreSeconds", "number", L("核心循环时长（秒）", "Core loop seconds"), L("一次微循环大约多少秒。", "Seconds for one micro cycle.")),
                field("sessionLoop", "textarea", L("对局循环（小时级）", "Session loop"), L("一次登录内微循环如何被目标串起。", "How micro cycles are strung by a session goal.")),
                field("dailyLoop", "textarea", L("日循环", "Daily loop"), L("每天打开的理由。", "Why they open today.")),
                field("weeklyLoop", "textarea", L("周循环", "Weekly loop"), L("周常、段位、社团或内容节奏。", "Weeklies, rank, group duty or cadence.")),
                field("seasonLoop", "textarea", L("赛季或版本循环", "Season loop"), L("更长尺度的目标切换。", "Longer goal rotation.")),
                field("socialLoop", "textarea", L("社交循环", "Social loop"), L("邀请、分工、围观、对抗如何拉回。", "Invite, role-split, spectate or rivalry.")),
                field("failRecover", "textarea", L("失败后如何再进入", "Failure re-entry"), L("失败必须指向下一钩。", "Failure must offer a next hook.")),
                field("tomorrowHook", "text", L("明天回来的一句理由", "Tomorrow hook"), L("离开时必须能被一句说清。", "Must be sayable in one sentence at exit.")),
                field("loopClosed", "radio", L("是否形成闭环", "Loop closed?"), L("产出是否被下一环消耗。", "Does output feed the next sink?"), options=opts(("yes", "闭环", "Closed"), ("partial", "半开，靠运营补", "Partial, ops must patch"), ("no", "尚未闭环", "Not closed"))),
                field("loopRisk", "textarea", L("循环断裂点", "Break points"), L("哪一步会觉得没有下一步。", "Where a player feels there is no next step.")),
            ],
        },
        {
            "id": "addiction",
            "no": "08",
            "title": L("上瘾与召回", "Habit and recall"),
            "lead": L("分别设计未打开时想起，与打开后难以停手，并写下克制边界。", "Design offline recall and in-session pull separately, then write the limits."),
            "fields": [
                field("offlineRecall", "check", L("未打开时如何被想起", "Offline recall"), L("不在游戏里时，哪一条线索把注意拉回。", "Which cue pulls attention elsewhere."), options=opts(("unfinished", "未完成事项残留", "Unfinished task residue"), ("appointment", "定时赴约", "Timed appointment"), ("social_ping", "熟人召唤或责任", "Social summons"), ("almost", "收集只差一件", "One short of a set"), ("cliff", "叙事或对局悬置", "Cliffhanger"), ("window", "限时窗口即将关闭", "Closing window"), ("status_drop", "地位可能下滑", "Status may drop"))),
                field("offlineCopy", "textarea", L("离线召回话术或信号", "Recall signal"), L("只写机制，不写具体渠道品牌。", "Mechanism only, no vendor brands.")),
                field("sessionPull", "check", L("对局内难以停手", "In-session pull"), L("让一次会话自我延长的结构。", "Structures that extend a sitting."), options=opts(("variable", "不确定比例奖励", "Variable-ratio reward"), ("near_miss", "差一点就成", "Near miss"), ("streak", "连胜或连击保护", "Streak protection"), ("short_clear", "短周期可清空", "Short clearable cycle"), ("next_visible", "下一奖始终可见", "Next prize always visible"), ("peak_end", "结束时给高峰回味", "Peak-end recap"), ("just_one", "再来一局的低摩擦", "Low-friction one more"))),
                field("dayOccupy", "check", L("如何占满一天", "Day-long occupancy"), L("把人留在生态里。", "Keep them in the ecology."), options=opts(("layers", "多层并行目标", "Stacked parallel goals"), ("energy", "体力或次数门", "Energy or attempt gates"), ("tracks", "多条养成轨道", "Several growth tracks"), ("calendar", "日历型稀缺", "Calendar scarcity"), ("duty", "组织职务", "Org duty"), ("season_meta", "赛季总账", "Season ledger"))),
                field("sessionLength", "radio", L("设计会话时长", "Designed session"), L("时长决定刺激密度。", "Length sets stimulus density."), options=opts(("micro", "八分钟内可完整", "Complete within eight minutes"), ("standard", "二十五分钟一节", "Twenty-five minute sit"), ("long", "一小时沉浸", "Hour immersion"), ("open", "不设上限", "No cap"))),
                field("intensity", "range", L("刺激强度（1–5）", "Stimulus intensity"), L("不是越大越好。", "Higher is not better."), min=1, max=5),
                field("nearMissNote", "textarea", L("差一点就成的设计", "Near-miss design"), L("失败仍指向下一次尝试。", "Failure should point to the next try.")),
                field("ethicalCap", "check", L("克制边界", "Limits"), L("写进文档的禁止项。", "Documented refusals."), options=opts(("no_pay_undo", "不允许付费撤销关键失败", "No pay-to-undo key failure"), ("show_odds", "随机必须可被理解", "Odds must be intelligible"), ("cap_nudge", "限制离线催促频率", "Cap offline nudges"), ("sleep_gate", "深夜降低召回强度", "Soften late-night recall"), ("kid_off", "不面向未成年人强化", "No minor-targeted intensification"))),
                field("habitRisk", "textarea", L("上瘾机制风险", "Habit risks"), L("哪一条可能伤害品牌或监管。", "Which hook may harm brand or compliance.")),
            ],
        },
        {
            "id": "systems",
            "no": "09",
            "title": L("系统架构", "System architecture"),
            "lead": L("框架等于模块及其关系。", "A framework is modules plus relations."),
            "fields": [
                field("infra", "check", L("基建系统", "Infrastructure"), L("没有则无法运行。", "Without this the product cannot run."), options=opts(("account", "账号与登录", "Account"), ("settings", "设置", "Settings"), ("mail", "邮件", "Mail"), ("social_base", "好友与聊天", "Friends and chat"), ("anti_cheat", "公平与风控", "Fair-play controls"), ("cloud_save", "云存档", "Cloud save"))),
                field("playSupport", "check", L("服务玩法的系统", "Play-support systems"), L("逻辑从玩法衍生。", "Derived from play."), options=opts(("match", "匹配", "Matchmaking"), ("room", "房间与大厅", "Rooms"), ("spectate", "观战", "Spectate"), ("replay", "回放", "Replay"), ("rank", "段位", "Rank"), ("training", "训练场", "Training"))),
                field("ecoSupport", "check", L("服务商业化的系统", "Commerce-support systems"), L("投放资产的管道。", "Pipes for selling assets."), options=opts(("pass", "战令式投放", "Season pass"), ("shop", "商店", "Shop"), ("gacha", "随机获取", "Random grant"), ("bp_track", "付费层级轨道", "Spender tracks"))),
                field("loopSupport", "textarea", L("服务循环的系统组合", "Loop-support assembly"), L("先写期望行为，再挑选组件。", "Write desired behaviour, then pick components.")),
                field("opsEco", "check", L("外部生态", "External ecology"), L("软件之外仍与玩家相连的层。", "Outside the binary, still touching players."), options=opts(("watch", "直播与观赛", "Broadcast"), ("forum", "论坛与社群", "Forum and community"), ("creator", "二创与视频", "Creator video"), ("event", "线下或线上赛事", "Events"))),
                field("socNote", "textarea", L("群体如何自组织", "How groups self-organise"), L("个体—互动—组织—文化。", "Person, interaction, organisation, culture.")),
            ],
        },
        {
            "id": "numerics",
            "no": "10",
            "title": L("数值体系", "Numeric systems"),
            "lead": L("按成长、战斗、经济、社会、投放五层分别建模。", "Model growth, combat, economy, social and grant layers."),
            "subs": [
                {"id": "n-growth", "no": "10-1", "title": L("成长数值", "Growth numbers"), "fields": [
                    field("levelCap", "number", L("等级或阶段上限", "Level cap"), L("可见成长的终点。", "Visible end of growth.")),
                    field("xpCurve", "radio", L("经验曲线", "XP curve"), L("前期过快会让后期无事可做。", "Too fast early leaves the late game empty."), options=CURVE),
                    field("powerCurve", "radio", L("战力或效率曲线", "Power curve"), L("变强的体感落在哪一段。", "Where getting stronger actually sits."), options=CURVE),
                    field("gateStyle", "radio", L("突破方式", "Gate style"), L("台阶制造仪式，连续更平滑。", "Steps create ritual; curves feel smooth."), options=opts(("soft", "连续平滑", "Continuous"), ("hard", "硬门槛突破", "Hard gates"), ("dual", "平滑为主、关键台阶", "Smooth with key gates"))),
                    field("growthNote", "textarea", L("成长设计说明", "Growth note"), L("成长服务掌握、身份还是比较。", "Mastery, identity or comparison."),),
                ]},
                {"id": "n-combat", "no": "10-2", "title": L("战斗数值", "Combat numbers"), "fields": [
                    field("ttk", "radio", L("击倒时长定位", "Time-to-down"), L("决定操作窗口与刺激密度。", "Sets input window and spike density."), options=opts(("instant", "瞬间", "Instant"), ("short", "短", "Short"), ("medium", "中", "Medium"), ("long", "长", "Long"))),
                    field("attrSet", "check", L("基础属性集", "Base attributes"), L("只保留玩法能读到的属性。", "Keep only attributes the play can read."), options=opts(("hp", "生命", "Health"), ("atk", "攻击", "Attack"), ("def", "防御", "Defense"), ("spd", "速度", "Speed"), ("crit", "暴击", "Crit"), ("acc", "命中与规避", "Hit / evade"))),
                    field("skillScale", "text", L("技能倍率原则", "Skill scaling rule"), L("一句话约束所有技能数值。", "One sentence that binds every skill number.")),
                    field("infoLoad", "radio", L("战场信息负荷", "Battlefield info load"), L("过载时乐趣来自筛选。", "When overloaded, fun is filtering."), options=opts(("low", "低，信息清晰", "Low, readable"), ("mid", "中，需观察", "Mid, must watch"), ("high", "高，需筛选", "High, must filter"))),
                    field("combatNote", "textarea", L("战斗数值说明", "Combat note"), L("与节奏、非线性如何互证。", "How this supports rhythm and peaks.")),
                ]},
                {"id": "n-econ", "no": "10-3", "title": L("经济数值", "Economy numbers"), "fields": [
                    field("sources", "textarea", L("产出源", "Sources"), L("谁在什么行为下产生资源。", "Which action creates which resource.")),
                    field("sinks", "textarea", L("消耗汇", "Sinks"), L("没有去处就会通胀。", "Resources need sinks or they inflate.")),
                    field("dailyCap", "text", L("日产出上限原则", "Daily cap rule"), L("上限保护长线，也会切断上瘾会话。", "Caps protect the long run and cut compulsive sits.")),
                    field("dropFeel", "radio", L("掉落体感", "Drop feel"), L("前期给满后期枯竭会迅速无聊。", "Front-loaded drops bore later."), options=opts(("front", "前期高、后期干", "High early, dry late"), ("tail", "前期收敛、后期仍有峰值", "Tight early, late tail"), ("flat", "全程平稳", "Flat"))),
                    field("econNote", "textarea", L("经济说明", "Economy note"), L("经济必须服务循环。", "Economy must serve the loop.")),
                ]},
                {"id": "n-social", "no": "10-4", "title": L("社会数值", "Social numbers"), "fields": [
                    field("rankDecay", "radio", L("段位或声望衰减", "Rank decay"), L("衰减制造召回，也会制造焦虑。", "Decay recalls and also creates anxiety."), options=opts(("none", "不衰减", "None"), ("slow", "缓衰减", "Slow"), ("season_reset", "赛季重置", "Season reset"))),
                    field("repSink", "text", L("贡献如何被看见", "How contribution is seen"), L("看不见的贡献不驱动组织。", "Invisible contribution does not drive an organisation.")),
                    field("ladderCap", "text", L("排行暴露范围", "Ladder exposure"), L("全服榜与好友榜刺激不同。", "Global and friend boards differ.")),
                    field("socialNumNote", "textarea", L("社会数值说明", "Social numbers note"), L("数字只是可见杠杆。", "Numbers are only visible levers.")),
                ]},
                {"id": "n-grant", "no": "10-5", "title": L("投放数值", "Grant numbers"), "fields": [
                    field("priceBands", "textarea", L("付费层级与卖什么", "Price bands and goods"), L("不同层级分别买到何种资产。", "What each spend band receives.")),
                    field("pity", "radio", L("保底", "Pity"), L("降低愤怒，也降低峰值。", "Lowers rage and also peak spike."), options=opts(("none", "无保底", "None"), ("soft", "软保底", "Soft"), ("hard", "硬保底", "Hard"))),
                    field("oddsVisible", "radio", L("概率可见性", "Odds visibility"), L("可见概率是信任。", "Visible odds are trust."), options=opts(("hidden", "不展示", "Hidden"), ("summary", "展示摘要", "Summary"), ("full", "完整展示", "Full"))),
                    field("grantCadence", "text", L("投放频率原则", "Grant cadence"), L("固定基础与动态活动如何分工。", "Baseline versus event grants.")),
                    field("grantNote", "textarea", L("投放说明", "Grant note"), L("对准玩家核心追求对应的资产价值。", "Map grants to the value players chase.")),
                ]},
            ],
        },
        {
            "id": "monetization",
            "no": "11",
            "title": L("商业化", "Monetization"),
            "lead": L("商业化从情绪出发：变强、展示、便利或收藏。", "Commerce starts from emotion: power, display, convenience or collection."),
            "fields": [
                field("payEmotion", "check", L("付费对应的情绪", "Emotions that pay"), L("资产价值必须对上核心追求。", "Asset value must match the pursuit."), options=opts(("power", "变强", "Power"), ("show", "展示", "Display"), ("conv", "省时便利", "Convenience"), ("collect", "收集完整", "Completion"), ("gift", "赠礼与社交", "Gifting"))),
                field("assetTypes", "textarea", L("可售资产类型与品质", "Sellable assets"), L("有哪些资产、如何分品质。", "Which assets, and how quality is tiered.")),
                field("spenderLadder", "textarea", L("付费层级诱导", "Spender ladder"), L("如何让人升层。", "How a player climbs bands.")),
                field("delivery", "textarea", L("投放方式", "Delivery"), L("商店、战令、活动、随机如何配比。", "Mix of shop, pass, event and random grant.")),
                field("liveCadence", "textarea", L("版本中的资产释放", "Release over versions"), L("长线如何放出新资产或新管道。", "How new assets or pipes appear over versions.")),
            ],
        },
        {
            "id": "ops",
            "no": "12",
            "title": L("运营、版本与验证", "Ops, versions, proof"),
            "lead": L("研运一体。用数据与深访验证，而不是“我觉得”。", "Research and ops are one. Prove with data and interviews."),
            "fields": [
                field("verContent", "check", L("版本应包含", "Version should contain"), L("服务型产品靠版本活着。", "A live product lives on versions."), options=opts(("infra", "基建修补", "Infra fixes"), ("play", "玩法增量", "Play increment"), ("shop_sys", "商业化系统", "Commerce systems"), ("core_loop", "核心循环系统", "Core-loop systems"), ("edge", "边缘系统", "Edge systems"), ("event", "活动", "Events"), ("grant", "资源投放", "Resource grants"))),
                field("sellPoint", "text", L("本版本对外卖点", "Public selling point"), L("宣发只说核心内容。", "Public talk is the core content.")),
                field("acqCheap", "textarea", L("持续低成本获客", "Cheap ongoing acquisition"), L("品牌与内容如何自我扩散。", "How brand and content spread themselves.")),
                field("proof", "check", L("验证手段", "Proof methods"), L("策划忌“我认为”。", "Avoid “I feel”."), options=opts(("data", "行为数据", "Behaviour data"), ("talk", "一对一深访", "One-to-one interviews"), ("survey", "问卷辅助", "Survey assist"), ("self", "设计者深玩", "Designer deep-play"))),
                field("playerVoice", "textarea", L("如何解读玩家表述", "How to read player talk"), L("表层可能荒唐，内在需求通常成立。", "The surface line may be nonsense; the need usually holds.")),
                field("mainContradiction", "textarea", L("当前主要矛盾", "Present contradiction"), L("抓住当下真正卡住的那一层。", "Name the layer that is actually stuck now.")),
            ],
        },
        {
            "id": "export",
            "no": "13",
            "title": L("汇总与导出", "Review and export"),
            "lead": L("检查各步是否自洽，然后按步或整份导出。", "Check consistency, then export a step or the whole brief."),
            "fields": [
                field("readyNote", "textarea", L("交付前自检", "Pre-flight note"), L("框架、方案、循环、数值与上瘾是否互相支持。", "Whether frame, plan, loop, numbers and habit support each other.")),
            ],
        },
    ]


GAME_STEPS = [MODE_STEP, CHARTER_STEP] + _game_body()


def _bp_body():
    steps = [
        ("bp_problem", L("市场空白", "The gap"), L("用几句话说明空白或问题及其严重程度。", "A few sentences on the gap and how bad it is."), [
            field("bpGap", "textarea", L("空白或问题", "Gap or problem"), L("一句话说清也可以。", "One sentence can suffice."), required=True),
            field("bpSeverity", "radio", L("严重程度", "Severity"), L("有多痛、有多普遍。", "How painful and how common."), options=opts(("niche", "小而真", "Small but real"), ("wide", "普遍存在", "Widespread"), ("acute", "已造成明确损失", "Already costing clearly"))),
        ]),
        ("bp_solution", L("解决方案", "Solution"), L("产品是什么，提供哪些功能。", "What the product is and which functions it offers."), [
            field("bpProduct", "textarea", L("产品与功能", "Product and functions"), L("写功能边界，不写愿景散文。", "Functions and bounds, not vision prose.")),
            field("bpHow", "textarea", L("如何解决问题", "How it solves"), L("从问题到功能的对应。", "Map problem to function.")),
        ]),
        ("bp_users", L("用户群", "Users"), L("必须划分用户群。", "Segments are mandatory."), [
            field("bpSegPrimary", "text", L("核心用户", "Core segment"), L("最先服务谁。", "Whom you serve first.")),
            field("bpSegMore", "textarea", L("其他分层", "Other segments"), L("付费层、意见层、规模层分开写。", "Separate spenders, voices and scale.")),
        ]),
        ("bp_moat", L("竞争力", "Advantage"), L("关键不在事情大小，而在能否做得更好或不同。", "Size of the prize matters less than better or different doing."), [
            field("bpWhyUs", "textarea", L("为何是你", "Why you"), L("别人做不到或做不好的具体原因。", "The concrete reason others cannot do this as well.")),
            field("bpUnlike", "text", L("与众不同的一点", "The unlike point"), L("只要有一点更亮即可。", "One brighter point is enough.")),
        ]),
        ("bp_market", L("市场前景", "Market future"), L("论证规模与走向，保持克制。", "Argue scale and direction with restraint."), [
            field("bpSize", "textarea", L("市场有多大", "How large"), L("用自己的口径，并写清口径。", "State the yardstick you are using.")),
            field("bpFuture", "textarea", L("未来怎么走", "Where it goes"), L("结构变化，而不是口号式增长。", "Structural change, not slogan growth.")),
        ]),
        ("bp_revenue", L("如何挣钱", "How it earns"), L("说不清可以承认，转而证明用户与价值。", "If unclear, say so, and prove users and value instead."), [
            field("bpKnowPay", "radio", L("变现是否已想清", "Revenue clarity"), L("诚实比虚假的三年预测更有用。", "Honesty beats a fake three-year forecast."), options=opts(("clear", "已有路径", "Path exists"), ("hypothesis", "有假说待验证", "Hypothesis"), ("unknown", "尚不清楚，先看使用规模", "Unknown; usage first"))),
            field("bpPayPath", "textarea", L("路径或价值陈述", "Path or value"), L("若不知如何挣钱，写清谁会用、为何有价值。", "If unknown, write who will use it and why it is valuable.")),
        ]),
        ("bp_compete", L("竞争格局", "Competition"), L("禁止“前无古人”。有人在做并不可怕。", "Do not claim there is no precedent."), [
            field("bpRivals", "textarea", L("谁在做、做得怎样", "Who else, and how well"), L("客观描述。", "Describe plainly.")),
            field("bpCompare", "textarea", L("优劣对照", "Contrast"), L("简单对照即可。", "A short contrast.")),
        ]),
        ("bp_highlights", L("亮点", "Bright points"), L("新产品必有缺陷。一处相对优势写透即可。", "New products are flawed. One relative strength is enough."), [
            field("bpShine", "textarea", L("最亮的一点", "The brightest point"), L("写可被验证的优点。", "A verifiable strength.")),
            field("bpKnownGap", "textarea", L("已知缺陷", "Known gaps"), L("主动写出缺陷。", "Name them before you are asked.")),
        ]),
        ("bp_budget", L("资金用途", "Use of funds"), L("只写未来六到十二个月要多少、用在何处。", "Six to twelve months: how much and on what."), [
            field("bpHorizon", "radio", L("预算窗口", "Horizon"), L("窗口越短越可信。", "Shorter is more believable."), options=opts(("m6", "六个月", "Six months"), ("m12", "十二个月", "Twelve months"))),
            field("bpNeed", "text", L("需要的资金", "Capital needed"), L("一个数字加币种即可。", "One number and a currency.")),
            field("bpUse", "textarea", L("钱用在何处", "Where it goes"), L("按事项拆。", "Split by task.")),
        ]),
        ("bp_team", L("团队", "Team"), L("写做过什么，而不是头衔。", "Write what they shipped, not titles."), [
            field("bpPeople", "textarea", L("成员与做过的事", "People and shipped work"), L("优秀之处必须可核对。", "Strengths must be checkable.")),
        ]),
        ("export", L("汇总与导出", "Review and export"), L("十项齐了就是一份可用的计划书。", "The ten parts make a usable plan."), [
            field("readyNote", "textarea", L("交付前自检", "Pre-flight note"), L("空白、方案、用户、竞争力与用钱是否能被一页说完。", "Whether gap, plan, users, edge and spend fit on one page.")),
        ]),
    ]
    out = []
    for i, (sid, title, lead, fields) in enumerate(steps, start=3):
        out.append({"id": sid, "no": f"{i:02d}", "title": title, "lead": lead, "fields": fields})
    return out


BP_STEPS = [MODE_STEP, CHARTER_STEP] + _bp_body()


def _pack(**kwargs):
    return kwargs


PRESETS = {
    "asymmetric_social": _pack(
        orientation="product", platforms=["mobile", "pc"], playShape="session",
        gap="短局多人里缺少低门槛、高讨论密度的身份对抗。熟人局有需求，现有供给要么过重要么过吵。",
        severity="clear", audience="25–40 岁熟人局组织者；轻度策略爱好者；内容创作者。",
        needPrimary="在一轮讨论里识破或隐瞒身份", needSecondary="低组织成本的再开一局",
        whyNow="语音与房间工具已经足够便宜，短内容传播让揭晓瞬间更有传播力。",
        selfFit="擅长社交规则与短局节奏，不依赖重资产射击手感。",
        controlPoint="讨论规则与身份信息差，而不是贴图量。",
        positioning="八至十五分钟可完整结束的身份对抗。",
        milestone="内测先验证‘揭晓是否被复述’；再验证‘再来一局率’。",
        acqBet="熟人拉人与揭晓切片，而不是买量开局。",
        shortStay="一局结束立刻给下一局身份重洗。", longStay="赛季身份图鉴与固定主持人职责。",
        payBet="展示身份外观与赠礼，不卖结果。",
        feelPrimary="识破与被识破的紧张", feelList=["deduce", "social", "tension"],
        feelOrder="推理第一，同场第二，紧张第三。不靠惊吓。",
        identityPlay="隐藏阵营中的普通成员或关键身份", emotionOnce="第一次被全桌指认",
        instinct=["lonely"], challengeMode=["hidden", "multi", "parse"],
        opDetail="操作负担低，窗口给发言与观察。",
        stratDetail="不完全信息 + 多方发言博弈。",
        dynamicsPve="系统只发身份与阶段时钟。", dynamicsPvp="发言、投票、私下结盟。",
        ruleTrade="放弃复杂技能树，保住讨论密度。", nonlinear="broken",
        rhythmNote="夜晚行动短、白天讨论长，揭晓制造单峰。",
        coreLoop="组局 → 隐藏身份行动 → 公开讨论与投票 → 揭晓 → 立刻再开",
        coreSeconds=90, sessionLoop="三至五局构成一次聚会。",
        dailyLoop="熟人缺人时的一条召唤。", weeklyLoop="周主题身份。",
        seasonLoop="赛季图鉴与主持人头衔。", socialLoop="房主拉人，败者指定下一局身份。",
        failRecover="失败方先选下一局规则。", tomorrowHook="熟人局还缺一个位置",
        loopClosed="yes", loopRisk="没熟人时匹配冷场。",
        offlineRecall=["social_ping", "unfinished", "cliff"],
        offlineCopy="房间还开着，缺你一张票。",
        sessionPull=["just_one", "peak_end", "variable"],
        dayOccupy=["duty", "calendar"], sessionLength="standard", intensity=3,
        nearMissNote="投错人后立刻看到本可成立的线索。",
        ethicalCap=["no_pay_undo", "cap_nudge", "kid_off"],
        habitRisk="社交债务过重会把房主累垮。",
        infra=["account", "settings", "social_base"],
        playSupport=["room", "spectate"], ecoSupport=["shop"],
        loopSupport="房间、身份发放、讨论钟、结算卡、再开按钮。",
        opsEco=["watch", "creator"],
        socNote="自然形成房主—常客—路人三层。设计应保护房主。",
        levelCap=1, xpCurve="linear", powerCurve="linear", gateStyle="soft",
        growthNote="成长主要在身份图鉴而非数值碾压。",
        ttk="instant", attrSet=[], skillScale="不使用战斗倍率。", infoLoad="mid",
        combatNote="对抗发生在发言，不在血条。",
        sources="对局次数、赛季任务。", sinks="外观与房间装饰。",
        dailyCap="每日匹配奖励收敛，熟人局不限。", dropFeel="flat",
        econNote="经济几乎不影响胜负。",
        rankDecay="none", repSink="主持场次被房间成员看见。", ladderCap="只做好友局战绩。",
        socialNumNote="不设全服压迫榜。",
        priceBands="低价身份外观；中价房间主题；高价主持套装。",
        pity="none", oddsVisible="full", grantCadence="赛季商店为主，活动为辅。",
        grantNote="不卖结果，只卖展示与仪式。",
        payEmotion=["show", "gift"], assetTypes="身份外观、语音、房间主题。",
        spenderLadder="用成套主题诱导，而不是用胜率。",
        delivery="商店直购为主。", liveCadence="每季六个新身份，两个房间主题。",
        verContent=["play", "event"], sellPoint="这一季的新身份怎么骗人",
        acqCheap="揭晓切片与房主工具。", proof=["talk", "self", "data"],
        playerVoice="玩家会说‘匹配好蠢’，真实需求往往是‘我要熟人’。",
        mainContradiction="冷启动时没有房主。",
    ),
}


def _clone_preset(base_id: str, **overlay):
    row = dict(PRESETS[base_id])
    row.update(overlay)
    return row


def _fill_rest():
    # additional presets cloned then specialised
    extra = {
        "squad_tactical": dict(
            orientation="product", platforms=["pc", "console"], playShape="session",
            gap="小队射击里缺少‘短准备+高配合撤离’的清晰循环，很多对局停在无目标对枪。",
            severity="clear", audience="已有射击手感的四人小队；晚间两小时用户。",
            needPrimary="四人生死与分工被同一目标绑住", needSecondary="失败后十分钟内能再挑战",
            whyNow="语音与反作弊基建已够用，缺的是目标结构而不是枪感。",
            selfFit="关卡脚本与音效节奏经验强于大世界生产。",
            controlPoint="目标区的信息设计与撤离规则。",
            positioning="二十五分钟可完成的小队任务射击。",
            milestone="先验证撤离时的配合呼喊是否自然出现。",
            acqBet="小队邀请链接与任务失败切片。",
            shortStay="失败回放指出下一次该换的分工。", longStay="每周轮换目标区与装备契约。",
            payBet="展示与便利，不卖直接胜负。",
            feelPrimary="压境时的配合紧张", feelList=["tension", "flow", "social"],
            feelOrder="紧张第一，手感第二，小队第三。",
            identityPlay="突击 / 支援 / 侦察中的一个职位", emotionOnce="第一次在撤离点互相掩护",
            instinct=["lonely"], challengeMode=["react", "muscle", "parse"],
            opDetail="反应与预瞄为主，信息负荷中等。", stratDetail="负荷与入口选择是策略层。",
            dynamicsPve="目标物、警报、增援波次。", dynamicsPvp="可选的入侵或纯合作。",
            ruleTrade="放弃大战场载具，保住四人可读性。", nonlinear="mixed",
            rhythmNote="渗透安静，目标区突然变密，撤离再抬一峰。",
            coreLoop="准备负荷 → 进入目标区 → 交火与配合 → 撤离或失败复盘",
            coreSeconds=40, sessionLoop="两至三张任务图构成一晚。",
            dailyLoop="每日契约任务。", weeklyLoop="周轮换图与装备限制。",
            seasonLoop="新目标区与战术道具。", socialLoop="固定四人缺人时的候补位。",
            failRecover="失败回放标出被打断的分工。", tomorrowHook="今晚公会约了两张图",
            loopClosed="yes", loopRisk="匹配到无语音队友会断循环。",
            offlineRecall=["appointment", "status_drop", "social_ping"],
            offlineCopy="约定的图还差一名支援。",
            sessionPull=["streak", "just_one", "peak_end"],
            dayOccupy=["duty", "calendar", "season_meta"], sessionLength="standard", intensity=4,
            nearMissNote="撤离进度 90% 被打断，下一局保留部分侦察信息。",
            ethicalCap=["no_pay_undo", "show_odds", "cap_nudge"],
            habitRisk="夜间加赛容易超时，需会话软结束。",
            infra=["account", "settings", "anti_cheat", "social_base"],
            playSupport=["match", "room", "replay", "training"], ecoSupport=["shop", "pass"],
            loopSupport="房间准备、负荷检查、目标脚本、撤离结算、回放。",
            opsEco=["watch", "event"], socNote="小队会固化角色，系统设计应允许轮换职位。",
            levelCap=30, xpCurve="ease_out", powerCurve="s_curve", gateStyle="dual",
            growthNote="成长在道具熟练度，不在血量膨胀。",
            ttk="short", attrSet=["hp"], skillScale="战术道具不改变基础射击模型。", infoLoad="mid",
            combatNote="短 TTK 服务紧张，不服务数值堆叠。",
            sources="任务完成、周契约。", sinks="战术皮肤、武器检视。",
            dailyCap="日任务经验有顶。", dropFeel="tail", econNote="经济不进入对局内强度。",
            rankDecay="slow", repSink="职位完成数在小队面板可见。", ladderCap="小队榜优先于全服。",
            socialNumNote="全服榜只作观赏。",
            priceBands="武器皮肤低中高三档；通行证中档。",
            pity="none", oddsVisible="full", grantCadence="赛季通行证 + 周商店。",
            grantNote="展示为主。", payEmotion=["show", "conv"],
            assetTypes="枪皮、角色制服、呼号。", spenderLadder="套装收集而非单件爆款。",
            delivery="直购加通行证。", liveCadence="每季一新区，两件战术道具。",
            verContent=["play", "core_loop", "event"], sellPoint="新目标区的撤离规则",
            acqCheap="失败撤离的短视频。", proof=["data", "self", "talk"],
            playerVoice="会说‘匹配不公平’，真实需求是‘我要固定队’。",
            mainContradiction="单排体验与四人设计冲突。",
        ),
    }
    PRESETS.update(extra)


_fill_rest()


def _dense_from_template(genre_id: str, title_zh: str, hook: str, feel, challenges, loop, extra=None):
    row = dict(
        orientation="product",
        platforms=["pc", "mobile"],
        playShape="session",
        gap=f"{title_zh}品类里，现有供给没有把‘{hook}’写成可重复的闭环。",
        severity="clear",
        audience="愿意为该体验每周给出两至三晚的玩家；以及组织他们的小团长。",
        needPrimary=hook,
        needSecondary="失败后仍能指出下一步",
        whyNow="分发与语音成本下降，缺的是结构而不是画面。",
        selfFit="对节奏与系统循环的判断比对大制作产能更有把握。",
        controlPoint="把该体验写成可验证的循环，而不是功能清单。",
        positioning=title_zh + "中强调闭环与可复述高潮的一档。",
        milestone="先验证高潮能否被玩家用一句话转述。",
        acqBet="高潮切片与房间邀请。",
        shortStay="结算页给出下一钩。",
        longStay="周目标与赛季总账。",
        payBet="展示与便利优先于直接强度。",
        feelPrimary=hook,
        feelList=feel,
        feelOrder="主体验不可让步，其余按场景加减。",
        identityPlay="与该品类匹配的可扮演身份",
        emotionOnce="第一次完整走完闭环时的高峰",
        instinct=["lonely"] if "social" in feel else ["instant"],
        challengeMode=challenges,
        opDetail="按挑战类型分配反应、记忆与读场。",
        stratDetail="策略层服务主体验，不另开第二套游戏。",
        dynamicsPve="系统给出目标、时钟与反馈。",
        dynamicsPvp="若有多人，则分工或对抗必须可读。",
        ruleTrade="删掉一切不服务主体验的规则。",
        nonlinear="mixed",
        rhythmNote="微观可突发，宏观仍能被组织者预期。",
        coreLoop=loop,
        coreSeconds=45,
        sessionLoop="数次微循环叠成一次可结束的会话。",
        dailyLoop="每日一钩：未完成、赴约或重置。",
        weeklyLoop="周常与组织义务。",
        seasonLoop="赛季切换目标，避免日循环耗尽。",
        socialLoop="邀请与责任把人拉回。",
        failRecover="失败结算指向可执行的下一试。",
        tomorrowHook=hook + "还差一次完整验证",
        loopClosed="partial",
        loopRisk="高潮之后没有下一目标。",
        offlineRecall=["unfinished", "appointment", "almost"],
        offlineCopy="上一环还没闭合。",
        sessionPull=["next_visible", "just_one", "peak_end"],
        dayOccupy=["layers", "calendar"],
        sessionLength="standard",
        intensity=3,
        nearMissNote="接近成功时留下可读的差距，而不是惩罚。",
        ethicalCap=["no_pay_undo", "cap_nudge", "show_odds", "kid_off"],
        habitRisk="召回过密会伤害品牌。",
        infra=["account", "settings"],
        playSupport=["match"] if "social" in feel else ["training"],
        ecoSupport=["shop"],
        loopSupport="目标生成、过程反馈、结算、再进入。",
        opsEco=["creator"],
        socNote="玩家会自发分层；设计只诱导方向。",
        levelCap=40,
        xpCurve="s_curve",
        powerCurve="ease_out",
        gateStyle="dual",
        growthNote="成长服务掌握，避免前期送满。",
        ttk="medium",
        attrSet=["hp", "atk"],
        skillScale="技能只放大主体验所需的那一种判断。",
        infoLoad="mid",
        combatNote="数值服从节奏。",
        sources="对局、日目标、周目标。",
        sinks="外观、便利、赛季通行证。",
        dailyCap="日产出有顶，周目标负责波动。",
        dropFeel="tail",
        econNote="经济不另开玩法。",
        rankDecay="slow",
        repSink="贡献在小团体内可见。",
        ladderCap="好友与小队优先。",
        socialNumNote="全服榜不作日常压力。",
        priceBands="低价便利；中价展示；高价成套主题。",
        pity="soft",
        oddsVisible="summary",
        grantCadence="固定日给底，活动给峰值。",
        grantNote="资产对准展示或便利。",
        payEmotion=["show", "conv"],
        assetTypes="外观、通行证、便利道具。",
        spenderLadder="成套诱导，避免只服务顶层。",
        delivery="商店 + 战令 + 活动。",
        liveCadence="按版本放出新目标与新外观管线。",
        verContent=["play", "core_loop", "event"],
        sellPoint=hook,
        acqCheap="可转述的高潮片段。",
        proof=["data", "self", "talk"],
        playerVoice="表层抱怨功能，内层往往是循环断了。",
        mainContradiction="高潮密度与长线稳定之间的冲突。",
    )
    if extra:
        row.update(extra)
    PRESETS[genre_id] = row


_TEMPLATES = [
    ("objective_team", "团队目标争夺", "把一条共同目标守住或推完", ["social", "mastery", "flow"], ["parse", "react", "optimize"], "选职 → 推进目标 → 团战结算 → 下一目标"),
    ("infil_defense", "建筑潜入与据守", "在信息差里完成一次潜入或守住", ["tension", "deduce", "mastery"], ["parse", "hidden", "knowledge"], "部署路线 → 潜入或据守 → 信息差爆发 → 残局"),
    ("extraction_survival", "撤离生存对抗", "带出战利品而不是死在加注上", ["tension", "wonder", "status"], ["parse", "hidden", "react"], "进入地图 → 搜刮与遭遇 → 抉择撤离或加注 → 带出或归零"),
    ("lane_arena", "分路竞技对战", "在一条路与一次团战里证明读场", ["mastery", "flow", "status"], ["parse", "react", "muscle", "knowledge"], "选角 → 对线发育 → 目标团战 → 结束结算"),
    ("deck_roguelike", "卡组构筑冒险", "用这一趟的构筑打通未知的下一层", ["mastery", "wonder"], ["knowledge", "optimize", "hidden"], "选牌或遗物 → 遭遇 → 资源权衡 → 下一层"),
    ("idle_growth", "放置成长", "用很少的操作看到数在涨", ["mastery", "care"], ["optimize"], "短领取 → 放置累积 → 解锁乘数 → 再挂机"),
    ("coop_sandbox", "合作沙盒生存", "和别人一起把据点撑过今晚", ["wonder", "social", "care"], ["parse", "knowledge"], "采集或建造 → 分工 → 威胁事件 → 隔夜目标"),
    ("sim_ops", "模拟经营", "找到并按下当前真正的瓶颈", ["mastery", "care"], ["optimize", "knowledge"], "观察状态 → 一项决策 → 等待反馈 → 下一瓶颈"),
    ("puzzle_story", "解谜叙事", "用一条新信息改写对世界的理解", ["wonder", "fear", "role"], ["parse", "knowledge"], "获得信息 → 改写理解 → 解开下一层"),
    ("action_growth", "动作角色成长", "打完这一场就能看见角色更顺手", ["flow", "mastery", "wonder"], ["muscle", "react", "knowledge"], "战斗 → 掉落或强化 → 下一目标点"),
    ("turn_strategy", "回合策略", "在信息不完全时下一手仍能自圆其说", ["mastery", "status"], ["optimize", "hidden", "knowledge"], "读局势 → 回合决策 → 结算 → 新的雾"),
    ("session_party", "轻量聚会对局", "用一轮短规则把一桌人逗开", ["social", "role"], ["multi", "hidden"], "开房间 → 短规则对局 → 揭晓 → 换规则再来"),
    ("auto_batch", "自动编队对局", "在开打前把阵容选择变成一次赌注", ["mastery", "status"], ["optimize", "knowledge", "hidden"], "买单位 → 站位 → 观战结算 → 下一回合经济"),
    ("stealth_horror", "潜行压迫", "在被发现之前把一件事做完", ["fear", "tension", "wonder"], ["parse", "hidden"], "观察巡逻 → 移动或躲藏 → 目标互动 → 逃离或暴露"),
    ("city_ops", "城邦经营建设", "让一座城的下一小时比这一小时更顺", ["care", "mastery"], ["optimize", "knowledge"], "读面板 → 下一公共决策 → 等待反馈 → 新瓶颈"),
    ("sports_season", "赛季竞技体育", "把今晚的一场比赛写进赛季总账", ["status", "flow", "social"], ["react", "muscle", "parse"], "赛前准备 → 比赛节奏段 → 结算 → 赛季排名变化"),
]

for item in _TEMPLATES:
    if item[0] not in PRESETS:
        _dense_from_template(*item)

# specialised overlays
PRESETS["idle_growth"].update(playShape="solo", instinct=["instant", "idle"], sessionLength="micro", intensity=2, xpCurve="ease_in", dropFeel="flat", payEmotion=["conv", "power"], tomorrowHook="离线收益即将封顶", platforms=["mobile"])
PRESETS["puzzle_story"].update(playShape="solo", sessionLength="standard", intensity=2, payEmotion=["collect"], offlineRecall=["cliff", "unfinished"], platforms=["pc", "mobile"])
PRESETS["sim_ops"].update(playShape="solo", intensity=1, sessionLength="standard", payEmotion=["conv", "collect"])
PRESETS["extraction_survival"].update(intensity=4, sessionLength="long", dropFeel="tail", payEmotion=["power", "show", "conv"], nonlinear="broken")
PRESETS["coop_sandbox"].update(playShape="hybrid", sessionLength="open", instinct=["lonely"], payEmotion=["show", "conv"])


UI = {
    "appTitle": L("框架策划台", "Framework Brief Desk"),
    "appSubtitle": L("逐步写成游戏框架或投资计划，并按步导出", "Write a game brief or investor plan, export by step"),
    "saved": L("已自动保存", "Saved"),
    "saving": L("正在保存", "Saving"),
    "back": L("上一步", "Back"),
    "next": L("下一步", "Next"),
    "exportStepJson": L("导出本步 JSON", "Step JSON"),
    "exportStepDocx": L("导出本步 DOCX", "Step DOCX"),
    "exportStepPdf": L("导出本步 PDF", "Step PDF"),
    "exportFullJson": L("整份 JSON", "Full JSON"),
    "exportFullDocx": L("整份 DOCX", "Full DOCX"),
    "exportFullPdf": L("整份 PDF", "Full PDF"),
    "newProject": L("新建", "New"),
    "load": L("打开已存", "Open saved"),
    "applyPreset": L("套用品类预设", "Apply category preset"),
    "presetApplied": L("已套用预设，可继续修改", "Preset applied, still editable"),
    "langNeed": L("请先填写必填项", "Fill required fields first"),
    "emptySave": L("尚无已存项目", "No saved projects"),
    "subHint": L("本步含子步骤，可单独导出", "This step has sub-steps that export on their own"),
    "importJson": L("导入 JSON", "Import JSON"),
    "importTitle": L("导入指定类型的 JSON", "Import JSON of the required type"),
    "importLeadGame": L("请上传游戏框架策划案的 JSON。若文件属于商业计划书，导入将被拒绝。", "Upload a game-framework JSON. An investor-plan file will be rejected."),
    "importLeadBiz": L("请上传商业计划书的 JSON。若文件属于游戏框架策划案，导入将被拒绝。", "Upload an investor-plan JSON. A game-framework file will be rejected."),
    "importPick": L("选择文件", "Choose file"),
    "importClose": L("关闭", "Close"),
    "importOk": L("导入成功，已写入当前项目", "Import complete. Values written to this project."),
    "importBadFile": L("无法读取该文件，请选择 UTF-8 JSON。", "The file could not be read. Choose UTF-8 JSON."),
    "exportSaved": L("已保存到所选路径", "Saved to the chosen path"),
    "exportCancel": L("已取消导出", "Export cancelled"),
    "exportFail": L("导出失败", "Export failed"),
    "addOption": L("添加品类", "Add option"),
    "addPrompt": L("输入自定义品类名称", "Enter a custom option name"),
    "addCancel": L("取消", "Cancel"),
    "addConfirm": L("添加", "Add"),
}


def _o(*pairs):
    return [{"id": a, "zh": b, "en": c} for a, b, c in pairs]


OPTION_EXTRAS = {
    "orientation": _o(
        ("co_create", "合作共创", "Co-created"),
        ("brand", "品牌导向", "Brand-led"),
        ("community", "社区导向", "Community-led"),
    ),
    "platforms": _o(
        ("handheld", "掌机", "Handheld"),
        ("cloud", "云游戏", "Cloud"),
        ("xr", "VR / XR", "VR / XR"),
        ("offline", "线下机台", "Location-based"),
    ),
    "playShape": _o(
        ("async", "异步多人", "Async multiplayer"),
        ("spectate_first", "观战主导", "Spectate-first"),
        ("arena_meta", "单局竞技加长线养成", "Match plus meta growth"),
        ("rotating", "轮转活动场", "Rotating event modes"),
    ),
    "severity": _o(
        ("replace", "被替代风险高", "High substitution risk"),
        ("new_only", "主要伤新用户", "Hurts new users most"),
        ("core_only", "主要伤核心用户", "Hurts core users most"),
        ("seasonal", "季节性明显", "Seasonal"),
        ("regulation", "监管催生的缺口", "Opened by regulation"),
    ),
    "bpSeverity": _o(
        ("replace", "被替代风险高", "High substitution risk"),
        ("new_only", "主要伤新客户", "Hurts new customers most"),
        ("core_only", "主要伤付费层", "Hurts paying layer most"),
        ("seasonal", "季节性明显", "Seasonal"),
        ("regulation", "监管催生的缺口", "Opened by regulation"),
    ),
    "instinct": _o(
        ("collect", "收集完整", "Completion urge"),
        ("compete", "好胜比较", "Competitive comparison"),
        ("curiosity", "好奇心缺口", "Curiosity gap"),
        ("sunk", "不甘已投入", "Sunk cost"),
    ),
    "challengeMode": _o(("resource", "资源调度", "Resource scheduling"),),
    "nonlinear": _o(
        ("twin_peak", "双高峰", "Twin peaks"),
        ("burst", "随机爆发", "Random bursts"),
        ("plateau_jump", "平台期后跃迁", "Plateau then jump"),
        ("dip_rise", "衰减后再抬", "Dip then rise"),
        ("oscillate", "对称往复", "Oscillating"),
    ),
    "loopClosed": _o(
        ("day_yes_week_no", "日闭环、周开环", "Closed daily, open weekly"),
        ("social_only", "只在社交层闭环", "Closed only socially"),
        ("paywall", "付费才能闭环", "Closed only after pay"),
        ("break_on_fail", "失败处开环", "Opens at failure"),
        ("content_dry", "内容耗尽开环", "Opens when content dries"),
    ),
    "offlineRecall": _o(("contest", "竞赛节点临近", "Contest node approaching"),),
    "sessionPull": _o(("bar_almost", "进度条将满", "Bar almost full"),),
    "dayOccupy": _o(("cross_day", "跨天任务", "Cross-day tasks"), ("world_event", "世界事件", "World events")),
    "sessionLength": _o(
        ("tiny", "三分钟可完整", "Complete in three minutes"),
        ("quarter", "十五分钟一节", "Fifteen-minute sit"),
        ("forty", "四十分钟一节", "Forty-minute sit"),
        ("overnight", "可隔夜挂起", "Can pause overnight"),
    ),
    "ethicalCap": _o(
        ("no_lootbox", "不卖封闭随机包", "No closed random packs"),
        ("mute_recall", "可一键关闭召回", "Recall can be muted"),
        ("show_time", "显示已玩时长", "Show time spent"),
    ),
    "infra": _o(("notice", "公告", "Notices"), ("support", "客服", "Support")),
    "playSupport": _o(("handbook", "赛季手册", "Season handbook"), ("coach", "新手指引", "Coaching")),
    "ecoSupport": _o(("sub", "订阅", "Subscription"), ("trade", "玩家交易", "Player trade"), ("rent", "租赁", "Rental"), ("exchange", "兑换所", "Exchange")),
    "opsEco": _o(("guide", "攻略站", "Guides"), ("mod", "模组", "Mods"), ("merch", "周边", "Merchandise"), ("alliance", "公会联盟", "Guild alliance")),
    "xpCurve": _o(("exp", "指数", "Exponential"), ("log", "对数", "Logarithmic"), ("flat_then_step", "前期平台后期台阶", "Flat then steps")),
    "powerCurve": _o(("exp", "指数", "Exponential"), ("log", "对数", "Logarithmic"), ("flat_then_step", "前期平台后期台阶", "Flat then steps")),
    "gateStyle": _o(
        ("time", "时间门", "Time gate"),
        ("social_gate", "社交门", "Social gate"),
        ("skill_check", "技能检定门", "Skill-check gate"),
        ("resource_gate", "资源门", "Resource gate"),
        ("parallel", "并行多门", "Parallel gates"),
    ),
    "ttk": _o(
        ("ultra", "超短", "Ultra short"),
        ("burst_window", "爆发窗口", "Burst window"),
        ("attrition", "持续消耗", "Attrition"),
        ("revive_extend", "可复活延长", "Extended by revive"),
    ),
    "attrSet": _o(("energy", "能量", "Energy"), ("resist", "抗性", "Resist")),
    "infoLoad": _o(
        ("teach", "极低，偏教学", "Minimal, tutorial-like"),
        ("layered", "分层显示", "Layered HUD"),
        ("custom_hud", "可自定义界面", "Custom HUD"),
        ("audio_only", "主要靠音频", "Mostly audio"),
        ("shared_vision", "小队共享视野", "Shared squad vision"),
    ),
    "dropFeel": _o(
        ("pity_tail", "保底抬尾", "Pity lifts the tail"),
        ("event_pulse", "活动脉冲", "Event pulses"),
        ("gifted", "社交赠予", "Social gifting"),
        ("achieve", "成就解锁", "Achievement unlocks"),
        ("trade_driven", "交易驱动", "Trade driven"),
    ),
    "rankDecay": _o(
        ("idle_protect", "不活跃保护", "Idle protection"),
        ("display_only", "只衰减展示分", "Display rating only"),
        ("tiered", "分段衰减", "Tiered decay"),
        ("dual_track", "双轨分", "Dual track"),
        ("hidden_mmr", "隐藏分另计", "Hidden rating separate"),
    ),
    "pity": _o(
        ("token", "累计积分兑换", "Token exchange"),
        ("daily_sure", "每日一次必得", "Daily guaranteed"),
        ("newbie", "新手保底", "Newcomer pity"),
        ("season_reset", "赛季重置保底", "Season-reset pity"),
        ("split_pool", "分池保底", "Split-pool pity"),
    ),
    "oddsVisible": _o(
        ("after", "事后公示", "Published after"),
        ("audit", "可被第三方核对", "Third-party auditable"),
        ("range", "只给区间", "Range only"),
        ("rare_only", "只公示高稀有", "Rares only"),
        ("community", "交由社区公示", "Community published"),
    ),
    "payEmotion": _o(("fomo", "害怕错过", "Fear of missing"), ("patron", "支持创作者", "Patronage"), ("story", "解锁叙事", "Unlock story")),
    "verContent": _o(("fair", "公平与治理", "Fairness and governance"),),
    "proof": _o(("replay_audit", "录像抽检", "Replay audit"), ("canary", "灰度", "Canary"), ("ab", "对照实验", "A/B test"), ("review", "外部评审", "External review")),
    "bpKnowPay": _o(
        ("ads", "广告路径清晰", "Ad path is clear"),
        ("sub_path", "订阅路径清晰", "Subscription path is clear"),
        ("b2b", "向机构收费", "Charge institutions"),
        ("hybrid", "混合变现已排优先级", "Hybrid ranked"),
        ("delay", "先规模后收费已写时点", "Scale first, dated later"),
    ),
    "bpHorizon": _o(
        ("m3", "三个月", "Three months"),
        ("m9", "九个月", "Nine months"),
        ("m18", "十八个月", "Eighteen months"),
        ("bridge", "只覆盖到下一里程碑", "Only to next milestone"),
        ("runway", "按现有团队跑道估算", "By current runway"),
        ("contingent", "分档：做完再决定是否加码", "Tranche after proof"),
    ),
}


def _pad_fields(steps: list) -> None:
    for step in steps:
        bags = [step.get("fields") or []]
        for sub in step.get("subs") or []:
            bags.append(sub.get("fields") or [])
        for fields in bags:
            for item in fields:
                if item.get("kind") not in ("radio", "check", "select"):
                    continue
                if item.get("key") == "docType":
                    continue
                options = list(item.get("options") or [])
                seen = {o["id"] for o in options}
                for extra in OPTION_EXTRAS.get(item["key"], []):
                    if extra["id"] not in seen:
                        options.append(extra)
                        seen.add(extra["id"])
                n = 1
                while len(options) < 8:
                    oid = f"{item['key']}_plus_{n}"
                    if oid not in seen:
                        options.append({"id": oid, "zh": f"扩展项 {n}", "en": f"Extension {n}"})
                        seen.add(oid)
                    n += 1
                item["options"] = options


_pad_fields(GAME_STEPS)
_pad_fields(BP_STEPS)


def steps_for(doc_type: str) -> list:
    return GAME_STEPS if doc_type != "business" else BP_STEPS


def all_steps() -> list:
    seen = {}
    for block in GAME_STEPS + BP_STEPS:
        seen[block["id"]] = block
    return list(seen.values())


def public_schema() -> dict:
    return {
        "version": APP_VERSION,
        "productZh": PRODUCT_ZH,
        "productEn": PRODUCT_EN,
        "genres": GENRES,
        "gameSteps": GAME_STEPS,
        "businessSteps": BP_STEPS,
        "presets": PRESETS,
        "ui": UI,
        "typeLabel": TYPE_LABEL,
    }
