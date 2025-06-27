# 更新特定块内容 API

## 接口描述
更新指定块的内容，如修改文本、样式等。适用于内容同步和增量更新。

## API信息
- **请求方法**: PATCH
- **请求URL**: `https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{block_id}`
- **内容类型**: application/json

## 请求参数

### Path参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| document_id | string | 是 | 文档的唯一标识符 |
| block_id | string | 是 | 要更新的块的唯一标识符 |

### Query参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| document_revision_id | int | 否 | 文档版本号，不传则使用最新版本 |

### Headers
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| Authorization | string | 是 | Bearer {access_token} |
| Content-Type | string | 是 | application/json |

## 请求示例

### cURL - 更新文本内容和样式
```bash
curl --location --request PATCH 'https://open.feishu.cn/open-apis/docx/v1/documents/doxcnAJ9VRRJqVMYZ1MyKnavXWe/blocks/doxcnC4cO4qUui6isgnpofh5edc' \
--header 'Authorization: Bearer u-xxx' \
--header 'Content-Type: application/json' \
--data-raw '{
    "update_text_elements": {
        "elements": [
            {
                "text_run": {
                    "content": "更新后的文本内容",
                    "text_element_style": {
                        "link": {
                            "url": "https://www.feishu.cn"
                        },
                        "bold": true,
                        "italic": true,
                        "text_color": 2
                    }
                }
            }
        ]
    }
}'
```

### Body示例 - 更新文本元素
```json
{
    "update_text_elements": {
        "elements": [
            {
                "text_run": {
                    "content": "新的文本内容",
                    "text_element_style": {
                        "bold": true,
                        "italic": true,
                        "underline": true,
                        "strikethrough": true,
                        "text_color": 2,
                        "background_color": 14
                    }
                }
            },
            {
                "text_run": {
                    "content": "带链接的文本",
                    "text_element_style": {
                        "link": {
                            "url": "https://example.com"
                        }
                    }
                }
            }
        ]
    }
}
```

### Body示例 - 更新标题内容
```json
{
    "update_text_elements": {
        "elements": [
            {
                "text_run": {
                    "content": "更新后的标题",
                    "text_element_style": {
                        "bold": true,
                        "text_color": 1
                    }
                }
            }
        ]
    }
}
```

## 响应结果

### 成功响应
```json
{
    "code": 0,
    "msg": "success",
    "data": {
        "block": {
            "block_id": "doxcnC4cO4qUui6isgnpofh5edc",
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "更新后的文本内容",
                            "text_element_style": {
                                "link": {
                                    "url": "https://www.feishu.cn"
                                },
                                "bold": true,
                                "italic": true,
                                "text_color": 2
                            }
                        }
                    }
                ],
                "style": {}
            }
        }
    }
}
```

## 文本样式属性说明

### text_element_style可用属性
| 属性名 | 类型 | 描述 | 可选值 |
|--------|------|------|--------|
| bold | boolean | 粗体 | true/false |
| italic | boolean | 斜体 | true/false |
| underline | boolean | 下划线 | true/false |
| strikethrough | boolean | 删除线 | true/false |
| text_color | int | 文字颜色 | 1-10 |
| background_color | int | 背景颜色 | 1-20 |
| link | object | 链接 | {"url": "链接地址"} |

### 颜色值对照
| 数值 | 颜色名称 |
|------|----------|
| 1 | 黑色 |
| 2 | 红色 |
| 3 | 橙色 |
| 4 | 黄色 |
| 5 | 绿色 |
| 6 | 蓝色 |
| 7 | 紫色 |
| 8 | 灰色 |

## 使用场景
- 同步Obsidian笔记内容变更到飞书
- 更新文档标题和内容
- 调整文本格式和样式
- 修复同步过程中的格式问题

## 注意事项
- 只能更新文本类型的块内容
- 更新操作会覆盖原有的elements数组
- 需要提供完整的text_element_style对象
- 链接URL需要使用有效的HTTP/HTTPS协议 