#!/usr/bin/env python3
"""从 chapters/ 自动生成 附录 B 术语表 与 附录 C 面试题索引。

    python3 reference/gen_appendix.py

术语的「首次出现章节」与面试题的题面均从章节 HTML 中提取，
因此改动章节后重跑本脚本即可保持附录同步。中文释义维护在本文件的 GLOSS 中。
reference/ 不发布，本脚本仅供构建期使用。
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS = os.path.join(ROOT, "chapters")

# 章节 slug -> (显示编号, 显示标题)
CH_META = {
    "0-1-how-to-read": ("0", "导读"),
    "1-1-tokenization": ("1.1", "Tokenization 与 Context Window"),
    "1-2-kv-cache": ("1.2", "KV Cache 与 PagedAttention"),
    "1-3-continuous-batching": ("1.3", "Continuous Batching"),
    "1-4-quantization": ("1.4", "量化 Quantization"),
    "1-5-speculative-decoding": ("1.5", "Speculative Decoding"),
    "2-1-latency-metrics": ("2.1", "延迟指标体系"),
    "2-2-prompt-caching": ("2.2", "Prompt Caching"),
    "2-3-model-routing": ("2.3", "模型分级与路由"),
    "2-4-capacity-planning": ("2.4", "容量规划与成本估算"),
    "3-1-why-rag": ("3.1", "为什么需要 RAG"),
    "3-2-chunking": ("3.2", "Chunking 策略"),
    "3-3-hybrid-search-rerank": ("3.3", "Embedding、Hybrid Search 与 Rerank"),
    "3-4-rag-vs-long-context": ("3.4", "RAG 是错误答案的时候"),
    "3-5-rag-eval": ("3.5", "RAG 评估"),
    "4-1-tool-use": ("4.1", "Tool Use 基础"),
    "4-2-planning-loop": ("4.2", "Planning Loop"),
    "4-3-memory": ("4.3", "Memory 设计"),
    "4-4-multi-agent": ("4.4", "Multi-agent：何时是过度设计"),
    "4-5-agent-eval": ("4.5", "Agent Evaluation"),
    "5-1-finetune-decision": ("5.1", "Fine-tune 是最后的手段"),
    "5-2-sft-peft": ("5.2", "SFT 与 PEFT 家族"),
    "5-3-data-engineering": ("5.3", "数据工程 — 真正的瓶颈"),
    "5-4-alignment-and-validation": ("5.4", "偏好对齐与验证"),
    "6-1-observability": ("6.1", "可观测性"),
    "6-2-prompt-injection": ("6.2", "Prompt Injection 与安全"),
    "6-3-hallucination": ("6.3", "幻觉的工程化缓解"),
    "6-4-eval-pipeline": ("6.4", "Eval Pipeline"),
    "6-5-degradation-fallback": ("6.5", "Degradation 与 Fallback"),
}

# 术语 -> (中文名, 释义)。释义须与正文一致，不生造译名。
GLOSS = {
    "token": ("词元", "模型处理文本的基本单位，也是计费、上下文长度与延迟的计量单位。模型看到的不是字符，而是 token ID 序列。"),
    "tokenizer": ("分词器", "把文本切成 token 并映射为整数 ID 的组件。不同模型的 tokenizer 互不通用，token 数必须用实际调用的模型来测。"),
    "BPE": ("字节对编码", "Byte Pair Encoding。从字节开始反复合并高频相邻符号对，得到固定大小词表的分词方法。高频内容压成一个 token，低频内容退化为碎片，且永不 OOV。"),
    "OOV": ("词表外", "out-of-vocabulary，输入中出现词表里没有的词。BPE 等子词方法通过回退到字节级编码消除了这一问题。"),
    "context window": ("上下文窗口", "模型单次能处理的最大 token 数。它是能力上限而非使用建议——填满它的代价随长度超线性增长。"),
    "prefill": ("预填充", "推理的第一阶段，一次性处理全部输入 token 并写入 KV cache。其 attention 计算量约为输入长度的二次方，是 TTFT 的主要来源。"),
    "decode": ("解码", "推理的第二阶段，逐个生成输出 token。每步只算一个 token 但要读取全部权重，因此受显存带宽限制。"),
    "autoregressive": ("自回归", "每次生成一个 token 并把它拼回输入再生成下一个的方式。它决定了解码必然是串行的。"),
    "KV cache": ("键值缓存", "缓存已计算的 Key/Value 向量以避免重复计算。占用显存随并发数与序列长度线性增长，常常是并发上限的真正瓶颈。"),
    "Key": ("键向量", "attention 机制中用于与 Query 做匹配的向量，逐 token 计算后可缓存复用。"),
    "Value": ("值向量", "attention 机制中被加权求和的内容向量，与 Key 一同构成 KV cache。"),
    "GQA": ("分组查询注意力", "Grouped-Query Attention。多个 query head 共享一组 KV head，按比例直接降低 KV cache 占用。它省的不是算力，是显存。"),
    "PagedAttention": ("分页注意力", "借鉴操作系统虚拟内存的 KV cache 管理方式：切成固定大小的 block 按需分配，物理上不必连续。消除了预留浪费与外部碎片。"),
    "block": ("块", "PagedAttention 中固定大小的 KV cache 分配单元（如 16 个 token 一块）。"),
    "block table": ("块表", "记录「逻辑块 N 存放在哪个物理块」的映射表，使显存分配无需连续。"),
    "virtual memory": ("虚拟内存", "操作系统让进程看到连续地址空间、而物理内存可以是碎片的机制。PagedAttention 把这套思想搬进了显存。"),
    "copy-on-write": ("写时复制", "多方共享同一份数据、直到有人要写入时才复制的机制。使多条序列可以共享公共前缀的 KV。"),
    "memory bandwidth": ("显存带宽", "数据在显存与计算单元之间的传输速率。解码阶段的真正瓶颈通常是它而非算力。"),
    "memory-bandwidth-bound": ("受显存带宽限制", "性能由数据搬运速度而非计算速度决定的状态。它解释了为什么批处理能几乎免费地提升吞吐。"),
    "static batching": ("静态批处理", "攒够一批请求一起执行、等整批完成才换下一批。已完成的请求会占着槽位空转，长度方差越大浪费越严重。"),
    "continuous batching": ("连续批处理", "以一次 forward 迭代为调度单位，完成的序列立即离场、新请求立即补位。消除的是时间维度的浪费。"),
    "iteration-level scheduling": ("迭代级调度", "连续批处理在论文中的名称，强调调度粒度从「请求」下降到「迭代」。"),
    "selective batching": ("选择性批处理", "只对与序列长度无关的算子做批处理，attention 部分按序列单独处理。它让批内序列长度可以自由不同。"),
    "chunked prefill": ("分块预填充", "把长 prefill 切成小块摊到多次迭代，避免它阻塞正在进行的解码。用少量 TTFT 换取平稳的 TPOT。"),
    "quantization": ("量化", "用更少的比特表示模型参数。它省的主要是显存与带宽；能否加速取决于量化对象与 batch 大小。"),
    "weight-only quantization": ("仅权重量化", "只压缩权重、计算时仍解压回高精度。在低并发场景提速明显，高并发下收益可能有限。"),
    "PTQ": ("训练后量化", "post-training quantization，对训练好的模型直接量化，成本低，是应用层的默认选择。"),
    "QAT": ("量化感知训练", "quantization-aware training，训练中模拟量化误差，质量更好但需重新训练。"),
    "outlier": ("离群值", "少数维度上比其余值大几个数量级的激活值。它会撑大量化范围、毁掉其余值的精度，是大模型量化的核心难点。"),
    "speculative decoding": ("投机解码", "用便宜模型生成草稿、由目标模型一次性并行验证。输出分布与原模型严格相同，本质是用富余算力换延迟。"),
    "speculative execution": ("投机执行", "CPU 中先赌一个分支往下算、赌错则回滚的技术。投机解码借用了同一思想。"),
    "time to first token": ("首字延迟 TTFT", "从发出请求到收到第一个 token 的时间，包含排队与 prefill。它是用户等待感的全部来源。"),
    "time per output token": ("每 token 延迟 TPOT", "后续每个输出 token 的平均间隔，决定流畅度。快过用户阅读速度后再优化收益趋近于零。"),
    "goodput": ("有效吞吐", "单位时间内满足 SLA 的请求数。容量规划应以它而非裸吞吐为准，两者的峰值通常不在同一点。"),
    "prompt caching": ("提示词缓存", "复用相同前缀已算好的 KV，跳过其 prefill。降低 TTFT 与输入成本，但不影响 TPOT。"),
    "prefix caching": ("前缀缓存", "prompt caching 的底层实现名称。匹配是从第 0 个 token 开始的逐 token 精确前缀匹配。"),
    "RadixAttention": ("基数树注意力", "用基数树自动组织并复用跨请求的公共前缀 KV，无需应用显式声明。"),
    "model routing": ("模型路由", "按请求难度把流量分配到不同能力/价格档位的模型。收益上限由简单请求的占比决定。"),
    "Little's Law": ("利特尔法则", "稳态系统中「平均在途请求数 = 到达率 × 平均停留时间」。用于把 QPS 换算成并发数，进而推导 KV cache 需求。"),
    "RAG": ("检索增强生成", "Retrieval-Augmented Generation。先检索外部知识再生成答案，把事实从权重里解耦出来。"),
    "parametric knowledge": ("参数化知识", "存在模型权重里的知识。稳定但无法快速更新、无法溯源、无法做权限区分。"),
    "non-parametric knowledge": ("非参数化知识", "存在外部可检索索引里的知识。可秒级更新、可溯源、可按权限过滤。"),
    "hallucination": ("幻觉", "模型生成看似合理但与事实不符的内容。它是生成机制的固有产物，工程目标是让它可检测、可控，而非消灭它。"),
    "chunk": ("文本块", "文档被切分后的检索单元。「检索要小、理解要大」的两难可通过「小块检索、大块生成」解耦。"),
    "embedding": ("向量嵌入", "把文本映射为高维向量，使语义相近的文本距离相近。本质是有损压缩，优先保留大意、丢弃细节。"),
    "dense retrieval": ("稠密检索", "基于向量相似度的检索。擅长语义改写，但在精确标识符、罕见词、否定与领域外场景上有系统性盲区。"),
    "BM25": ("BM25", "基于词频与文档长度归一的经典词法检索算法。因为不需要泛化，它在跨领域场景下依然是稳健基线。"),
    "RRF": ("倒数排名融合", "Reciprocal Rank Fusion。只按排名而非分数融合多路检索结果，无需归一化与调权重。"),
    "lost in the middle": ("中间迷失", "相关信息位于长上下文中部时模型利用率明显下降的现象，呈 U 形曲线。说明「塞进去不等于用得上」。"),
    "groundedness": ("忠实度", "回答中的事实性陈述能否在检索到的材料中找到依据。它比「正确率」更适合作为 RAG 生成层的核心指标，因为可自动化、可归因。"),
    "function calling": ("函数调用", "模型输出结构化的工具调用请求。模型本身从不执行任何工具——执行的是你的代码，安全边界也在那里。"),
    "ReAct": ("推理-行动交错", "把推理轨迹与行动交错生成的 agent 循环模式。推理帮助规划与纠错，行动带来外部信息。"),
    "memory": ("记忆", "agent 语境下由应用层构造的上下文管理机制。模型本身无记忆，它「记得」只是因为你又发了一遍。"),
    "multi-agent": ("多智能体", "多个 agent 分工协作的架构。收益来自并行探索与突破单一上下文容量，代价是每条通信边都是有损压缩。"),
    "pass^k": ("pass^k", "同一任务连续 k 次执行全部成功的概率，衡量一致性。它比单次成功率更能预测 agent 在生产中的可用性。"),
    "distillation": ("蒸馏", "用强模型的输出训练小模型，使其在窄任务上接近强模型。教师的错误率会被学生继承，因此数据过滤是关键。"),
    "SFT": ("有监督微调", "supervised fine-tuning，用「输入-期望输出」样本对继续训练。适用于有明确对错标准的任务。"),
    "PEFT": ("参数高效微调", "parameter-efficient fine-tuning，只训练极少量参数即可完成任务适配的一类方法。"),
    "LoRA": ("低秩适配", "Low-Rank Adaptation。冻结原权重，用两个低秩矩阵表示改动量。推理时可合并回原权重，零额外延迟。"),
    "QLoRA": ("量化低秩适配", "把冻结的基座量化到 4-bit 再训练 LoRA adapter，大幅降低显存门槛，使单卡微调大模型成为常规操作。"),
    "catastrophic forgetting": ("灾难性遗忘", "在新任务上训练导致旧能力退化。它在目标任务指标上完全不可见，必须用无关的能力回归测试来检测。"),
    "preference alignment": ("偏好对齐", "利用「比较比生成容易」的不对称性来调整模型行为，适用于「什么算好」难以写成标准答案的场景。"),
    "RLHF": ("基于人类反馈的强化学习", "先拟合奖励模型、再用强化学习优化策略的两阶段对齐路径。"),
    "abstention": ("拒答", "模型在依据不足时明确表示无法回答。两类错误代价不对称——过度自信悄无声息，过度保守立刻被发现，因此默认应偏保守。"),
    "trace": ("调用链", "一次请求横跨检索、模型调用、工具调用等多个 span 的完整记录。每个 span 须带 token 数、成本与模型版本，否则无法归因。"),
    "LLM-as-judge": ("模型评委", "用模型给模型的输出打分。必须先用人工标注校准一致率——未校准的评委比没有评委更危险。"),
    "parameterized query": ("参数化查询", "SQL 中从语法层分离语句与数据的机制，它根治了 SQL 注入。LLM 缺少对应的结构，这正是 prompt injection 难以根治的原因。"),
    "indirect prompt injection": ("间接提示注入", "把恶意指令藏在模型会读到的外部内容里，借受害者的权限执行。凡是接入检索或工具的系统都要按它来建模。"),
    "circuit breaker": ("熔断器", "连续失败达阈值后快速失败、定期试探恢复。既避免拖死自己，也给上游留出恢复空间。"),
}

# 面试题索引按题型分组的展示顺序
QTYPE_ORDER = ["面试题改编", "架构评审", "决策题", "场景判断", "场景判断组",
               "估算题", "计算题", "概念题"]

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · AI 系统工程手册</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Noto+Sans+SC:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/handbook.css">
<script src="assets/theme.js"></script>
</head>
<body>
<button class="theme-toggle" type="button" aria-label="切换深色/浅色模式" title="切换深色/浅色模式">
  <span class="moon" aria-hidden="true">🌙</span><span class="sun" aria-hidden="true">☀️</span>
</button>
<div class="wrap">

<nav class="crumb"><a href="index.html">← 目录</a> · 附录 {letter}</nav>

<header class="ch">
  <div class="blockrow" aria-hidden="true">
    <span></span><span></span><span></span><span class="w"></span><span></span>
    <span></span><span class="f"></span><span></span><span class="f"></span><span class="f"></span>
  </div>
  <div class="kicker">Appendix {letter}</div>
  <h1>{en}
    <span class="zh">{title}</span>
  </h1>
  <div class="meta"><span>本页由 <b>reference/gen_appendix.py</b> 从各章自动生成</span></div>
</header>
"""

