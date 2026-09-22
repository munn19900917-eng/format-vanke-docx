# format-vanke-docx

Kimi Skill：万科公文版式 Word 一键排版。

## 安装

把下面这句话发给你的 Kimi / Claude Code / 任意 Agent：

> 现在为你安装 format-vanke-docx 技能，请执行 `curl -fsSL https://cdn.jsdelivr.net/gh/munn19900917-eng/format-vanke-docx@main/install.sh | bash`，装完重启 Kimi 即可；之后说"按万科格式排一下这个 Word"会自动触发。

也可以手动执行：

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/munn19900917-eng/format-vanke-docx@main/install.sh | bash
```

## 版式

仿宋_GB2312 三号正文、方正小标宋简体二号标题、黑体三号部分标题、固定行距 28.95 磅、页边距上下 2.54cm 左右 3cm（与《万科集团综合住区项目命名管理办法（试行）》版式一致）。

## 依赖

python3（仅标准库）；字体：方正小标宋简体、仿宋_GB2312（未安装时会自动 fallback）。
