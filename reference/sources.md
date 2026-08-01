# 引用溯源台账

CLAUDE.md 写作红线：**不虚构论文数据；引用论文数字须可溯源**。
本文件登记正文中每一个归属于论文 / 公开报告的数字，及其核验状态。
`reference/` 不发布，仅供构建与审校使用。

状态说明：
- **已核验** — 构建时通过检索原始论文摘要 / 出版方页面确认过数字与条件。
- **自行推导** — 本书按明示假设自己算出来的，不归属任何论文（CLAUDE.md 允许，须写出计算方法）。

> 通则：所有引用**必须连同实验条件一起写出**（哪个模型、什么基线、什么负载）。
> 脱离条件的「快 N 倍」在本书中视为不合格引用。

---

## Part 1 · 推理基础

| 章节 | 数字 / 主张 | 条件（必须同时出现在正文） | 来源 | 状态 |
|------|------------|---------------------------|------|------|
| 1.1 | 同一内容跨语言 token 数最高差 **15×** | 跨语言对比测量 | Petrov, La Malfa, Torr, Bibi, *Language Model Tokenizers Introduce Unfairness Between Languages*, NeurIPS 2023 | 已核验 |
| 1.1 | 字符级/字节级模型部分语言对仍有 **>4×** 差距 | 同上 | 同上 | 已核验 |
| 1.1 | 多轮对话 token 累积估算 | 假设中文 1 字≈1.3 token（正文明示需实测） | — | 自行推导 |
| 1.2 | KV 显存浪费 **60–80%**、改造后 **<4%**、吞吐 **2–4×**、block=16 | vs 2023 年 SOTA（FasterTransformer / Orca 等） | Kwon et al., *Efficient Memory Management for LLM Serving with PagedAttention*, SOSP 2023 | 沿用审定样章 |
| 1.3 | **36.9×** 吞吐提升 | GPT-3 175B，**固定延迟 190ms** 时，基线 NVIDIA FasterTransformer；0.185 → 6.81 req/s | Yu, Jeong, Kim, Kim, Chun, *Orca*, OSDI 2022 | 已核验 |
| 1.4 | 离群特征在 **6.7B** 规模全面涌现；约 **6** 个维度承载约 15 万离群值；置零导致困惑度劣化 **600–1000%**；占比约 **0.1%** | Transformer 激活值测量 | Dettmers et al., *LLM.int8()*, NeurIPS 2022 | 已核验 |
| 1.4 | 175B 模型 **~4 GPU 小时**量化到 3–4 bit；OPT-175B 3-bit 困惑度 **8.68** vs 全精度 **8.34** | 一次性 PTQ | Frantar et al., *GPTQ*, ICLR 2023 | 已核验 |
| 1.4 | 保护约 **1%** 显著权重即可大幅降低量化误差；相对 HF FP16 实现 **>3×** 加速 | MLSys 2024 最佳论文 | Lin et al., *AWQ*, MLSys 2024 | 已核验 |
| 1.4 | 7B 模型各位宽显存占用（14/7/3.5 GB） | 参数量 × 每参数字节数 | — | 自行推导 |
| 1.5 | **2×–3×** 加速，输出分布完全一致 | **T5-XXL**，基线为标准 T5X 实现 | Leviathan, Kalman, Matias, *Fast Inference from Transformers via Speculative Decoding*, ICML 2023 (arXiv:2211.17192) | 已核验 |
| 1.5 | 期望产出 = (1−α^(K+1))/(1−α) | 明示「每个草稿 token 独立以概率 α 被接受」的简化假设 | — | 自行推导 |

---

## 待补充

Part 2–6 的引用在各 Part 撰写前批量核验后登记。