FOOT = """
<nav class="next">
  {prev}
  {next}
</nav>

</div>
</body>
</html>
"""


def read_chapters():
    out = {}
    for slug in CH_META:
        p = os.path.join(CHAPTERS, slug + ".html")
        out[slug] = open(p, encoding="utf-8").read()
    return out


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def build_glossary(chs):
    """术语 -> 首次出现的章节 slug（按章节顺序）。"""
    first = {}
    for slug in CH_META:
        for t in re.findall(r'<span class="term">(.*?)</span>', chs[slug]):
            t = strip_tags(t)
            if t not in first:
                first[t] = slug
    # KV cache 在导读中作为「术语写法示例」出现，真正的定义在 1.2
    if first.get("KV cache") == "0-1-how-to-read":
        first["KV cache"] = "1-2-kv-cache"

    missing = [t for t in first if t not in GLOSS]
    if missing:
        raise SystemExit("以下术语缺少中文释义，请补进 GLOSS：{}".format(missing))

    # 按英文术语字母序分组
    groups = {}
    for t in sorted(first, key=lambda x: x.lower()):
        groups.setdefault(t[0].upper(), []).append(t)

    letters = sorted(groups)
    body = ['<section style="margin-top:40px">']
    body.append("<p>全书共 <b>{}</b> 条术语。每条给出英文原文、中文解释，"
                "以及<b>首次出现章节的锚点链接</b>——点击可直接跳到该术语被引入的段落。"
                "业界无通用中文译名的术语保持英文，本书不生造译名。</p>".format(len(first)))
    body.append('<div class="gl-nav">')
    for L in letters:
        body.append('<a href="#gl-{0}">{0}</a>'.format(L))
    body.append("</div>")
    body.append("</section>")

    for L in letters:
        body.append('<div class="gl-group" id="gl-{}">'.format(L))
        body.append("<h2>{}</h2>".format(L))
        for t in groups[L]:
            zh, desc = GLOSS[t]
            slug = first[t]
            num, name = CH_META[slug]
            anchor = "s01" if slug.startswith("0-") else "concept"
            body.append('<div class="gl-item">')
            body.append('<div><span class="en">{}</span>'
                        '<span class="zh">{}</span></div>'.format(html.escape(t), zh))
            body.append('<div class="desc">{}</div>'.format(desc))
            body.append('<div class="ref">首次出现：'
                        '<a href="chapters/{}.html#{}">{} {}</a></div>'
                        .format(slug, anchor, num, name))
            body.append("</div>")
        body.append("</div>")

    page = HEAD.format(title="术语表 Glossary", letter="B", en="Glossary",
                       desc="全书技术术语的英文原文、中文解释与首次出现章节锚点。")
    page += "\n".join(body)
    page += FOOT.format(
        prev='<a href="appendix-a-tooling.html">← 附录 A 工具层速查</a>',
        next='<a href="appendix-c-interview-index.html">附录 C 面试题索引 →</a>')
    open(os.path.join(ROOT, "glossary.html"), "w", encoding="utf-8").write(page)
    return len(first)


