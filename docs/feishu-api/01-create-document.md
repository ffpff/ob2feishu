# 创建飞书文档 API

## 接口描述
创建新的飞书文档，可选择指定目标文件夹。

## API信息
- **请求方法**: POST
- **请求URL**: `https://open.feishu.cn/open-apis/docx/v1/documents`
- **内容类型**: application/json

## 请求参数

### Query参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| folder_token | string | 否 | 目标文件夹的token，不传则创建在根目录 |

### Headers
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| Authorization | string | 是 | Bearer {access_token} |
| Content-Type | string | 是 | application/json |

## 请求示例

### cURL
```bash
curl --location --request POST 'https://open.feishu.cn/open-apis/docx/v1/documents?folder_token=fldcnbCHL8OAtkcYHnPzZi1yupN' \
--header 'Authorization: Bearer u-xxx' \
--header 'Content-Type: application/json'
```

## 响应结果

### 成功响应
```json
{
    "code": 0,
    "msg": "success",
    "data": {
        "document": {
            "document_id": "doxcnAJ9VRRJqVMYZ1MyKnavXWe",
            "revision_id": 1,
            "title": "Untitled"
        }
    }
}
```

## 使用场景
- 为每个Obsidian笔记创建对应的飞书文档
- 在指定的知识库文件夹中创建文档

## 注意事项
- 创建后的文档默认标题为"Untitled"，需要后续更新
- 返回的document_id是后续操作文档的唯一标识
- folder_token需要提前获取或使用知识库API创建 