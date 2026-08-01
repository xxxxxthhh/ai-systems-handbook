# AI 系统工程手册 · AI Systems Engineering Handbook — 全书骨架 v1

> 定位：面向应用层 AI 工程师的双语（中文为主、英文术语原文标注）HTML 电子书。
> 范式沿用期权手册：每章 = 核心概念 + 真实案例 + 图表 + 自测题（quiz）。
> 双重目标：个人知识整理 + 公开作品集（求职转型背书）。

---

## 全书结构总览

「用 → 调 → 养」递进：

| Part | 主题 | 一句话定位 |
|------|------|-----------|
| 0 | 导读 | 怎么读这本书、知识分层说明 |
| 1 | LLM 推理基础 (Inference Fundamentals) | 模型是怎么跑起来的 |
| 2 | 模型服务与成本工程 (Serving & Cost) | 怎么跑得又快又省 |
| 3 | RAG 与上下文工程 (RAG & Context Engineering) | 怎么让模型知道它不知道的事 |
| 4 | Agent 设计模式 (Agent Design Patterns) | 怎么让模型做事而不只是说话 |
| 5 | Training / Fine-tuning | 什么时候、怎么定制模型 |
| 6 | 生产化 (Production) | 可观测性、安全与失败模式 |
| 附录 | 工具层速查 (Tooling Appendix) | 易过期内容集中存放，低成本更新 |
| 附录 | 术语表 (Glossary) | 面向中文读者的英文术语独立页 |

**知识分层原则（全书贯彻）**：
- **原理层**（正文）：为什么存在、解决什么问题、不随工具版本过期。
- **工具层**（侧栏 sidebar / 附录）：当前主流工具的具体参数与用法，标注「截至日期」，允许过期，集中更新。

---

## Part 0 · 导读

- 0.1 这本书写给谁、不写给谁（应用层工程师 ✓ / 预训练研究员 ✗）
- 0.2 原理层 vs 工具层的阅读方法
- 0.3 全书贯穿案例预告（见 Part 5 说明）

## Part 1 · LLM 推理基础 (Inference Fundamentals)

- 1.1 **Tokenization 与 Context Window** — token 是什么、为什么中文更「贵」、context window 的真实成本曲线
  - 案例：同一段文本在不同 tokenizer 下的 token 数对比（图表）
  - Quiz：估算题（给定文本估 token 数与成本）
- 1.2 **KV Cache 与 PagedAttention** ⭐ 样章
  - 为什么自回归生成需要 KV cache、显存怎么被浪费、PagedAttention 的分页思想
  - 案例：vLLM 论文（显存碎片浪费 → 分页管理），显存分配对比图
  - Quiz：面试高频题改编（如「为什么 KV cache 随 batch 和序列长度线性增长」）
- 1.3 **Continuous Batching** — static vs continuous batching、吞吐提升的来源
  - 案例：Orca 论文的调度示意图重绘
- 1.4 **量化 (Quantization)** — 为什么可行（原理层）；GPTQ / AWQ / FP8 差异（工具层侧栏）
  - 案例：同一模型不同量化等级的质量-显存-速度三角对比
- 1.5 **Speculative Decoding** — 草稿模型思想、什么时候有效什么时候反而更慢
  - Quiz：场景判断题（哪些负载适合投机解码）

## Part 2 · 模型服务与成本工程 (Serving & Cost Engineering)

- 2.1 **延迟指标体系** — TTFT / TPOT / E2E latency，latency vs throughput 的根本取舍
- 2.2 **Prompt Caching** — 前缀缓存原理、对系统提示词设计的反向约束
  - 案例：长 system prompt 场景开启缓存前后的成本对比
- 2.3 **模型分级与路由 (Model Routing)** — 什么任务用小模型、级联与回退设计
- 2.4 **容量规划与成本估算** — 从流量画像到 GPU 数量 / API 预算的估算方法
  - Quiz（本 Part 核心题型）：**决策题** — 给定流量画像与 SLA，选部署方案并估算月成本，附参考答案的推导过程

## Part 3 · RAG 与上下文工程 (RAG & Context Engineering)

- 3.1 **为什么需要 RAG** — 参数化知识 vs 非参数化知识、幻觉的知识边界成因
- 3.2 **Chunking 策略** — 固定长度 / 语义切分 / 结构感知切分的边界情况
  - 案例（失败案例）：chunk 切坏导致检索质量崩塌的典型复盘
