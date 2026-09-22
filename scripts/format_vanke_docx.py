# -*- coding: utf-8 -*-
"""把 docx 重排为万科公文版式（仿宋_GB2312 三号 / 固定行距 579 缇 / 页边距上下2.54cm左右3cm）。

用法:
    python3 format_vanke_docx.py 输入.docx 输出.docx

规则（与《万科集团综合住区项目命名管理办法（试行）》参考件一致）:
- 文档标题(首个非空段): 方正小标宋简体 二号(44) 加粗 居中
- "第X部分…"          : 黑体 三号(32) 加粗 居中 outlineLvl 0
- "1.1 …" 数字节标题   : 仿宋_GB2312 三号 加粗 首行缩进2字符
- 短粗体子标题(≤45字,原带粗): 仿宋_GB2312 三号 加粗 首行缩进2字符
- 其余正文            : 仿宋_GB2312 三号 首行缩进2字符
- 表格单元格           : 仿宋_GB2312 五号(21), 首行加粗
- 行距: 全文固定值 579 缇(28.95磅); 清除所有高亮/彩色字
"""
import re, sys, zipfile, shutil, os

def rpr(font, sz, bold):
    b = '<w:b/>' if bold else ''
    return f'<w:rPr>{font}{b}<w:sz w:val="{sz}"/><w:szCs w:val="28"/></w:rPr>'

def ppr(jc=None, indent=False, keep=False, outline=False):
    s = '<w:pPr>'
    if keep: s += '<w:keepNext/>'
    s += '<w:spacing w:line="579" w:lineRule="exact"/>'
    if indent: s += '<w:ind w:firstLineChars="200" w:firstLine="640"/>'
    if jc: s += f'<w:jc w:val="{jc}"/>'
    if outline: s += '<w:outlineLvl w:val="0"/>'
    s += '</w:pPr>'
    return s

def tx(p):
    return ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))

def set_runs(p, font, sz, bold):
    def fix_run(m):
        r = m.group(0)
        inner = re.sub(r'<w:rPr>.*?</w:rPr>', '', r, flags=re.S)
        inner = re.sub(r'<w:rPr/>', '', inner)
        nr = rpr(font, sz, bold)
        return re.sub(r'<w:r\b[^>]*>', lambda mm: mm.group(0) + nr, inner, count=1)
    return re.sub(r'<w:r\b(?:(?!</w:r>).)*</w:r>', fix_run, p, flags=re.S)

def set_ppr(p, newppr):
    if re.search(r'<w:pPr>.*?</w:pPr>', p, re.S):
        return re.sub(r'<w:pPr>.*?</w:pPr>', newppr, p, count=1, flags=re.S)
    if '<w:pPr/>' in p:
        return p.replace('<w:pPr/>', newppr, 1)
    return re.sub(r'<w:p\b[^>]*>', lambda mm: mm.group(0) + newppr, p, count=1)

def make_bold(p):
    if '<w:b/>' in p:
        return p
    return re.sub(r'(<w:rPr><w:rFonts[^/]*/>)', r'\1<w:b/>', p, count=1)

FS = '<w:rFonts w:ascii="仿宋_GB2312" w:eastAsia="仿宋_GB2312" w:hAnsi="仿宋" w:cs="仿宋"/>'
HT = '<w:rFonts w:ascii="黑体" w:eastAsia="黑体" w:hAnsi="黑体"/>'
XB = '<w:rFonts w:ascii="方正小标宋简体" w:eastAsia="方正小标宋简体" w:hAnsi="仿宋"/>'

# 正文前缀: 以这些开头的粗体段落视为正文而非标题
BODY_PREFIX = ('20', '判读', '由头', '结果', '归因', '节奏', '汇总', '收口', '附：', '附:')

