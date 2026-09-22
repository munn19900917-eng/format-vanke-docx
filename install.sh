#!/usr/bin/env bash
# format-vanke-docx 技能一键安装脚本（万科公文 Word 排版）
# 用法: curl -fsSL https://raw.githubusercontent.com/munn19900917-eng/format-vanke-docx/main/install.sh | bash
set -euo pipefail

SKILL_NAME="format-vanke-docx"
RAW_PRIMARY="https://raw.githubusercontent.com/munn19900917-eng/format-vanke-docx/main"
RAW_MIRROR="https://cdn.jsdelivr.net/gh/munn19900917-eng/format-vanke-docx@main"

# 1. 确定 skills 目录（按常见客户端优先级，默认 ~/.config/agents/skills）
SKILLS_DIR=""
for d in "$HOME/.config/agents/skills" "$HOME/.kimi/skills" "$HOME/.claude/skills"; do
  if [ -d "$d" ]; then SKILLS_DIR="$d"; break; fi
done
[ -n "$SKILLS_DIR" ] || SKILLS_DIR="$HOME/.config/agents/skills"
DEST="$SKILLS_DIR/$SKILL_NAME"
mkdir -p "$DEST/scripts"

# 2. 下载技能文件（GitHub raw 优先，国内走 jsdelivr 镜像兜底）
fetch() {
  local path="$1"
  curl -fsSL --connect-timeout 8 "$RAW_PRIMARY/$path" -o "$DEST/$path" 2>/dev/null \
    || curl -fsSL --connect-timeout 8 "$RAW_MIRROR/$path" -o "$DEST/$path"
}
echo "安装 $SKILL_NAME ..."
fetch "SKILL.md"
fetch "scripts/format_vanke_docx.py"

# 3. 校验并收尾
if [ ! -s "$DEST/SKILL.md" ] || [ ! -s "$DEST/scripts/format_vanke_docx.py" ]; then
  echo "下载不完整，请检查网络后重试" >&2; exit 1
fi
chmod +x "$DEST/scripts/format_vanke_docx.py" 2>/dev/null || true

echo "✅ $SKILL_NAME 已安装到 $DEST"
echo "重启 Kimi / Agent 后生效；之后说「按万科格式排一下这个 Word」即可自动使用。"
