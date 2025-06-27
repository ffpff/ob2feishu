# 批量更新文档块 API

## 接口描述
在单个请求中对文档的多个不同块进行批量更新操作，提高同步效率。

## API信息
- **请求方法**: PATCH
- **请求URL**: `https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/batch_update`
- **内容类型**: application/json

## 请求参数

### Path参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| document_id | string | 是 | 文档的唯一标识符 |

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
| requests | array | 是 | 批量更新请求数组 |

## 请求示例

### cURL - 批量更新多个块
```bash
curl --location --request PATCH 'https://open.feishu.cn/open-apis/docx/v1/documents/doxcnAJ9VRRJqVMYZ1MyKnavXWe/blocks/batch_update' \
--header 'Authorization: Bearer u-xxx' \
--header 'Content-Type: application/json' \
--data-raw '{
    "requests": [
        {
            "block_id": "doxcnk0i44OMOaouw8AdXuXrp6b",
            "merge_table_cells": {
                "column_end_index": 2,
                "column_start_index": 0,
                "row_end_index": 1,
                "row_start_index": 0
            }
        },
        {
            "block_id": "doxcn0K8iGSMW4Mqgs9qlyTP50d",
            "update_text_elements": {
                "elements": [
                    {
                        "text_run": {
                            "content": "Hello",
                            "text_element_style": {
                                "background_color": 2,
                                "bold": true,
                                "italic": true,
                                "strikethrough": true,
                                "text_color": 2,
                                "underline": true
                            }
                        }
                    },
                    {
                        "text_run": {
                            "content": "World ",
                            "text_element_style": {
                                "italic": true
                            }
                        }
                    }
                ]
            }
        }
    ]
}'
```

### Body示例 - 批量更新文本内容
```json
{
    "requests": [
        {
            "block_id": "block_id_1",
            "update_text_elements": {
                "elements": [
                    {
                        "text_run": {
                            "content": "第一个块的新内容",
                            "text_element_style": {
                                "bold": true,
                                "text_color": 2
                            }
                        }
                    }
                ]
            }
        },
        {
            "block_id": "block_id_2", 
            "update_text_elements": {
                "elements": [
                    {
                        "text_run": {
                            "content": "第二个块的新内容",
                            "text_element_style": {
                                "italic": true,
                                "text_color": 5
                            }
                        }
                    }
                ]
            }
        },
        {
            "block_id": "block_id_3",
            "update_text_elements": {
                "elements": [
                    {
                        "text_run": {
                            "content": "第三个块的新内容",
                            "text_element_style": {
                                "underline": true,
                                "background_color": 14
                            }
                        }
                    }
                ]
            }
        }
    ]
}
```

## 支持的批量操作类型

### 1. 更新文本元素
```json
{
    "block_id": "block_id",
    "update_text_elements": {
        "elements": [...]
    }
}
```

### 2. 合并表格单元格
```json
{
    "block_id": "table_block_id",
    "merge_table_cells": {
        "column_start_index": 0,
        "column_end_index": 2,
        "row_start_index": 0,
        "row_end_index": 1
    }
}
```

### 3. 删除块内容
```json
{
    "block_id": "block_id",
    "delete_block": {}
}
```

### 4. 插入块内容
```json
{
    "block_id": "parent_block_id",
    "insert_blocks": {
        "index": 0,
        "blocks": [...]
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
        "responses": [
            {
                "block_id": "doxcnk0i44OMOaouw8AdXuXrp6b",
                "success": true
            },
            {
                "block_id": "doxcn0K8iGSMW4Mqgs9qlyTP50d",
                "success": true,
                "block": {
                    "block_id": "doxcn0K8iGSMW4Mqgs9qlyTP50d",
                    "block_type": 2,
                    "text": {
                        "elements": [
                            {
                                "text_run": {
                                    "content": "Hello",
                                    "text_element_style": {
                                        "background_color": 2,
                                        "bold": true,
                                        "italic": true,
                                        "strikethrough": true,
                                        "text_color": 2,
                                        "underline": true
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }
}
```

### 部分失败响应
```json
{
    "code": 0,
    "msg": "success",
    "data": {
        "responses": [
            {
                "block_id": "valid_block_id",
                "success": true
            },
            {
                "block_id": "invalid_block_id",
                "success": false,
                "error": {
                    "code": 400001,
                    "message": "Block not found"
                }
            }
        ]
    }
}
```

## 使用场景
- 大批量同步Obsidian笔记内容
- 一次性更新文档的多个部分
- 提高API调用效率，减少请求次数
- 原子性操作，保证数据一致性

## 注意事项
- 单次请求最多支持100个更新操作
- 所有操作在同一个事务中执行
- 如果某个操作失败，不会影响其他操作
- 响应中会标明每个操作的成功/失败状态
- 建议按块类型分组进行批量操作

## 性能优化建议
- 优先使用批量接口而非单个更新接口
- 合理控制单次批量操作的数量
- 对于大文档，可以分页进行批量更新
- 使用合适的document_revision_id确保数据一致性 