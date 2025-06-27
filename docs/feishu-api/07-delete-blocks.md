# 删除文档块 API

## 接口描述
删除指定父块下的一定范围的子块内容。

## API信息
- **请求方法**: DELETE
- **请求URL**: `https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children/batch_delete`
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
| start_index | int | 是 | 删除起始位置（包含） |
| end_index | int | 是 | 删除结束位置（不包含） |

## 请求示例

### cURL - 删除指定范围的子块
```bash
curl --location --request DELETE 'https://open.feishu.cn/open-apis/docx/v1/documents/doxcnAJ9VRRJqVMYZ1MyKnavXWe/blocks/doxcnAJ9VRRJqVMYZ1MyKnavXWe/children/batch_delete?document_revision_id=-1' \
--header 'Authorization: Bearer u-xxx' \
--header 'Content-Type: application/json' \
--data-raw '{
   "start_index": 0,
   "end_index": 1
}'
```

### Body示例 - 删除单个块
```json
{
   "start_index": 0,
   "end_index": 1
}
```

### Body示例 - 删除多个连续块
```json
{
   "start_index": 2,
   "end_index": 5
}
```

### Body示例 - 清空所有子块
```json
{
   "start_index": 0,
   "end_index": 999
}
```

## 响应结果

### 成功响应
```json
{
    "code": 0,
    "msg": "success",
    "data": {
        "deleted_count": 3,
        "deleted_block_ids": [
            "doxcnBlock1234567890",
            "doxcnBlock0987654321", 
            "doxcnBlockAbcdefghij"
        ]
    }
}
```

### 错误响应 - 无效范围
```json
{
    "code": 400002,
    "msg": "Invalid range: start_index must be less than end_index"
}
```

### 错误响应 - 块不存在
```json
{
    "code": 404001,
    "msg": "Block not found"
}
```

## 索引规则说明

### 索引计算
- `start_index`: 删除起始位置（从0开始，包含该位置）
- `end_index`: 删除结束位置（不包含该位置）
- 删除范围: `[start_index, end_index)`

### 示例说明
假设父块下有5个子块（索引0-4）：
```
[Block0] [Block1] [Block2] [Block3] [Block4]
   0        1        2        3        4
```

不同删除参数的效果：
| start_index | end_index | 删除的块 | 说明 |
|-------------|-----------|----------|------|
| 0 | 1 | Block0 | 删除第一个块 |
| 1 | 3 | Block1, Block2 | 删除中间两个块 |
| 0 | 5 | 全部块 | 删除所有子块 |
| 2 | 2 | 无 | 无效范围，不删除任何块 |

## 使用场景
- 清空文档内容重新同步
- 删除过期的内容块
- 重置文档结构
- 批量删除不需要的内容

## 注意事项
- 删除操作是不可逆的，请谨慎使用
- start_index必须小于end_index
- 如果end_index超出实际子块数量，只删除到最后一个块
- 删除后，后续块的索引会自动前移
- 不能删除文档的根块（document page）

## 安全建议
- 删除前建议先备份重要内容
- 使用具体的索引范围，避免使用过大的end_index
- 在删除操作前获取当前文档的块列表确认索引
- 对于重要文档，建议分步骤进行删除操作

## 与其他操作的配合
1. **先获取块列表**: 使用获取文档块API确认当前结构
2. **执行删除操作**: 使用本API删除指定范围的块
3. **重新插入内容**: 使用创建子块API插入新内容
4. **验证结果**: 再次获取块列表确认操作结果 