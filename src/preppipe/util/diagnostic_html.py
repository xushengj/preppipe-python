# SPDX-FileCopyrightText: 2025 PrepPipe's Contributors
# SPDX-License-Identifier: Apache-2.0

# !!!WIP!!! DeepSeek 写的，还没完善

import dataclasses
import typing
import html
import json
import os

@dataclasses.dataclass
class DiagnosticLocation:
  """诊断位置信息"""
  type: str = "text"  # 'text', 'block', 'element', 'asset'
  file_index: int = 0
  block_index: typing.Optional[int] = None
  element_index: typing.Optional[int] = None
  start_offset: typing.Optional[int] = None
  end_offset: typing.Optional[int] = None
  description: str = ""

@dataclasses.dataclass
class DiagnosticReference:
  """诊断引用关系"""
  node_id: int = 0
  description: str = ""

@dataclasses.dataclass
class DiagnosticNode:
  """诊断节点"""
  id: int = 0
  kind_id: int = 0
  severity: str = "info"  # 'error', 'warning', 'info'
  description: str = ""
  message: str = ""  # 可选的自定义消息
  locations: list[DiagnosticLocation] = dataclasses.field(default_factory=list)
  references: list[DiagnosticReference] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class TextElement:
  """文本元素"""
  type: str = "text"
  content: str = ""
  format: dict[str, typing.Any] = dataclasses.field(default_factory=dict)
  diagnostics: list[DiagnosticNode] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class AssetRefElement:
  """资源引用元素"""
  type: str = "assetref"
  ref: str = ""
  asset_info: typing.Optional[dict[str, typing.Any]] = None

@dataclasses.dataclass
class Paragraph:
  """段落，包含多个元素"""
  elements: list[typing.Any] = dataclasses.field(default_factory=list)  # TextElement, AssetRefElement 等
  block_index: int = 0
  diagnostics: list[DiagnosticNode] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class SpecialBlock:
  """特殊块（居中、代码块等）"""
  type: str  # 'centered', 'codeblock'
  content: str = ""
  diagnostics: list[DiagnosticNode] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class ListBlock:
  """列表块"""
  type: str = "list"
  items: list['Paragraph'] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class FileContent:
  """文件内容"""
  name: str = ""
  path: str = ""
  paragraphs: list[Paragraph] = dataclasses.field(default_factory=list)
  diagnostics: list[DiagnosticNode] = dataclasses.field(default_factory=list)

@dataclasses.dataclass
class DiagnosticKind:
  """诊断类型定义"""
  id: int = 0
  severity: str = "info"
  code: str = ""
  description: str = ""

@dataclasses.dataclass
class NavigationItem:
  """导航项"""
  file_index: int = 0
  name: str = ""
  path: str = ""
  diagnostic_counts: dict[str, int] = dataclasses.field(default_factory=dict)  # {'error': 0, 'warning': 0, 'info': 0}

@dataclasses.dataclass
class ReportData:
  """完整的报告数据"""
  files: list[FileContent] = dataclasses.field(default_factory=list)
  diagnostic_kinds: list[DiagnosticKind] = dataclasses.field(default_factory=list)
  diagnostic_nodes: list[DiagnosticNode] = dataclasses.field(default_factory=list)
  navigation: list[NavigationItem] = dataclasses.field(default_factory=list)
  diagnostic_summary: dict[str, int] = dataclasses.field(default_factory=dict)  # {'error': 0, 'warning': 0, 'info': 0}

