# SPDX-FileCopyrightText: 2025 PrepPipe's Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import os
import html
from typing import Dict, List, Any, Optional
from pathlib import Path

class HTMLReportGenerator:
  def __init__(self, content_json: Dict, diagnostic_json: Optional[Dict] = None):
    self.content_json = content_json
    self.diagnostic_json = diagnostic_json
    self.translations = {}  # 实际使用时需要填充翻译字典

  def get_translated_str(self, code: str) -> str:
    """获取翻译后的字符串"""
    return self.translations.get(code, code)

  def create_translatable(self, msg: str) -> str:
    """创建可翻译字符串代号（这里简单实现）"""
    return f"CUSTOM/{hash(msg)}"

  def generate_html(self) -> str:
    """生成完整的HTML报告"""
    html_parts = []

    # HTML头部
    html_parts.append(self._generate_header())

    # 主体结构
    html_parts.append('<div class="report-container">')

    # 左侧导航栏
    html_parts.append(self._generate_navigation())

    # 中间内容区域
    html_parts.append(self._generate_content_panel())

    # 右侧诊断面板
    html_parts.append(self._generate_diagnostic_panel())

    html_parts.append('</div>')  # 结束 report-container

    # JavaScript
    html_parts.append(self._generate_scripts())

    return '\n'.join(html_parts)

  def _generate_header(self) -> str:
    """生成HTML头部和CSS样式"""
    return f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>文档诊断报告</title>
  <style>
    /* 基础样式 */
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      background-color: #f5f5f5;
    }}

    .report-container {{
      display: flex;
      height: 100vh;
      overflow: hidden;
    }}

    /* 导航面板样式 */
    .navigation-panel {{
      width: 300px;
      background: #2c3e50;
      color: white;
      overflow-y: auto;
      border-right: 1px solid #34495e;
    }}

    .file-tree {{
      padding: 1rem;
    }}

    .file-item {{
      padding: 0.5rem;
      margin: 0.25rem 0;
      border-radius: 4px;
      cursor: pointer;
      transition: background-color 0.2s;
    }}

    .file-item:hover {{
      background: #34495e;
    }}

    .file-item.active {{
      background: #3498db;
    }}

    .diagnostic-counts {{
      display: flex;
      gap: 0.5rem;
      margin-top: 0.5rem;
      font-size: 0.8rem;
    }}

    .count-error {{ color: #e74c3c; }}
    .count-warning {{ color: #f39c12; }}
    .count-info {{ color: #3498db; }}

    .diagnostic-summary {{
      padding: 1rem;
      border-top: 1px solid #34495e;
    }}

    .summary-item {{
      display: flex;
      justify-content: space-between;
      margin: 0.5rem 0;
      padding: 0.5rem;
      border-radius: 4px;
    }}

    .summary-error {{ background: rgba(231, 76, 60, 0.2); }}
    .summary-warning {{ background: rgba(243, 156, 18, 0.2); }}
    .summary-info {{ background: rgba(52, 152, 219, 0.2); }}

    /* 内容面板样式 */
    .content-panel {{
      flex: 1;
      background: white;
      overflow-y: auto;
      padding: 1rem;
      border-right: 1px solid #ddd;
    }}

    .document-content {{
      max-width: 800px;
      margin: 0 auto;
    }}

    .paragraph {{
      margin: 1rem 0;
      padding: 0.5rem;
      position: relative;
    }}

    .paragraph:hover {{
      background: #f8f9fa;
    }}

    .line-number {{
      position: absolute;
      left: -3rem;
      width: 2.5rem;
      text-align: right;
      color: #6c757d;
      font-size: 0.8rem;
    }}

    .text {{
      display: inline;
      white-space: pre-wrap;
    }}

    .text.bold {{ font-weight: bold; }}
    .text.italic {{ font-style: italic; }}

    /* 诊断标记样式 */
    .diagnostic-highlight {{
      position: relative;
      display: inline;
    }}

    .diagnostic-marker {{
      position: absolute;
      top: -0.8rem;
      right: -0.5rem;
      font-size: 0.8rem;
      cursor: pointer;
      z-index: 10;
    }}

    .highlight-error {{
      background: rgba(231, 76, 60, 0.1);
      border-bottom: 2px wavy #e74c3c;
    }}

    .highlight-warning {{
      background: rgba(243, 156, 18, 0.1);
      border-bottom: 2px wavy #f39c12;
    }}

    .highlight-info {{
      background: rgba(52, 152, 219, 0.1);
      border-bottom: 2px wavy #3498db;
    }}

    /* 诊断面板样式 */
    .diagnostic-panel {{
      width: 400px;
      background: white;
      overflow-y: auto;
      border-left: 1px solid #ddd;
    }}

    .diagnostic-header {{
      padding: 1rem;
      background: #f8f9fa;
      border-bottom: 1px solid #ddd;
    }}

    .diagnostic-list {{
      padding: 1rem;
    }}

    .diagnostic-item {{
      padding: 1rem;
      margin: 0.5rem 0;
      border-radius: 6px;
      border-left: 4px solid;
      cursor: pointer;
    }}

    .diagnostic-item.error {{
      border-left-color: #e74c3c;
      background: rgba(231, 76, 60, 0.05);
    }}

    .diagnostic-item.warning {{
      border-left-color: #f39c12;
      background: rgba(243, 156, 18, 0.05);
    }}

    .diagnostic-item.info {{
      border-left-color: #3498db;
      background: rgba(52, 152, 219, 0.05);
    }}

    .diagnostic-item.active {{
      box-shadow: 0 0 0 2px currentColor;
    }}

    .diagnostic-severity {{
      display: inline-block;
      padding: 0.25rem 0.5rem;
      border-radius: 4px;
      font-size: 0.8rem;
      font-weight: bold;
      margin-bottom: 0.5rem;
    }}

    .severity-error {{ background: #e74c3c; color: white; }}
    .severity-warning {{ background: #f39c12; color: white; }}
    .severity-info {{ background: #3498db; color: white; }}

    .location-list {{
      margin-top: 0.5rem;
      font-size: 0.9rem;
      color: #6c757d;
    }}

    .location-item {{
      margin: 0.25rem 0;
      padding: 0.25rem;
      background: #f8f9fa;
      border-radius: 3px;
    }}

    /* 代码块和特殊块样式 */
    .codeblock {{
      background: #f8f9fa;
      border: 1px solid #e9ecef;
      border-radius: 4px;
      padding: 1rem;
      font-family: 'Courier New', monospace;
      white-space: pre-wrap;
      margin: 0.5rem 0;
    }}

    .centered {{
      text-align: center;
      font-style: italic;
      color: #6c757d;
      margin: 0.5rem 0;
    }}

    .assetref {{
      display: block;
      text-align: center;
      margin: 1rem 0;
      padding: 1rem;
      background: #f8f9fa;
      border: 1px dashed #dee2e6;
      border-radius: 4px;
    }}

    .list-item {{
      margin-left: 2rem;
      margin: 0.5rem 0;
    }}
  </style>
</head>
<body>
'''

  def _generate_navigation(self) -> str:
    """生成左侧导航栏"""
    files = self.content_json.get('files', [])
    diagnostic_summary = self._calculate_diagnostic_summary()

    html_parts = ['<div class="navigation-panel">']

    # 文件树
    html_parts.append('<div class="file-tree">')
    html_parts.append('<h3>文件</h3>')

    for i, file_data in enumerate(files):
      file_diagnostics = self._get_file_diagnostics(i)
      counts = self._count_diagnostics_by_severity(file_diagnostics)

      html_parts.append(f'''
      <div class="file-item" data-file-index="{i}">
        <div class="file-name">{html.escape(file_data.get('name', '未知文件'))}</div>
        <div class="diagnostic-counts">
          <span class="count-error">❌ {counts['error']}</span>
          <span class="count-warning">⚠️ {counts['warning']}</span>
          <span class="count-info">ℹ️ {counts['info']}</span>
        </div>
      </div>
      ''')

    html_parts.append('</div>')  # 结束 file-tree

    # 诊断摘要
    html_parts.append('<div class="diagnostic-summary">')
    html_parts.append('<h3>诊断摘要</h3>')

    for severity, count in diagnostic_summary.items():
      severity_class = f"summary-{severity}"
      html_parts.append(f'''
      <div class="summary-item {severity_class}">
        <span>{severity.upper()}</span>
        <span>{count}</span>
      </div>
      ''')

    html_parts.append('</div>')  # 结束 diagnostic-summary
    html_parts.append('</div>')  # 结束 navigation-panel

    return '\n'.join(html_parts)

  def _generate_content_panel(self) -> str:
    """生成中间内容面板"""
    html_parts = ['<div class="content-panel">']
    html_parts.append('<div class="document-content">')

    # 这里默认显示第一个文件，实际应该根据用户选择动态切换
    if self.content_json.get('files'):
      file_data = self.content_json['files'][0]
      html_parts.append(self._render_file_content(0, file_data))

    html_parts.append('</div>')  # 结束 document-content
    html_parts.append('</div>')  # 结束 content-panel

    return '\n'.join(html_parts)

  def _generate_diagnostic_panel(self) -> str:
    """生成右侧诊断面板"""
    html_parts = ['<div class="diagnostic-panel">']
    html_parts.append('<div class="diagnostic-header">')
    html_parts.append('<h3>诊断信息</h3>')
    html_parts.append('</div>')

    html_parts.append('<div class="diagnostic-list">')

    if self.diagnostic_json:
      nodes = self.diagnostic_json.get('nodes', [])
      nodekinds = self.diagnostic_json.get('nodekinds', [])

      for node in nodes:
        html_parts.append(self._render_diagnostic_item(node, nodekinds))
    else:
      html_parts.append('<p>没有诊断信息</p>')

    html_parts.append('</div>')  # 结束 diagnostic-list
    html_parts.append('</div>')  # 结束 diagnostic-panel

    return '\n'.join(html_parts)

  def _render_file_content(self, file_index: int, file_data: Dict) -> str:
    """渲染单个文件的内容"""
    html_parts = []
    body = file_data.get('body', [])

    html_parts.append(f'<h2>{html.escape(file_data.get("name", "未知文件"))}</h2>')
    html_parts.append(f'<p class="file-path"><small>{html.escape(file_data.get("path", ""))}</small></p>')

    for block_index, block in enumerate(body):
      html_parts.append(self._render_block(file_index, block_index, block))

    return '\n'.join(html_parts)

  def _render_block(self, file_index: int, block_index: int, block: List) -> str:
    """渲染单个块（段落）"""
    html_parts = []

    # 添加行号
    html_parts.append(f'<div class="paragraph" data-block="{block_index}">')
    html_parts.append(f'<span class="line-number">{block_index + 1}</span>')

    # 处理块内的元素
    if block and isinstance(block, list):
      first_element = block[0]

      if first_element.get('type') == 'list':
        # 列表块
        html_parts.append(self._render_list(file_index, block_index, first_element))
      elif first_element.get('type') == 'centered':
        # 居中文本
        content = html.escape(first_element.get('content', ''))
        html_parts.append(f'<div class="centered">{content}</div>')
      elif first_element.get('type') == 'codeblock':
        # 代码块
        content = html.escape(first_element.get('content', ''))
        html_parts.append(f'<pre class="codeblock">{content}</pre>')
      else:
        # 普通文本段落
        for element_index, element in enumerate(block):
          html_parts.append(self._render_element(file_index, block_index, element_index, element))

    html_parts.append('</div>')  # 结束 paragraph

    return '\n'.join(html_parts)

  def _render_element(self, file_index: int, block_index: int, element_index: int, element: Dict) -> str:
    """渲染单个元素"""
    element_type = element.get('type', 'text')

    if element_type == 'text':
      return self._render_text_element(file_index, block_index, element_index, element)
    elif element_type == 'assetref':
      return self._render_assetref_element(element)
    else:
      return f'<span>未知元素类型: {element_type}</span>'

  def _render_text_element(self, file_index: int, block_index: int, element_index: int, element: Dict) -> str:
    """渲染文本元素"""
    content = html.escape(element.get('content', ''))
    format_info = element.get('format', {})

    # 应用格式
    css_classes = []
    if format_info.get('bold'):
      css_classes.append('bold')
    if format_info.get('italic'):
      css_classes.append('italic')

    class_attr = f' class="{" ".join(css_classes)}"' if css_classes else ''

    # 检查是否有诊断信息
    diagnostics = self._get_element_diagnostics(file_index, block_index, element_index)

    if diagnostics:
      # 为每个诊断创建高亮区域
      highlighted_content = self._apply_diagnostic_highlights(content, diagnostics, element_index)
      return f'<span{class_attr}>{highlighted_content}</span>'
    else:
      return f'<span{class_attr}>{content}</span>'

  def _render_assetref_element(self, element: Dict) -> str:
    """渲染资源引用元素"""
    ref = element.get('ref', '')

    # 查找资源信息
    asset_info = None
    for asset in self.content_json.get('embedded', []):
      if asset.get('srcref') == ref:
        asset_info = asset
        break

    if asset_info:
      return f'''
      <div class="assetref">
        📷 图片引用: {html.escape(ref)}<br>
        <small>大小: {asset_info.get('size', ['?', '?'])[0]}x{asset_info.get('size', ['?', '?'])[1]}</small>
      </div>
      '''
    else:
      return f'<div class="assetref">📷 图片引用: {html.escape(ref)}</div>'

  def _render_list(self, file_index: int, block_index: int, list_element: Dict) -> str:
    """渲染列表"""
    html_parts = ['<ul>']

    for item_index, item in enumerate(list_element.get('items', [])):
      html_parts.append('<li class="list-item">')
      # 递归渲染列表项
      if isinstance(item, list):
        for sub_element in item:
          html_parts.append(self._render_element(file_index, block_index, item_index, sub_element))
      html_parts.append('</li>')

    html_parts.append('</ul>')
    return '\n'.join(html_parts)

  def _render_diagnostic_item(self, node: Dict, nodekinds: List) -> str:
    """渲染单个诊断项"""
    kind_id = node.get('kind', 0)
    nodekind = next((nk for nk in nodekinds if nk.get('id') == kind_id), {})

    severity = nodekind.get('severity', 'info')
    description = self.get_translated_str(nodekind.get('description', '未知诊断'))

    # 自定义消息（如果存在）
    custom_message = node.get('message')
    if custom_message:
      description = self.get_translated_str(custom_message)

    html_parts = []
    html_parts.append(f'<div class="diagnostic-item {severity}" data-node-id="{node.get("id")}">')

    # 严重性标签
    html_parts.append(f'<div class="diagnostic-severity severity-{severity}">{severity.upper()}</div>')

    # 诊断描述
    html_parts.append(f'<div class="diagnostic-description">{description}</div>')

    # 位置信息
    locations = node.get('locations', [])
    if locations:
      html_parts.append('<div class="location-list">')
      html_parts.append('<strong>位置:</strong>')
      for location in locations:
        loc_desc = self.get_translated_str(location.get('description', '位置'))
        html_parts.append(f'<div class="location-item">{loc_desc}</div>')
      html_parts.append('</div>')

    # 引用信息
    references = node.get('references', [])
    if references:
      html_parts.append('<div class="reference-list">')
      html_parts.append('<strong>相关诊断:</strong>')
      for ref in references:
        ref_desc = self.get_translated_str(ref.get('description', '引用'))
        ref_node_id = ref.get('node')
        html_parts.append(f'<div class="reference-item" data-ref-node="{ref_node_id}">{ref_desc}</div>')
      html_parts.append('</div>')

    html_parts.append('</div>')  # 结束 diagnostic-item

    return '\n'.join(html_parts)

  def _apply_diagnostic_highlights(self, content: str, diagnostics: List, element_index: int) -> str:
    """在文本内容上应用诊断高亮"""
    # 简化实现：为整个元素添加高亮
    # 实际应该根据具体的位置偏移量来精确高亮

    severity_classes = {
      'error': 'highlight-error',
      'warning': 'highlight-warning',
      'info': 'highlight-info'
    }

    # 使用最高严重性的诊断来决定高亮颜色
    max_severity = max(d.get('severity', 'info') for d in diagnostics)
    highlight_class = severity_classes.get(max_severity, 'highlight-info')

    diagnostic_ids = [str(d.get('id')) for d in diagnostics]
    diagnostic_icons = {
      'error': '❌',
      'warning': '⚠️',
      'info': 'ℹ️'
    }
    icon = diagnostic_icons.get(max_severity, 'ℹ️')

    return f'''
    <span class="diagnostic-highlight {highlight_class}" data-diagnostic-ids="{','.join(diagnostic_ids)}">
      {content}
      <span class="diagnostic-marker">{icon}</span>
    </span>
    '''

  def _calculate_diagnostic_summary(self) -> Dict[str, int]:
    """计算诊断摘要统计"""
    if not self.diagnostic_json:
      return {'error': 0, 'warning': 0, 'info': 0}

    summary = {'error': 0, 'warning': 0, 'info': 0}
    nodes = self.diagnostic_json.get('nodes', [])
    nodekinds = self.diagnostic_json.get('nodekinds', [])

    for node in nodes:
      kind_id = node.get('kind', 0)
      nodekind = next((nk for nk in nodekinds if nk.get('id') == kind_id), {})
      severity = nodekind.get('severity', 'info')
      summary[severity] = summary.get(severity, 0) + 1

    return summary

  def _get_file_diagnostics(self, file_index: int) -> List[Dict]:
    """获取指定文件的诊断信息"""
    if not self.diagnostic_json:
      return []

    file_diagnostics = []
    nodes = self.diagnostic_json.get('nodes', [])
    nodekinds = self.diagnostic_json.get('nodekinds', [])

    for node in nodes:
      locations = node.get('locations', [])
      for location in locations:
        if location.get('file') == file_index:
          kind_id = node.get('kind', 0)
          nodekind = next((nk for nk in nodekinds if nk.get('id') == kind_id), {})
          file_diagnostics.append({
            **node,
            'severity': nodekind.get('severity', 'info')
          })
          break

    return file_diagnostics

  def _get_element_diagnostics(self, file_index: int, block_index: int, element_index: int) -> List[Dict]:
    """获取指定元素的诊断信息"""
    if not self.diagnostic_json:
      return []

    element_diagnostics = []
    nodes = self.diagnostic_json.get('nodes', [])
    nodekinds = self.diagnostic_json.get('nodekinds', [])

    for node in nodes:
      locations = node.get('locations', [])
      for location in locations:
        loc_file = location.get('file')
        loc_block = location.get('block')
        loc_element = location.get('element')

        if (loc_file == file_index and
          loc_block == block_index and
          loc_element == element_index):

          kind_id = node.get('kind', 0)
          nodekind = next((nk for nk in nodekinds if nk.get('id') == kind_id), {})
          element_diagnostics.append({
            **node,
            'severity': nodekind.get('severity', 'info')
          })
          break

    return element_diagnostics

  def _count_diagnostics_by_severity(self, diagnostics: List[Dict]) -> Dict[str, int]:
    """按严重性统计诊断数量"""
    counts = {'error': 0, 'warning': 0, 'info': 0}
    for diagnostic in diagnostics:
      severity = diagnostic.get('severity', 'info')
      counts[severity] = counts.get(severity, 0) + 1
    return counts

  def _generate_scripts(self) -> str:
    """生成JavaScript代码"""
    return '''
<script>
// 文件切换功能
document.querySelectorAll('.file-item').forEach(item => {
  item.addEventListener('click', function() {
    // 移除所有active类
    document.querySelectorAll('.file-item').forEach(i => i.classList.remove('active'));
    // 添加active类到当前项
    this.classList.add('active');

    const fileIndex = this.dataset.fileIndex;
    // 这里应该加载对应文件的内容
    console.log('切换到文件:', fileIndex);
  });
});

// 诊断项点击功能
document.querySelectorAll('.diagnostic-item').forEach(item => {
  item.addEventListener('click', function() {
    // 移除所有active类
    document.querySelectorAll('.diagnostic-item').forEach(i => i.classList.remove('active'));
    // 添加active类到当前项
    this.classList.add('active');

    const nodeId = this.dataset.nodeId;
    // 高亮对应的文档位置
    highlightDiagnosticLocations(nodeId);
  });
});

// 诊断标记点击功能
document.querySelectorAll('.diagnostic-highlight').forEach(highlight => {
  highlight.addEventListener('click', function(e) {
    e.stopPropagation();
    const diagnosticIds = this.dataset.diagnosticIds.split(',');

    // 找到对应的诊断项并激活
    document.querySelectorAll('.diagnostic-item').forEach(item => {
      if (diagnosticIds.includes(item.dataset.nodeId)) {
        item.classList.add('active');
        item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        item.classList.remove('active');
      }
    });
  });
});

// 引用跳转功能
document.querySelectorAll('.reference-item').forEach(ref => {
  ref.addEventListener('click', function(e) {
    e.stopPropagation();
    const refNodeId = this.dataset.refNode;
    const targetItem = document.querySelector(`.diagnostic-item[data-node-id="${refNodeId}"]`);

    if (targetItem) {
      document.querySelectorAll('.diagnostic-item').forEach(i => i.classList.remove('active'));
      targetItem.classList.add('active');
      targetItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  });
});

function highlightDiagnosticLocations(nodeId) {
  // 移除所有高亮
  document.querySelectorAll('.diagnostic-highlight').forEach(el => {
    el.style.backgroundColor = '';
  });

  // 高亮当前诊断对应的位置
  const highlights = document.querySelectorAll(`[data-diagnostic-ids*="${nodeId}"]`);
  highlights.forEach(highlight => {
    highlight.style.backgroundColor = 'rgba(255, 255, 0, 0.3)';

    // 滚动到第一个高亮位置
    highlight.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
}

// 初始化：激活第一个文件
document.querySelector('.file-item')?.classList.add('active');
</script>
</body>
</html>
'''

def generate_report(content_json_path: str,
           diagnostic_json_path: Optional[str] = None,
           output_path: str = 'report.html') -> None:
  """生成HTML报告的主函数"""

  # 读取内容JSON
  with open(content_json_path, 'r', encoding='utf-8') as f:
    content_json = json.load(f)

  # 读取诊断JSON（如果提供）
  diagnostic_json = None
  if diagnostic_json_path and os.path.exists(diagnostic_json_path):
    with open(diagnostic_json_path, 'r', encoding='utf-8') as f:
      diagnostic_json = json.load(f)

  # 生成HTML报告
  generator = HTMLReportGenerator(content_json, diagnostic_json)
  html_content = generator.generate_html()

  # 保存报告
  with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

  print(f"HTML报告已生成: {output_path}")

# 使用示例
if __name__ == "__main__":
  # 示例用法
  generate_report(
    content_json_path='content.json',
    diagnostic_json_path='diagnostic.json',  # 可选
    output_path='diagnostic_report.html'
  )