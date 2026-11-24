# 局部保护与授权差异 / Local protection and authorized differences

只读文件使用整文件指纹，允许编辑同一文件时使用局部锁和授权范围差异检查。
Use whole-file fingerprints for read-only files, and local locks plus authorized-difference checks when editing within a file.

| 类型 / Type | 实际保护 / Actual protection | 边界 / Boundary |
|---|---|---|
| `text_fragment` | 精确文字及出现次数 / Exact text and occurrence count | 不锁定位置；需要时追加结构约束 / Does not lock position; add structural constraints when needed |
| `text_section` | 唯一首尾标记之间的原文 / Text between unique start/end markers | 标记必须明确且不重复 / Markers must be explicit and unique |
| `svg_element` | 指定 ID 子树、祖先属性和全局样式定义 / ID subtree, ancestor attributes and global styles/defs | 保护指定对象，不等于任意像素区域 / Protects named objects, not arbitrary pixel regions |
| `svg_image_order` | 图像 ID、引用及文档顺序 / Image IDs, references and document order | 图像位置另由对象锁保护 / Protect positions separately with object locks |

```python
from task_integrity import capture_lock, review_text_edit, review_svg_edit
lock = capture_lock(root, "working-title", "chapter.md", "text_fragment",
                    {"text": "Multipurpose Spaces Connecting Indoors and Outdoors", "count": 1})
# Add lock to task['protected_content'] before editing.
diff = review_text_edit(before, after, [{"start": "<!-- EDIT_START -->", "end": "<!-- EDIT_END -->"}])
```

编辑后同时检查锁和授权区域外的差异；锁仍通过不能证明其他未授权位置没有被改动。
After editing, check both the locks and differences outside the authorized region; intact locks alone do not establish that other unauthorized content is unchanged.

正文改变影响引用或图注时重新核查相应依赖；文字含义、图文对应和美学判断仍需实际阅读或观看。
Recheck affected references or captions when prose changes; meaning, image–text agreement and aesthetic judgment still require actual reading or viewing.

本版直接支持 UTF-8 文本和带稳定 ID 的 SVG，不宣称已实现 PDF、Word、InDesign 或 CAD 的任意局部锁定。
This version directly supports UTF-8 text and SVG with stable IDs; it does not claim arbitrary local locking for PDF, Word, InDesign or CAD.

遇到其他格式先保留原件、生成可检查的工作副本和实际差异报告，再按当前可用应用和格式能力执行。
For other formats, preserve originals, create reviewable working copies and actual difference reports, then use the available applications and format capabilities.