- 3.3 **Embedding、Hybrid Search 与 Rerank** — 稠密检索的盲区、BM25 为什么没死、两阶段检索
- 3.4 **RAG 是错误答案的时候** — 长上下文 vs RAG 的成本与质量边界、什么时候该直接塞上下文
  - Quiz：场景判断题（RAG / 长上下文 / fine-tune 三选一）
- 3.5 **RAG 评估** — retrieval 指标与生成质量指标分离评估

## Part 4 · Agent 设计模式 (Agent Design Patterns)

- 4.1 **Tool Use 基础** — function calling 的本质、schema 设计对成功率的影响
- 4.2 **Planning Loop** — ReAct、plan-and-execute、反思循环；何时循环何时一把梭
- 4.3 **Memory 设计** — 短期 / 长期记忆、上下文压缩策略
- 4.4 **Multi-agent：何时是过度设计** — 单 agent + 好工具 vs 多 agent 编排的判断标准
- 4.5 **Agent Evaluation** — 轨迹评估、任务完成率、为什么 agent eval 比模型 eval 难
  - 贯穿案例：一个私有 AI 助理平台的真实架构演进（匿名化）
  - Quiz：架构评审题（给一个 agent 设计，找出三处问题）

## Part 5 · Training / Fine-tuning

> 定位：不教从零训模型，教「该不该训、训什么、怎么验证」。
> **贯穿叙事案例**：把一个任务从前沿大模型 API 蒸馏到自托管小模型的完整故事，四章各讲一段。

- 5.1 **Fine-tune 是最后的手段 — 决策框架** — prompt → few-shot → RAG → fine-tune 升级路径，每级的成本收益边界
  - Quiz（本章灵魂）：场景判断题组（退款政策知识 → RAG；稳定 JSON 输出 → constrained decoding；垂直领域推理风格 → fine-tune）
  - 故事线第 1 段：要不要蒸馏的决策
- 5.2 **SFT 与 PEFT 家族** — LoRA/QLoRA 原理（低秩分解 ΔW=BA 图解）、rank/alpha 选择、full FT vs LoRA 能力边界
  - 工具层侧栏：Axolotl / Unsloth / LLaMA-Factory 配置速查
  - 故事线第 2 段：选 LoRA 配置
- 5.3 **数据工程 — 真正的瓶颈** — 数据配比、去重与质量过滤、合成数据与蒸馏、灾难性遗忘及缓解
  - 案例：Phi 系列 "textbook quality data"、Alpaca 52k 合成样本
  - 故事线第 3 段：造数据
- 5.4 **偏好对齐与验证** — RLHF/DPO 概念层（DPO 绕开 reward model 的对比图）、eval set 设计、与 base model 的 A/B、能力回归测试
  - 故事线第 4 段：验证效果
  - 与 Part 6 的 eval 章节交叉引用

## Part 6 · 生产化 (Production)

- 6.1 **可观测性** — LLM 应用的 tracing、成本与质量监控指标设计
- 6.2 **Prompt Injection 与安全** — 攻击面分类、工程化缓解、为什么无法根治
  - 案例：公开的注入攻击事件复盘
- 6.3 **幻觉的工程化缓解** — 引用约束、置信度信号、拒答设计
- 6.4 **Eval Pipeline** — 离线 eval / 在线 A/B / 回归测试三层体系
- 6.5 **Degradation 与 Fallback** — 上游模型故障、限流、降级策略
  - 案例：公开 postmortem 选编（对应期权手册的「经典历史案例」角色）

## 附录

- A. 工具层速查（vLLM / SGLang / TGI 参数、主流 embedding 模型对比等，每节标注「截至日期」）
- B. 术语表 Glossary（独立页，英文术语 + 中文解释 + 首次出现章节链接）
- C. 面试题索引（按章节聚合全书 quiz 中的面试高频题，方便冲刺复习）

---

## 执行顺序（沿用期权手册流程）

1. 骨架定稿（本文档）
2. 样章验证：**1.2 KV Cache 与 PagedAttention**（概念清楚、论文背书、图表表现力强、面试高频）
3. 格式确认后由 Claude Code 全量构建
4. 托管：GitHub Pages / Cloudflare Pages，支持导出 PDF