def build_interview_index(chs):
    """从各章 quiz 中提取题型与题面，按题型聚合。"""
    items = []
    for slug in CH_META:
        for m in re.finditer(
                r'<summary><span class="qtype">(.*?)</span>(.*?)</summary>',
                chs[slug], flags=re.S):
            qtype = strip_tags(m.group(1))
            text = strip_tags(m.group(2))
            text = re.sub(r"\s+", " ", text)
            items.append((qtype, text, slug))

    by_type = {}
    for qtype, text, slug in items:
        by_type.setdefault(qtype, []).append((text, slug))

    order = [q for q in QTYPE_ORDER if q in by_type]
    order += [q for q in sorted(by_type) if q not in QTYPE_ORDER]

    body = ['<section style="margin-top:40px">']
    body.append("<p>本页从全书 {} 章的章末自测中<b>自动聚合</b>了 <b>{}</b> 道题，"
                "按题型分组，便于面试前按题型集中复习。"
                "每题链接回原章节，参考答案与推导过程在原章节中默认折叠——"
                "<b>建议先自己回答，再展开对照</b>。</p>"
                .format(len(CH_META), len(items)))
    body.append('<div class="gl-nav">')
    for q in order:
        body.append('<a href="#q-{}">{}（{}）</a>'.format(
            abs(hash(q)) % 10000, q, len(by_type[q])))
    body.append("</div>")
    body.append('<div class="callout"><p><b>怎么用这一页。</b>'
                '「面试题改编」与「架构评审」两组最接近真实面试的提问方式，'
                '优先刷这两组；「估算题」「计算题」考察的是能不能当场算出量级，'
                '需要动笔而不只是看答案；「场景判断」与「决策题」考察的是取舍意识，'
                '答案的价值在推导链条而非结论本身。</p></div>')
    body.append("</section>")

    for q in order:
        body.append('<div class="gl-group" id="q-{}">'.format(abs(hash(q)) % 10000))
        body.append("<h2>{}　<span style=\"font-family:var(--mono);font-size:14px;"
                    "font-weight:400;color:var(--ink-soft)\">{} 题</span></h2>"
                    .format(q, len(by_type[q])))
        for text, slug in by_type[q]:
            num, name = CH_META[slug]
            body.append('<div class="gl-item">')
            body.append('<div class="desc">{}</div>'.format(html.escape(text)))
            body.append('<div class="ref"><a href="chapters/{}.html#quiz">{} {} →</a></div>'
                        .format(slug, num, name))
            body.append("</div>")
        body.append("</div>")

    page = HEAD.format(title="面试题索引", letter="C", en="Interview Question Index",
                       desc="全书章末自测按题型聚合，冲刺复习用。")
    page += "\n".join(body)
    page += FOOT.format(
        prev='<a href="glossary.html">← 附录 B 术语表</a>',
        next='<a href="index.html">返回目录 →</a>')
    open(os.path.join(ROOT, "appendix-c-interview-index.html"), "w",
         encoding="utf-8").write(page)
    return len(items)


if __name__ == "__main__":
    chs = read_chapters()
    n_terms = build_glossary(chs)
    n_quiz = build_interview_index(chs)
    print("glossary.html: {} 条术语".format(n_terms))
    print("appendix-c-interview-index.html: {} 道题".format(n_quiz))
