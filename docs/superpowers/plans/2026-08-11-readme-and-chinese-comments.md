# Quelyra 中文 README 与注释改造实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Quelyra 骨架改造成中文成品宣传型项目文档，并将所有用途占位注释改为中文，同时保持仓库没有业务实现代码。

**Architecture:** 根 README 负责产品价值、系统架构、技术栈、项目结构、快速开始和工程约定；各子目录 README 只描述局部职责。代码与配置占位文件按照语言支持的注释语法改写，严格 JSON 继续保留空对象。

**Tech Stack:** Markdown、Mermaid、Python 注释、Go 注释、TypeScript/Vue/CSS 注释、PowerShell 验证、ripgrep。

---

### Task 1: 重写根项目 README

**Files:**
- Modify: `D:/code/quelyra/README.md`

- [ ] 使用中文成品口吻说明 Quelyra 的定位、问题、核心能力和适用场景。
- [ ] 加入 Mermaid 系统架构图和自然语言分析流程。
- [ ] 加入技术栈、完整 Monorepo 目录树及 Python、Go、Vue3 的职责边界。
- [ ] 加入快速开始、配置、安全、评测、开发约定、路线图与常见问题。
- [ ] 不填写虚假指标、演示地址、截图或 CI 状态。

### Task 2: 中文化子目录 README

**Files:**
- Modify: `D:/code/quelyra/**/README.md`

- [ ] 将服务、契约、评测、部署、Demo、前端功能目录的标题和用途说明改为中文。
- [ ] 服务 README 说明边界，功能 README 说明目录所有权，避免复制根 README。
- [ ] 扫描 README 中的英文用途标记和英文占位标题，预期无匹配。

### Task 3: 中文化所有用途占位注释

**Files:**
- Modify: `D:/code/quelyra/**/*.py`
- Modify: `D:/code/quelyra/**/*.go`
- Modify: `D:/code/quelyra/**/*.ts`
- Modify: `D:/code/quelyra/**/*.vue`
- Modify: `D:/code/quelyra/**/*.css`
- Modify: `D:/code/quelyra/**/*.{yaml,yml,toml}`
- Modify: `D:/code/quelyra/**/.gitkeep`
- Modify: `D:/code/quelyra/Makefile`
- Modify: `D:/code/quelyra/**/Dockerfile`

- [ ] 保留每种文件原有注释语法，只将说明改为自然、具体的中文职责描述。
- [ ] 严格 JSON 文件保持 `{}`，由 `apps/web/README.md` 解释其用途。
- [ ] 扫描全仓库的英文用途标记，预期无匹配。

### Task 4: 验证文档与纯骨架约束

**Files:**
- Verify: `D:/code/quelyra/README.md`
- Verify: `D:/code/quelyra/**/*`

- [ ] 检查根 README 必须包含“核心能力”“系统架构”“项目结构”“快速开始”“安全设计”“评测体系”。
- [ ] 扫描 `.py`，确认不存在 `import`、`def`、`class` 等可执行声明。
- [ ] 扫描 `.go`，确认不存在 `package`、`import`、`func`、`type` 等声明。
- [ ] 扫描 `.ts` 和 `.vue`，确认不存在实现声明或组件代码块。
- [ ] 解析全部 JSON，确认格式合法且仍为空对象。
- [ ] 输出 README 数量、英文用途残留数和实现代码违规数；全部必须为零违规。