def fix_table(t):
    def cellp(cm):
        cp = cm.group(0)
        cp = set_ppr(cp, '<w:pPr><w:spacing w:line="360" w:lineRule="auto"/></w:pPr>')
        return set_runs(cp, FS, 21, False)
    t = re.sub(r'<w:p\b(?:(?!</w:p>).)*</w:p>', cellp, t, flags=re.S)
    # 首行(表头)加粗
    mrow = re.search(r'<w:tr\b.*?</w:tr>', t, re.S)
    if mrow:
        t = t.replace(mrow.group(0), make_bold(mrow.group(0)), 1)
    return t

def fix_para_factory(title_text):
    state = {'title_done': False}
    def fix_para(m):
        p = m.group(0)
        t = tx(p).strip()
        if not t:
            return set_ppr(p, ppr())
        if not state['title_done']:
            state['title_done'] = True
            return set_runs(set_ppr(p, ppr(jc='center')), XB, 44, True)
        if re.match(r'^第[一二三四五六七八九十]+部分', t):
            return set_runs(set_ppr(p, ppr(jc='center', keep=True, outline=True)), HT, 32, True)
        if re.match(r'^\d+\.\d+\s', t):
            return set_runs(set_ppr(p, ppr(indent=True, keep=True)), FS, 32, True)
        is_bold = bool(re.search(r'<w:rPr>(?:(?!</w:rPr>).)*?<w:b/>', p, re.S))
        if is_bold and len(t) <= 45 and not t.startswith(BODY_PREFIX) and not t.endswith('。'):
            return set_runs(set_ppr(p, ppr(indent=True, keep=True)), FS, 32, True)
        return set_runs(set_ppr(p, ppr(indent=True)), FS, 32, False)
    return fix_para

def fix_subheads(m):
    p = m.group(0)
    t = tx(p).strip()
    if re.match(r'^([A-Z]\d\s|[一二三四五六七八九十]+、|信任线|产品线|场景线)', t):
        p = set_ppr(p, ppr(indent=True, keep=True))
        if '<w:b/>' not in p:
            p = make_bold(p)
    return p

NEW_SECT = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1440" w:right="1701" w:bottom="1440" w:left="1701" '
            'w:header="851" w:footer="992" w:gutter="0"/>'
            '<w:cols w:num="1" w:space="425"/>'
            '<w:docGrid w:type="lines" w:linePitch="291"/></w:sectPr>')

def transform(document_xml):
    x = document_xml
    parts = re.split(r'(<w:tbl>.*?</w:tbl>)', x, flags=re.S)
    for i, seg in enumerate(parts):
        if seg.startswith('<w:tbl>'):
            parts[i] = fix_table(seg)
        else:
            seg = re.sub(r'<w:p\b(?:(?!</w:p>).)*</w:p>', fix_para_factory(None), seg, flags=re.S)
            parts[i] = re.sub(r'<w:p\b(?:(?!</w:p>).)*</w:p>', fix_subheads, seg, flags=re.S)
    x = ''.join(parts)
    # 保留原有页眉/页脚引用,仅替换页面几何与网格
    m = re.search(r'<w:sectPr>.*?</w:sectPr>', x, re.S)
    if m:
        keep = ''.join(re.findall(r'<w:(?:headerReference|footerReference)[^>]*/>', m.group(0)))
        x = x.replace(m.group(0), '<w:sectPr>' + keep +
                      NEW_SECT[len('<w:sectPr>'):-len('</w:sectPr>')] + '</w:sectPr>', 1)
    return x

def main():
    if len(sys.argv) != 3:
        print(__doc__); sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]
    zin = zipfile.ZipFile(src)
    doc = zin.read('word/document.xml').decode('utf8')
    new_doc = transform(doc)
    if os.path.exists(dst):
        os.remove(dst)
    zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename == 'word/document.xml':
            data = new_doc.encode('utf8')
        zout.writestr(item, data)
    zout.close(); zin.close()
    n579 = new_doc.count('w:line="579"')
    print(f'OK -> {dst}  (固定行距段落 {n579} 个, 高亮残留 {new_doc.count("highlight")})')

if __name__ == '__main__':
    main()
