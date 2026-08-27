---
name: yuque-lake-document
description: Create and repair native Yuque .lake documents, including Yuque cards, task lists, collapsible blocks, alerts, tables, code blocks, and embedded Lakeboard diagrams. Use for 语雀文档/Lake document authoring, not ordinary Markdown files.
---

# 语雀 Lake 文档原生编写

`.lake` 是语雀的 HTML 文档格式，不是 Markdown。直接生成语雀结构，不先写 Markdown 再做有损转换。

## 文件外壳

文档以这一行开头：

```html
<!doctype lake><meta name="doc-version" content="1" /><meta name="viewport" content="fixed" />
```

正文紧随其后，不额外包 `<html>`、`<head>` 或 `<body>`。保存为 UTF-8；可以格式化检查，但最终优先写成单行，避免工具把空白误当正文。

标题、段落、粗体、斜体、删除线、链接、普通有序/无序列表、引用和基础表格与 Markdown 语义一致，按对应 HTML 标签表达即可。

## Lake 节点 ID

可编辑正文节点使用相同的 `data-lake-id` 和 `id`，例如：

```html
<p data-lake-id="u0f15eb4e" id="u0f15eb4e"><span data-lake-id="u7d2bf5b7" id="u7d2bf5b7">正文</span></p>
```

- 每个 `id` 在文档中唯一；短随机 ID 或 UUID 均可。
- 列表项的 `fid` 表示同一列表族，可以重复；不要把它当节点 ID。
- 编辑现有文档时保留未改节点的 ID，只给新增节点生成新 ID。

## Markdown 没有完整表达的行内样式

- 下划线：`<u>文字</u>`。
- 字色：`<span style="color: #DF2A3F">文字</span>`。
- 高亮：`<span style="background-color: #FBDE28">文字</span>`。
- 多种样式按语义嵌套，最内层文本仍放带 Lake ID 的 `span`。

## Card 协议

语雀独有内容用自闭合语义的 `card` 元素：

```html
<card type="block" name="CARD_NAME" value="data:PERCENT_ENCODED_VALUE"></card>
```

`value` 必须以 `data:` 开头。对象和数组先 JSON 序列化，再用 `encodeURIComponent` 等价规则进行 UTF-8 百分号编码；布尔卡片直接编码 `true` / `false`。不要把未编码 JSON 塞进属性。

已验证的卡片：

| `name` | `type` | payload |
|---|---|---|
| `hr` | `block` | `{ "id": "唯一 ID" }` |
| `checkbox` | `inline` | `true` 或 `false` |
| `codeblock` | `inline` | 代码、语言和显示选项对象 |
| `board` | `block` | 内嵌 Lakeboard 对象 |

编辑现有 `codeblock` 时保留未知显示字段。新建时至少写 `mode`、`code`、`lineNumbers`、`autoWrap`、`theme`、`fontSize`、`id` 和 `margin`；不要把 fenced code 原样放进正文冒充语雀代码块。

## 表格

语雀表格除普通 HTML 表格结构外，还保留列宽和显示方式：

```html
<table data-lake-id="ID" id="ID" margin="true" width-mode="contain" class="lake-table" style="width: 750px">
  <colgroup><col width="250"><col width="250"><col width="250"></colgroup>
  <tbody><tr data-lake-id="ROW" id="ROW"><td data-lake-id="CELL" id="CELL"></td></tr></tbody>
</table>
```

列数、`colgroup` 和每行单元格数必须一致。空单元格保持空 `td`，不要填伪造占位文本。

## 折叠块

```html
<details data-lake-id="ID" id="ID" open="true" class="lake-collapse">
  <summary data-lake-id="SUMMARY_ID" id="SUMMARY_ID" class="lake-summary">标题</summary>
  <p data-lake-id="BODY_ID" id="BODY_ID">内容</p>
</details>
```

`open="true"` 表示导入后默认展开；需要默认折叠时省略 `open`。

## 任务列表与缩进列表

任务项使用普通 `ul/li` 加 checkbox card：

```html
<ul list="LIST_ID" class="lake-list">
  <li fid="FAMILY_ID" data-lake-id="ITEM_ID" id="ITEM_ID" class="lake-list-node lake-list-task"><card type="inline" name="checkbox" value="data:false"></card>任务</li>
</ul>
```

同一连续列表复用 `list` 和 `fid`。嵌套层级使用 `data-lake-indent="1"`、`"2"`；真实导出可能把不同缩进拆成相邻的 `ol/ul`，编辑时沿用，不强行重组 DOM。

## 提示块

```html
<blockquote data-lake-id="ID" id="ID" class="lake-alert lake-alert-info"><p data-lake-id="P_ID" id="P_ID">提示内容</p></blockquote>
```

`lake-alert-info` 是已验证样式。其他提示类型没有样例时不要猜类名，先从语雀导出对应样式取样。

## 内嵌 Lakeboard

文档与画板保持两个 Skill：本文档 Skill 负责 `board` card 外壳，`lakeboard-authoring` 负责画板内容。只有文档包含内嵌画板时才加载并使用 `$lakeboard-authoring`，避免普通文档任务承担整套绘图规则。

`board` payload 是 `.lakeboard` 的内嵌形态：

```json
{
  "diagramData": { "head": {}, "body": [] },
  "viewportOption": "adapt",
  "viewportSetting": {},
  "search": "画板可搜索文本",
  "graphicsBBox": {},
  "id": "唯一 ID"
}
```

- 从 `$lakeboard-authoring` 生成并验证画板后，取 `diagramData`、`viewportOption`、`viewportSetting`、`graphicsBBox`，把顶层 `text` 改放到 `search`，再编码进 card。
- 内嵌 payload 不带 `.lakeboard` 顶层的 `format`、`type`、`version`、`mode`。
- `src` 是语雀生成的画板预览资源。编辑已有文档时保留；新建时没有真实预览资源就不要伪造 CDN 地址，并在语雀导入后确认预览是否自动生成。

## 完成检查

运行：

```bash
python3 .agents/skills/yuque-lake-document/scripts/validate_lake.py <file.lake>
```

然后在语雀导入检查：普通排版、折叠默认状态、任务勾选状态、代码块语言、表格列宽和内嵌画板是否可编辑。若包含画板，还要先运行 `$lakeboard-authoring` 的验证脚本检查画板结构。
