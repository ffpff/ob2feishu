# 获取飞书文档基本信息 API

## 接口描述
获取指定飞书文档的基本信息，包括文档标题、最新版本号等。

## API信息
- **请求方法**: GET
- **请求URL**: `https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}`
- **内容类型**: application/json

## 请求参数

### Path参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| document_id | string | 是 | 文档的唯一标识符 |

### Headers
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| Authorization | string | 是 | Bearer {access_token} |

## 请求示例

### cURL
```bash
curl --location --request GET 'https://open.feishu.cn/open-apis/docx/v1/documents/doxcnAJ9VRRJqVMYZ1MyKnavXWe' \
--header 'Authorization: Bearer u-xxx'
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
            "revision_id": 120,
            "title": "我的笔记标题"
        }
    }
}
```

## 使用场景
- 检查文档是否存在
- 获取文档最新版本号，用于版本控制
- 获取当前文档标题
- 同步前的状态检查

## 注意事项
- revision_id表示文档的版本号，每次修改都会递增
- 如果文档不存在或无权限访问，会返回相应错误码
- 该接口不返回文档内容，仅返回基本元信息 