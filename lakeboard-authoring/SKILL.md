---
name: lakeboard-authoring
description: Draw and repair native Yuque Lakeboard (.lakeboard) diagrams with readable layout, faithful content, frames, shapes, and connectors. Use for 语雀画板/Lakeboard authoring; this is not a format-conversion workflow.
---

# Lakeboard 原生绘制

把 `.lakeboard` 当作画板场景来画，不把另一种文件格式的字段逐项硬映射。外部流程图只提供内容、层级和连线语义；输出应重新选择适合 Lakeboard 的可读布局。

## 开始前

有真实语雀导出样例时先读样例，沿用它的顶层外壳和节点字段。官方 schema 不完整，不猜未经样例验证的字段。

先列一份绘制清单：标题、分区、节点、关键语义、连线、连线标签。忠实还原时保留全部信息；用户允许精简时，保留状态、动作、校验、产物去向和失败分支，删除重复说明、冗长类名和实现背景。

## 文件外壳

```json
{
  "format": "lakeboard",
  "type": "Board",
  "version": "1.0",
  "diagramData": {
    "head": {
      "version": "2.0.0",
      "theme": { "name": "default" },
      "rough": { "name": "default" }
    },
    "body": []
  },
  "mode": "edit",
  "viewportSetting": {
    "zoom": 0.75,
    "tlCanvasPoint": [0, 0, 1],
    "width": 1600,
    "height": 900
  },
  "viewportOption": "adapt",
  "text": "可搜索的画板文本摘要",
  "graphicsBBox": { "x": 0, "y": 0, "width": 1600, "height": 900 }
}
```

所有 `id` 使用 UUID。`zIndex` 严格递增，顺序是背景框、标题/节点、连线；背景必须先于其内部节点。

## 元素选择

| `type` | 用途 | 关键结构 |
|---|---|---|
| `geometry` | 带框图形、分区背景 | `shape`、尺寸、填充、边框、HTML |
| `text` | 无框纯文本 | 根坐标、HTML；真实样例不带尺寸 |
| `line` | 普通形状之间的连线 | `source`、`target`、`connection` |
| `swimlane` | 原生横/纵泳道 | 分隔比例、泳道标题、包含关系 |
| `mindmap` | 可自动排版的递归思维导图 | 嵌套 `children`、`layout`、`treeEdge` |
| `pen` | 自由手绘折线/封闭图形 | 绝对坐标点集 `points` |

不要因为外观看起来相似就混用类型：普通流程树用框线，真正需要自动树布局时用 mindmap，需要规则分区时才用 swimlane。

## 画形状

普通节点使用 `geometry`：

```json
{
  "type": "geometry",
  "shape": "rounded-rect",
  "category": "basic",
  "round": 10,
  "id": "UUID",
  "x": 100,
  "y": 100,
  "width": 280,
  "height": 180,
  "html": "<div style=\"text-align:center;\">第一行<br>第二行</div>",
  "fill": { "color": "#D6EAF8" },
  "stroke": { "color": "#585A5A" },
  "defaultContentStyle": { "color": "#262626" },
  "rotate": 0,
  "zIndex": 1
}
```

- 文本默认使用 `text-align:center`；只有用户明确要求或表格/代码等内容确实不适合居中时才改对齐方式。文本先做 HTML 转义，再把换行变成 `<br>`；空框用 `&nbsp;`。
- 分区背景也用大号 `rounded-rect`，不用不稳定的嵌套容器。背景框必须完整包住标题和节点。
- 推荐颜色：人工 `#DFB85D`，Workspace `#D6EAF8`，CI `#E8DAEF`，注意 `#FCF3CF`，错误/闸门 `#FADBD8`，背景 `#FFFFFF`。
- 普通节点优先控制在 3–5 行；超过时先去掉重复解释，再拆成相邻节点，最后才增大框。宁可让画板可滚动，也不要把长文塞进小框或缩成全局鸟瞰图。

## 布局规则

- 分区标题条高约 36–44 px。内部节点距标题条至少 24 px，距分区左右/底边至少 32 px；不得像贴边标签一样挤在边框上。
- 同行节点间距至少 40 px，跨行至少 56 px；为曲线和线标签额外留一条不穿框的通道。
- 主流程保持单一阅读方向。需要回折时整行换向，或使用独立回程通道；不要让连线穿过节点、标题或其他分区。
- 同类节点尽量等宽、同行等高；先根据内容确定最大节点尺寸，再计算分区尺寸，禁止先固定分区再硬塞节点。
- 生成后检查每个节点矩形是否完全落在所属分区的安全内边距内，并检查 `graphicsBBox` 是否覆盖最外侧节点、曲线控制点和标题。

原素材已验证的 `geometry.shape`：

- `rounded-rect`：普通节点和背景框；圆角由 `round` 控制。
- `circle`、`triangle`、`diamond`、`cloud`：使用相同的填充、边框和 HTML 字段。
- `parallelogram`：另带 `controlPoints: [[0.1875, 0.25]]`。

纯文本使用独立 `text`：

```json
{
  "type": "text",
  "shape": "text",
  "category": "basic",
  "id": "UUID",
  "x": 100,
  "y": 100,
  "html": "纯文本",
  "defaultContentStyle": { "color": "#262626" },
  "zIndex": 1
}
```

真实样例的 `text` 没有 `width/height`；若文字需要稳定的换行与包围盒，直接使用透明或白底 geometry 更可靠。

## 画连线

连线自身不写 `x/y/width/height`，只引用已存在节点：

