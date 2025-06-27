# 创建子块内容 API

## 接口描述
在指定的父块下创建新的子块内容，支持插入文本、标题、列表等各种类型的块。

## API信息
- **请求方法**: POST
- **请求URL**: `https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children`
- **内容类型**: application/json

## 请求参数

### Path参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| document_id | string | 是 | 文档的唯一标识符 |
| block_id | string | 是 | 父块的唯一标识符 |

### Query参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| document_revision_id | int | 否 | 文档版本号，不传则使用最新版本 |

### Headers
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| Authorization | string | 是 | Bearer {access_token} |
| Content-Type | string | 是 | application/json |

### Body参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| index | int | 是 | 插入位置，0表示最前面 |
| children | array | 是 | 要插入的块内容数组 |

## 请求示例

### cURL - 插入文本段落
```bash
curl --location --request POST 'https://open.feishu.cn/open-apis/docx/v1/documents/doxcnAJ9VRRJqVMYZ1MyKnavXWe/blocks/doxcnAJ9VRRJqVMYZ1MyKnavXWe/children?document_revision_id=120' \
--header 'Authorization: Bearer u-xxx' \
--header 'Content-Type: application/json' \
--data-raw '{
    "index": 0,
    "children": [
        {
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "这是一段新的文本内容",
                            "text_element_style": {
                                "background_color": 14,
                                "text_color": 5,
                                "bold": true
                            }
                        }
                    }
                ],
                "style": {}
            }
        }
    ]
}'
```

### Body示例 - 插入标题
```json
{
    "index": 0,
    "children": [
        {
            "block_type": 1,
            "heading1": {
                "elements": [
                    {
                        "text_run": {
                            "content": "这是一级标题",
                            "text_element_style": {
                                "bold": true
                            }
                        }
                    }
                ],
                "style": {}
            }
        }
    ]
}
```

### Body示例 - 插入代码块
```json
{
    "index": 0,
    "children": [
        {
            "block_type": 10,
            "code": {
                "language": "python",
                "elements": [
                    {
                        "text_run": {
                            "content": "def hello_world():\n    print('Hello, World!')"
                        }
                    }
                ]
            }
        }
    ]
}
```

### Body示例 - 插入表格
```json
{
    "index": 0,
    "children": [
        {
            "block_type": "table",
            "table": {
                "rowSize": 3,
                "columnSize": 3
            }
        }
    ]
}
```

## 响应结果

### 成功响应
```json
{
    "code": 0,
    "msg": "success",
    "data": {
        "children": [
            {
                "block_id": "doxcnNewBlockId123456",
                "block_type": 2,
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "这是一段新的文本内容",
                                "text_element_style": {
                                    "background_color": 14,
                                    "text_color": 5,
                                    "bold": true
                                }
                            }
                        }
                    ],
                    "style": {}
                }
            }
        ]
    }
}
```

## 常用块类型结构

### 文本段落 (block_type: 2)
```json
{
    "block_type": 2,
    "text": {
        "elements": [
            {
                "text_run": {
                    "content": "文本内容",
                    "text_element_style": {
                        "bold": true,
                        "italic": true,
                        "underline": true,
                        "text_color": 1,
                        "background_color": 2
                    }
                }
            }
        ],
        "style": {}
    }
}
```

### 标题块 (block_type: 1-7)
```json
{
    "block_type": 1,  // 1-7对应H1-H6
    "heading1": {     // heading1-heading6
        "elements": [
            {
                "text_run": {
                    "content": "标题内容",
                    "text_element_style": {}
                }
            }
        ],
        "style": {}
    }
}
```

## 使用场景
- 将Obsidian笔记内容转换为飞书文档块
- 批量创建文档内容
- 动态构建文档结构

## 注意事项
- index从0开始，表示插入位置
- 每次调用返回新创建块的ID
- 支持批量创建多个块
- 文本样式支持颜色、粗体、斜体等格式 