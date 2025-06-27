# 获取飞书文档所有块内容 API

## 接口描述
获取指定飞书文档的所有块（Block）内容，支持深度遍历和分页。

## API信息
- **请求方法**: GET
- **请求URL**: `https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks`
- **内容类型**: application/json

## 请求参数

### Path参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| document_id | string | 是 | 文档的唯一标识符 |

### Query参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page_size | int | 否 | 分页大小，默认100，最大500 |
| page_token | string | 否 | 分页标记，用于获取下一页 |
| document_revision_id | int | 否 | 文档版本号，-1表示最新版本 |

### Headers
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| Authorization | string | 是 | Bearer {access_token} |

## 请求示例

### cURL
```bash
curl --location --request GET 'https://open.feishu.cn/open-apis/docx/v1/documents/doxcnAJ9VRRJqVMYZ1MyKnavXWe/blocks?page_size=100&document_revision_id=-1' \
--header 'Authorization: Bearer u-xxx'
```

## 响应结果

### 成功响应
```json
{
    "code": 0,
    "msg": "success",
    "data": {
        "items": [
            {
                "block_id": "doxcnAJ9VRRJqVMYZ1MyKnavXWe",
                "block_type": 22,
                "page": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "这是文档标题",
                                "text_element_style": {
                                    "bold": true
                                }
                            }
                        }
                    ]
                }
            },
            {
                "block_id": "doxcnC4cO4qUui6isgnpofh5edc", 
                "block_type": 2,
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": "这是段落文本内容",
                                "text_element_style": {}
                            }
                        }
                    ],
                    "style": {}
                }
            }
        ],
        "page_token": "next_page_token",
        "has_more": false
    }
}
```

## Block类型说明
| block_type | 类型名称 | 描述 |
|------------|----------|------|
| 1 | 标题1 | H1标题 |
| 2 | 段落 | 普通文本段落 |
| 3 | 标题2 | H2标题 |
| 4 | 标题3 | H3标题 |
| 5 | 标题4 | H4标题 |
| 6 | 标题5 | H5标题 |
| 7 | 标题6 | H6标题 |
| 8 | 无序列表 | Bullet List |
| 9 | 有序列表 | Numbered List |
| 10 | 代码块 | Code Block |
| 11 | 引用 | Quote Block |
| 22 | 页面 | Document Page |

## 使用场景
- 读取现有文档内容进行比较
- 实现增量同步的内容检查
- 分析文档结构和格式

## 注意事项
- 该接口进行深度遍历，会返回所有层级的块
- 支持分页，大文档需要多次请求
- document_revision_id设为-1获取最新版本
- 每个块都有唯一的block_id，用于后续更新操作 