```json
{
  "type": "line",
  "shape": "curve",
  "id": "UUID",
  "source": { "id": "源节点 UUID", "connection": "E" },
  "target": { "id": "目标节点 UUID", "connection": "W", "marker": "arrow" },
  "stroke": { "color": "#585A5A" },
  "defaultContentStyle": { "color": "#262626" },
  "opacity": 1,
  "zIndex": 99
}
```

- 普通连线默认使用 `curve`，包括同行连接；端点仍按阅读方向使用 `E → W`、`S → N` 等成对连接。
- 默认不要写 `controlPoints`，让 Lakeboard 根据端点自动生成平滑曲线，避免出现可见曲点或人为弯折。只有用户明确要求固定绕线路径时才添加控制点，并把它放在预留通道内。
- 只有用户明确要求直线/折线，或边框、表格等几何语义必须笔直时，才使用 `straight` / `elbow`。
- 虚线用 `stroke.style = "dash"`。
- 标签放 `html`，并设 `textPosition`。标签只保留确有语义的文字，避免在线上重复节点内容。

## 画思维导图

思维导图不是普通框线的视觉变体，而是独立的递归 `mindmap` 数据结构。不要用 `geometry + line` 模拟：原生结构才能让 Lakeboard 自动排树、切换方向、折叠分支并识别节点图标。

```json
{
  "type": "mindmap",
  "id": "根 UUID",
  "x": 800,
  "y": 1200,
  "html": "中心主题",
  "border": { "fill": "#EFF0F0", "shape": "capsule" },
  "defaultContentStyle": { "color": "#262626" },
  "layout": { "type": "standard", "direction": [1, 0] },
  "children": [
    {
      "id": "子节点 UUID",
      "html": "分支 1",
      "children": [],
      "treeEdge": { "stroke": "#A287E1" },
      "defaultContentStyle": { "color": "#262626" },
      "layout": { "quadrant": 1 },
      "zIndex": 1
    }
  ],
  "zIndex": 2
}
```

- 每个后代都是嵌套对象，必须有独立 UUID、`html` 和 `children`；分支线由子节点的 `treeEdge` 控制，不另建顶层 `line`。
- `layout.type = "standard"` 用于左右展开；子节点 `layout.quadrant` 的 `1/2` 控制两侧。缩进式用 `type = "indent"`，真实样例还带 `direction` 和 `quadrantConstraint`，沿用样例值，不凭空组合。
- `icons` 可写 `priority`、`progress`、`flag` 等原生标记。
- 摘要节点是放在根 `children` 中的特殊节点，带 `abstract: true`、`start`、`end`、透明边框；只有确实需要分支概要时才生成。
- 真实导出中的 mindmap 通常只有根坐标而没有 `width/height`，尺寸由布局引擎计算。因此 `graphicsBBox` 要给树的展开范围留余量，不能只按普通 geometry 求包围盒。

## 画泳道

泳道是独立容器。纵向泳道用 `swimlane-vertical`，横向泳道用 `swimlane-horizontal`：

```json
{
  "type": "swimlane",
  "shape": "swimlane-vertical",
  "category": "swimlane",
  "id": "UUID",
  "x": 400,
  "y": 400,
  "widths": [0.3333333333, 0.6666666667],
  "heights": [0.1],
  "stroke": { "color": "#585A5A" },
  "children": [
    {
      "id": "泳道标题 UUID",
      "nth": 0,
      "html": "<div style=\"text-align:center;\"><strong>Lane 1</strong></div>",
      "fill": { "color": "#FFFFFF" },
      "defaultContentStyle": { "color": "#262626" },
      "zIndex": 1
    }
  ],
  "contain": [],
  "zIndex": 2
}
```

- `widths` / `heights` 是 0–1 的分隔点，不是像素尺寸。纵向三列用两个 `widths` 分隔点和一个标题栏 `heights`；横向三行反过来。
- `children[].nth` 从 0 开始，对应泳道标题；每个标题也必须有独立 UUID。
- `contain` 放泳道内顶层元素 UUID。真实样例可为空；不确定编辑器的包含行为时保持空数组，按绝对坐标摆放元素。
- 原素材的泳道对象不带 `width/height`。需要非默认大小时必须用语雀实测导出验证，不把普通 geometry 的尺寸规则想当然套过来。

## 画手绘元素

`pen` 使用绝对坐标点集：

```json
{
  "type": "pen",
  "id": "UUID",
  "points": [[100, 100], [160, 220], [260, 170]],
  "isClosed": true,
  "zIndex": 1
}
```

`isClosed: true` 会闭合首尾。原素材没有为 pen 写普通 geometry 的 `fill/stroke` 字段，因此不要猜样式字段；需要特定笔刷时先在语雀画一个并重新导出取样。

## 可读性与视口

Lakeboard 在低缩放下会把框内多行文字显示成短横占位符；这不等于文本字段丢失。初始 `zoom` 通常设为 `0.7–0.9`，让首屏可读，允许用户滚动画板查看后续分区。不要为了首屏显示全部内容把缩放压得过低。

`graphicsBBox` 必须覆盖所有带坐标和尺寸的可见对象，不只覆盖业务节点；漏掉左侧入口、标题或背景框会导致导入后的自适应视口裁掉它们。

## 完成检查

运行：

```bash
python3 .agents/skills/lakeboard-authoring/scripts/validate_lakeboard.py <file.lakeboard>
```

然后核对：信息符合绘制清单、允许精简时关键语义仍完整、普通连线默认是曲线、文本默认居中、所有连线端点存在、mindmap 后代 UUID 不重复、节点满足分区安全边距、背景在底层、包围盒无裁切。最后在语雀以 80%–100% 缩放导入查看；若低缩放只显示短横，先放大再判断格式是否损坏。