class HTMLExporter:
  def generate_html(self, report_data: ReportData) -> str:
    """HTML导出部分 - 只负责简单的字符串拼接"""

    # 1. 生成基础HTML结构
    html_parts = [
      self._generate_header(),
      '<div class="report-container">',
      self._generate_navigation(report_data.navigation, report_data.diagnostic_summary),
      self._generate_content_panel(report_data.files),
      self._generate_diagnostic_panel(report_data.diagnostic_nodes),
      '</div>',
      self._generate_scripts(),
      '</body></html>'
    ]
    return '\n'.join(html_parts)

  def _generate_navigation(self, navigation, summary):
    """生成导航栏 - 只需要遍历navigation列表"""
    html_parts = ['<div class="navigation-panel">']

    # 文件列表 - 简单遍历
    for nav_item in navigation:
      html_parts.append(f'''
      <div class="file-item" data-file-index="{nav_item.file_index}">
        <div class="file-name">{html.escape(nav_item.name)}</div>
        <div class="diagnostic-counts">
          <span class="count-error">❌ {nav_item.diagnostic_counts['error']}</span>
          <span class="count-warning">⚠️ {nav_item.diagnostic_counts['warning']}</span>
          <span class="count-info">ℹ️ {nav_item.diagnostic_counts['info']}</span>
        </div>
      </div>
      ''')

    # 诊断摘要 - 直接使用预计算的数据
    html_parts.append('<div class="diagnostic-summary">')
    for severity, count in summary.items():
      html_parts.append(f'''
      <div class="summary-item summary-{severity}">
        <span>{severity.upper()}</span>
        <span>{count}</span>
      </div>
      ''')
    html_parts.append('</div></div>')

    return '\n'.join(html_parts)

  def _generate_content_panel(self, files):
    """生成内容面板 - 只需要递归遍历文件结构"""
    html_parts = ['<div class="content-panel"><div class="document-content">']

    for file in files:
      html_parts.append(f'<h2>{html.escape(file.name)}</h2>')
      for paragraph in file.paragraphs:
        html_parts.append(self._render_paragraph(paragraph))

    html_parts.append('</div></div>')
    return '\n'.join(html_parts)

  def _render_paragraph(self, paragraph):
    """渲染段落 - 只需要处理预关联的诊断信息"""
    html_parts = [f'<div class="paragraph" data-block="{paragraph.block_index}">']
    html_parts.append(f'<span class="line-number">{paragraph.block_index + 1}</span>')

    for element in paragraph.elements:
      if isinstance(element, TextElement):
        html_parts.append(self._render_text_element(element))
      elif element.type == 'assetref':
        html_parts.append(self._render_assetref_element(element))
      # 其他元素类型...

    html_parts.append('</div>')
    return '\n'.join(html_parts)

  def _render_text_element(self, element):
    """渲染文本元素 - 诊断信息已经预关联"""
    content = html.escape(element.content)

    # 格式类
    style = []
    if element.format.get('bold'):
      style.append('font-weight: bold;')
    if element.format.get('italic'):
      style.append('font-style: italic;')

    style_str = f' style="{" ".join(style)}"' if style else ''

    # 诊断高亮 - 如果有诊断信息
    if element.diagnostics:
      severity = max(d.severity for d in element.diagnostics)
      diagnostic_ids = ','.join(str(d.id) for d in element.diagnostics)
      return f'''
      <span{style_str} class="diagnostic-highlight highlight-{severity}"
          data-diagnostic-ids="{diagnostic_ids}">
        {content}
        <span class="diagnostic-marker">{self._get_severity_icon(severity)}</span>
      </span>
      '''
    else:
      return f'<span{style_str}>{content}</span>'

  def _get_severity_icon(self, severity: str) -> str:
    """根据严重性返回对应的图标"""
    icons = {
      'error': '❌',    # 红色叉号
      'warning': '⚠️',  # 黄色警告三角
      'info': 'ℹ️'      # 蓝色信息图标
    }
    return icons.get(severity, '🔍')  # 默认可视化图标

  def _escape(self, text: str) -> str:
    """HTML转义"""
    return html.escape(text)

  def _render_assetref_element(self, element) -> str:
    """渲染资源引用元素"""
    ref = element.ref
    asset_info = element.asset_info

    if asset_info:
      # 如果有完整的资源信息
      size = asset_info.get('size', ['?', '?'])
      width, height = size if len(size) == 2 else ('?', '?')

      return f'''
      <div class="assetref" data-asset-ref="{self._escape(ref)}">
          <div class="asset-icon">🖼️</div>
          <div class="asset-info">
              <div class="asset-name">{self._escape(ref)}</div>
              <div class="asset-details">
                  图片引用 | 尺寸: {width}×{height}px
              </div>
          </div>
      </div>
      '''
    else:
      # 如果只有引用路径，没有完整的资源信息
      return f'''
      <div class="assetref" data-asset-ref="{self._escape(ref)}">
          <div class="asset-icon">🖼️</div>
          <div class="asset-info">
              <div class="asset-name">{self._escape(ref)}</div>
              <div class="asset-details">图片引用</div>
          </div>
      </div>
      '''

  def _generate_diagnostic_panel(self, diagnostic_nodes: list[DiagnosticNode]) -> str:
    """生成右侧诊断面板"""
    html_parts = [
      '<div class="diagnostic-panel">',
      '<div class="diagnostic-header">',
      '<h3>诊断信息</h3>',
      '</div>',
      '<div class="diagnostic-list">'
    ]

    if diagnostic_nodes:
      # 按严重性排序：错误 -> 警告 -> 信息
      sorted_nodes = sorted(diagnostic_nodes,
                key=lambda node: {'error': 0, 'warning': 1, 'info': 2}.get(node.severity, 3))

      for node in sorted_nodes:
        html_parts.append(self._render_diagnostic_item(node))
    else:
      html_parts.append('''
      <div class="no-diagnostics">
        <div class="no-diagnostics-icon">✅</div>
        <div class="no-diagnostics-text">没有发现诊断问题</div>
      </div>
      ''')

    html_parts.extend([
      '</div>',  # 结束 diagnostic-list
      '</div>'   # 结束 diagnostic-panel
    ])

    return '\n'.join(html_parts)

  def _render_diagnostic_item(self, node: DiagnosticNode) -> str:
    """渲染单个诊断项"""
    # 使用自定义消息（如果有），否则使用类型描述
    display_message = node.message if node.message else node.description

    html_parts = [
      f'<div class="diagnostic-item {node.severity}" data-node-id="{node.id}">',
      f'<div class="diagnostic-severity severity-{node.severity}">{node.severity.upper()}</div>',
      f'<div class="diagnostic-description">{self._escape(display_message)}</div>'
    ]

    # 位置信息
    if node.locations:
      html_parts.append('<div class="location-list">')
      html_parts.append('<div class="location-title">位置:</div>')
      for location in node.locations:
        location_text = self._format_location_text(location)
        html_parts.append(f'<div class="location-item">{self._escape(location_text)}</div>')
      html_parts.append('</div>')

    # 引用关系
    if node.references:
      html_parts.append('<div class="reference-list">')
      html_parts.append('<div class="reference-title">相关诊断:</div>')
      for ref in node.references:
        ref_text = ref.description if ref.description else f"诊断 #{ref.node_id}"
        html_parts.append(
          f'<div class="reference-item" data-ref-node="{ref.node_id}">'
          f'{self._escape(ref_text)}'
          f'</div>'
        )
      html_parts.append('</div>')

    html_parts.append('</div>')  # 结束 diagnostic-item

    return '\n'.join(html_parts)

  def _format_location_text(self, location: DiagnosticLocation) -> str:
    """格式化位置信息为可读文本"""
    location_type = location.type

    if location_type == 'text' and location.block_index is not None:
      return f"第{location.block_index + 1}段"
    elif location_type == 'block' and location.block_index is not None:
      return f"第{location.block_index + 1}段"
    elif location_type == 'element' and location.element_index is not None:
      return f"第{location.element_index + 1}个元素"
    elif location_type == 'asset':
      return f"资源: {location.description}" if location.description else "资源引用"
    else:
      return location.description if location.description else "未知位置"

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
# ==============================================================================

class ReportDataReader:
  """读取JSON文件并转换为ReportData结构的类"""

  def __init__(self):
    self.content_data = None
    self.diagnostic_data = None
    self.report_data = ReportData()

  def load_files(self, content_json_path: str, diagnostic_json_path: typing.Optional[str] = None) -> None:
    """加载内容JSON和可选的诊断JSON文件"""
    # 加载内容JSON
    with open(content_json_path, 'r', encoding='utf-8') as f:
      self.content_data = json.load(f)

    # 加载诊断JSON（如果提供）
    if diagnostic_json_path:
      with open(diagnostic_json_path, 'r', encoding='utf-8') as f:
        self.diagnostic_data = json.load(f)
    else:
      print(f"诊断JSON文件不存在或未提供: {diagnostic_json_path}")
      self.diagnostic_data = None

  def build_report_data(self) -> ReportData:
    """构建完整的ReportData结构"""
    if not self.content_data:
      raise ValueError("未加载内容数据，请先调用load_files方法")

    # 处理诊断数据
    self._process_diagnostic_data()

    # 处理内容数据
    self._process_content_data()

    # 建立诊断关联
    self._associate_diagnostics()

    # 构建导航数据
    self._build_navigation()

    # 计算诊断摘要
    self._calculate_summary()

    return self.report_data

  def _process_diagnostic_data(self) -> None:
    """处理诊断JSON数据"""
    if not self.diagnostic_data:
      return

    # 处理诊断类型
    for kind_data in self.diagnostic_data.get('nodekinds', []):
      kind = DiagnosticKind(
        id=kind_data.get('id', 0),
        severity=kind_data.get('severity', 'info'),
        code=kind_data.get('code', ''),
        description=kind_data.get('description', '')
      )
      self.report_data.diagnostic_kinds.append(kind)

    # 处理诊断节点
    for node_data in self.diagnostic_data.get('nodes', []):
      # 获取对应的诊断类型
      kind_id = node_data.get('kind', 0)
      kind = next((k for k in self.report_data.diagnostic_kinds if k.id == kind_id), None)
      severity = kind.severity if kind else 'info'
      description = kind.description if kind else ''

      # 处理位置信息
      locations = []
      for loc_data in node_data.get('locations', []):
        location = DiagnosticLocation(
          type=loc_data.get('type', 'text'),
          file_index=loc_data.get('file', 0),
          block_index=loc_data.get('block'),
          element_index=loc_data.get('element'),
          start_offset=loc_data.get('start_offset'),
          end_offset=loc_data.get('end_offset'),
          description=loc_data.get('description', '')
        )
        locations.append(location)

      # 处理引用关系
      references = []
      for ref_data in node_data.get('references', []):
        # 处理新的引用格式
        if isinstance(ref_data, dict):
          reference = DiagnosticReference(
            node_id=ref_data.get('node'),
            description=ref_data.get('description', '')
          )
        # 处理旧的引用格式（直接是节点ID）
        else:
          reference = DiagnosticReference(node_id=ref_data)
        references.append(reference)

      node = DiagnosticNode(
        id=node_data.get('id', len(self.report_data.diagnostic_nodes)),
        kind_id=kind_id,
        severity=severity,
        description=description,
        message=node_data.get('message', ''),
        locations=locations,
        references=references
      )
      self.report_data.diagnostic_nodes.append(node)

  def _process_content_data(self) -> None:
    """处理内容JSON数据"""
    if not self.content_data:
      return

    # 处理文件内容
    for file_index, file_data in enumerate(self.content_data.get('files', [])):
      file_content = FileContent(
        name=file_data.get('name', ''),
        path=file_data.get('path', '')
      )

      # 处理文件体内容
      body = file_data.get('body', [])
      for block_index, block_data in enumerate(body):
        paragraph = self._process_block(block_index, block_data)
        file_content.paragraphs.append(paragraph)

      self.report_data.files.append(file_content)

    # 构建资源引用映射表，用于后续关联
    self._build_asset_mapping()

  def _process_block(self, block_index: int, block_data: list) -> Paragraph:
    """处理单个块数据"""
    paragraph = Paragraph(block_index=block_index)

    # 空块处理
    if not block_data:
      return paragraph

    # 检查是否为特殊块（第一个元素决定块类型）
    first_element = block_data[0] if isinstance(block_data, list) and block_data else {}

    if first_element.get('type') == 'list':
      # 列表块
      list_element = self._process_list_block(block_data[0])
      paragraph.elements.append(list_element)
    elif first_element.get('type') in ['centered', 'codeblock']:
      # 特殊块（居中文本、代码块）
      special_block = self._process_special_block(first_element)
      paragraph.elements.append(special_block)
    else:
      # 普通段落，包含多个元素
      for element_index, element_data in enumerate(block_data):
        element = self._process_element(element_data)
        paragraph.elements.append(element)

    return paragraph

  def _process_list_block(self, list_data: dict) -> ListBlock:
    """处理列表块"""
    list_block = ListBlock()

    for item_data in list_data.get('items', []):
      # 列表项本身是一个BodyScope，递归处理
      if isinstance(item_data, list):
        # 创建一个虚拟段落来保存列表项内容
        item_paragraph = Paragraph()
        for element_data in item_data:
          element = self._process_element(element_data)
          item_paragraph.elements.append(element)
        list_block.items.append(item_paragraph)

    return list_block

  def _process_special_block(self, element_data: dict) -> SpecialBlock:
    """处理特殊块（居中文本、代码块）"""
    return SpecialBlock(
      type=element_data.get('type', ''),
      content=element_data.get('content', '')
    )

  def _process_element(self, element_data: dict) -> typing.Any:
    """处理单个元素"""
    element_type = element_data.get('type', 'text')

    if element_type == 'text':
      return TextElement(
        content=element_data.get('content', ''),
        format=element_data.get('format', {})
      )
    elif element_type == 'assetref':
      return AssetRefElement(
        ref=element_data.get('ref', '')
      )
    else:
      # 未知元素类型，创建基础文本元素
      return TextElement(
        content=f"[未知元素类型: {element_type}]",
        format={}
      )

  def _build_asset_mapping(self) -> None:
    """构建资源引用映射表"""
    self.asset_mapping = {}
    for asset_data in self.content_data.get('embedded', []):
      srcref = asset_data.get('srcref')
      if srcref:
        self.asset_mapping[srcref] = asset_data

  def _associate_diagnostics(self) -> None:
    """将诊断信息关联到对应的文件、段落和元素"""
    if not self.diagnostic_data:
      return

    # 为资源引用元素关联资源信息
    self._associate_asset_info()

    # 关联诊断到具体位置
    for diagnostic in self.report_data.diagnostic_nodes:
      for location in diagnostic.locations:
        file_index = location.file_index
        if file_index < len(self.report_data.files):
          file = self.report_data.files[file_index]

          # 如果诊断尚未关联到文件，则关联
          if diagnostic not in file.diagnostics:
            file.diagnostics.append(diagnostic)

          # 关联到段落级别
          block_index = location.block_index
          if block_index is not None and block_index < len(file.paragraphs):
            paragraph = file.paragraphs[block_index]
            if diagnostic not in paragraph.diagnostics:
              paragraph.diagnostics.append(diagnostic)

            # 关联到元素级别
            element_index = location.element_index
            if (element_index is not None and
              element_index < len(paragraph.elements)):
              element = paragraph.elements[element_index]
              if hasattr(element, 'diagnostics'):
                if diagnostic not in element.diagnostics:
                  element.diagnostics.append(diagnostic)

  def _associate_asset_info(self) -> None:
    """为资源引用元素关联完整的资源信息"""
    for file in self.report_data.files:
      for paragraph in file.paragraphs:
        for element in paragraph.elements:
          if (isinstance(element, AssetRefElement) and
            hasattr(self, 'asset_mapping')):
            asset_info = self.asset_mapping.get(element.ref)
            if asset_info:
              element.asset_info = asset_info

  def _build_navigation(self) -> None:
    """构建导航数据"""
    for file_index, file in enumerate(self.report_data.files):
      # 计算每个文件的诊断统计
      counts = {'error': 0, 'warning': 0, 'info': 0}
      for diagnostic in file.diagnostics:
        counts[diagnostic.severity] = counts.get(diagnostic.severity, 0) + 1

      nav_item = NavigationItem(
        file_index=file_index,
        name=file.name,
        path=file.path,
        diagnostic_counts=counts
      )
      self.report_data.navigation.append(nav_item)

  def _calculate_summary(self) -> None:
    """计算诊断摘要统计"""
    summary = {'error': 0, 'warning': 0, 'info': 0}
    for diagnostic in self.report_data.diagnostic_nodes:
      summary[diagnostic.severity] = summary.get(diagnostic.severity, 0) + 1
    self.report_data.diagnostic_summary = summary

# ==============================================================================

def main():
  """测试HTMLExporter的主函数，直接填充dataclass进行测试"""

  # 创建测试数据
  report_data = create_test_report_data()

  # 生成HTML
  exporter = HTMLExporter()
  html_content = exporter.generate_html(report_data)

  # 保存测试文件
  with open('test_report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

  print("测试报告已生成: test_report.html")
  print(f"包含 {len(report_data.files)} 个文件")
  print(f"包含 {len(report_data.diagnostic_nodes)} 个诊断项")

def create_test_report_data():
  """创建测试用的ReportData"""

  # 创建诊断类型
  error_kind = DiagnosticKind(
    id=0,
    severity="error",
    code="TEST/SyntaxError",
    description="语法错误：缺少必要的标点符号"
  )

  warning_kind = DiagnosticKind(
    id=1,
    severity="warning",
    code="TEST/UnusedVariable",
    description="未使用的变量"
  )

  info_kind = DiagnosticKind(
    id=2,
    severity="info",
    code="TEST/NoteInfo",
    description="相关信息说明"
  )

  # 创建诊断位置
  error_location = DiagnosticLocation(
    type="text",
    file_index=0,
    block_index=0,
    element_index=0,
    start_offset=0,
    end_offset=5,
    description="命令名称位置"
  )

  warning_location = DiagnosticLocation(
    type="text",
    file_index=0,
    block_index=1,
    element_index=1,
    start_offset=2,
    end_offset=8,
    description="参数值位置"
  )

  info_location = DiagnosticLocation(
    type="block",
    file_index=0,
    block_index=2,
    description="相关定义位置"
  )

  # 创建诊断节点
  error_node = DiagnosticNode(
    id=0,
    kind_id=0,
    severity="error",
    description="语法错误：缺少必要的标点符号",
    locations=[error_location],
    references=[DiagnosticReference(node_id=2, description="相关说明")]
  )

  warning_node = DiagnosticNode(
    id=1,
    kind_id=1,
    severity="warning",
    description="未使用的变量：player_name",
    locations=[warning_location]
  )

  info_node = DiagnosticNode(
    id=2,
    kind_id=2,
    severity="info",
    description="角色player已在场景start中声明",
    locations=[info_location]
  )

  # 创建文本元素（带诊断）
  error_text = TextElement(
    content="场景开始",
    format={"bold": True},
    diagnostics=[error_node]
  )

  normal_text = TextElement(
    content="这是一个测试文档，包含各种内容元素。",
    format={}
  )

  warning_text = TextElement(
    content="显示角色player_name",
    format={},
    diagnostics=[warning_node]
  )

  italic_text = TextElement(
    content="斜体文本示例",
    format={"italic": True}
  )

  bold_text = TextElement(
    content="加粗文本示例",
    format={"bold": True}
  )

  # 创建资源引用元素
  asset_element = AssetRefElement(
    ref="background.png",
    asset_info={
      "size": [1920, 1080],
      "bbox": [0, 0, 1920, 1080]
    }
  )

  # 创建特殊块
  centered_block = SpecialBlock(
    type="centered",
    content="图1：场景示意图"
  )

  code_block = SpecialBlock(
    type="codeblock",
    content="function test() {\n  return 'Hello World';\n}"
  )

  # 创建段落
  paragraph1 = Paragraph(
    elements=[error_text, normal_text],
    block_index=0,
    diagnostics=[error_node]
  )

  paragraph2 = Paragraph(
    elements=[warning_text, italic_text, bold_text],
    block_index=1,
    diagnostics=[warning_node]
  )

  paragraph3 = Paragraph(
    elements=[asset_element],
    block_index=2
  )

  paragraph4 = Paragraph(
    elements=[centered_block],
    block_index=3
  )

  paragraph5 = Paragraph(
    elements=[code_block],
    block_index=4
  )

  # 创建文件内容
  file1 = FileContent(
    name="测试场景",
    path="scenes/test_scene.docx",
    paragraphs=[paragraph1, paragraph2, paragraph3, paragraph4, paragraph5],
    diagnostics=[error_node, warning_node, info_node]
  )

  file2 = FileContent(
    name="角色定义",
    path="characters/player.docx",
    paragraphs=[
      Paragraph(
        elements=[TextElement(content="角色定义文件，没有诊断问题。")],
        block_index=0
      )
    ],
    diagnostics=[]
  )

  # 创建导航项
  nav1 = NavigationItem(
    file_index=0,
    name="测试场景",
    path="scenes/test_scene.docx",
    diagnostic_counts={"error": 1, "warning": 1, "info": 1}
  )

  nav2 = NavigationItem(
    file_index=1,
    name="角色定义",
    path="characters/player.docx",
    diagnostic_counts={"error": 0, "warning": 0, "info": 0}
  )

  # 创建完整的报告数据
  report_data = ReportData(
    files=[file1, file2],
    diagnostic_kinds=[error_kind, warning_kind, info_kind],
    diagnostic_nodes=[error_node, warning_node, info_node],
    navigation=[nav1, nav2],
    diagnostic_summary={"error": 1, "warning": 1, "info": 1}
  )

  return report_data

if __name__ == "__main__":
  main()
