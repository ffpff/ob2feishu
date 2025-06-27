# 飞书知识库文件夹和权限管理

## 概述

本文档记录飞书文档API中关于知识库文件夹创建和权限管理的相关接口和配置。

## 1. 创建文档到指定文件夹

### API端点
```
POST /open-apis/docx/v1/documents?folder_token={folder_token}
```

### 请求示例
```bash
curl --location --request POST 'https://open.feishu.cn/open-apis/docx/v1/documents?folder_token=fldcnbCHL8OAtkcYHnPzZi1yupN' \
--header 'Authorization: Bearer u-xxx'
```

### 参数说明
- `folder_token`: 目标文件夹的token，可以从飞书知识库URL中获取
- 如果不提供`folder_token`，文档将创建在根目录

### 实现代码示例

#### Python实现
```python
def create_document(
    self, 
    title: Optional[str] = None,
    folder_token: Optional[str] = None
) -> FeishuDocument:
    """创建新的飞书文档"""
    endpoint = "/open-apis/docx/v1/documents"
    if folder_token:
        endpoint += f"?folder_token={folder_token}"
    
    response = self.client.post(endpoint)
    # 处理响应...
```

## 2. 文档权限和访问控制

### 权限类型

#### 基础权限结构
```json
{
    "acl": [{
        "access": "allow",  // 或 "deny"
        "type": "user",
        "value": "everyone" // 或具体用户ID
    }]
}
```

#### 权限配置示例

##### 所有人可访问
```json
{
    "acl": [{
        "access": "allow",
        "type": "user",
        "value": "everyone"
    }]
}
```

##### 特定用户可访问
```json
{
    "acl": [
        {
            "access": "allow",
            "type": "user",
            "value": "user1_employeeID"
        },
        {
            "access": "allow",
            "type": "user",
            "value": "user2_employeeID"
        }
    ]
}
```

##### 除特定用户外所有人可访问
```json
{
    "acl": [
        {
            "access": "allow",
            "type": "user",
            "value": "everyone"
        },
        {
            "access": "deny",
            "type": "user",
            "value": "user2"
        }
    ]
}
```

### 权限规则
1. **空ACL**: 默认所有用户无法访问
2. **Deny优先**: `deny`规则优先于`allow`规则
3. **用户类型**: 目前主要支持`user`类型
4. **特殊值**: `everyone`表示所有用户

## 3. 获取文件夹Token

### 从URL获取
飞书知识库URL格式通常为：
```
https://your-domain.feishu.cn/wiki/space/{space_id}/folder/{folder_token}
```

### API查询（如果有相关接口）
```bash
# 查询知识库空间信息
curl --location --request GET 'https://open.feishu.cn/open-apis/wiki/v2/spaces/{space_id}/nodes' \
--header 'Authorization: Bearer u-xxx'
```

## 4. 应用权限配置

### 应用可见性设置
```json
{
    "visibility": {
        "is_all": false,
        "visible_list": {
            "open_ids": [{
                "union_id": "on_8ed6aa67826108097d9ee143816345",
                "user_id": "e33ggbyz",
                "open_id": "ou_84aad35d084aa403a838cf73ee18467"
            }],
            "department_ids": ["od-ddee42c0f8a948a5e650341e2153243b"]
        },
        "invisible_list": {
            "open_ids": [{
                "union_id": "on_8ed6aa67826108097d9ee143816345",
                "user_id": "e33ggbyz",
                "open_id": "ou_84aad35d084aa403a838cf73ee18467"
            }],
            "department_ids": ["od-ddee42c0f8a948a5e650341e2153243b"]
        }
    },
    "app_status": 1
}
```

## 5. 常见问题和解决方案

### 问题1：文档创建在根目录而非指定文件夹
**原因**: 
- `folder_token`参数缺失或错误
- 应用权限不足

**解决方案**:
1. 确保正确提供`folder_token`参数
2. 检查应用是否有目标文件夹的写入权限
3. 验证`folder_token`的有效性

### 问题2：用户无法编辑文档
**原因**:
- 文档权限设置不当
- 应用权限配置问题
- 用户不在可见用户列表中

**解决方案**:
1. 配置正确的ACL权限
2. 检查应用的可见性设置
3. 确保目标用户在权限列表中

### 问题3：获取文件夹token困难
**解决方案**:
1. 从浏览器URL中复制`folder_token`
2. 使用飞书API查询知识库结构
3. 联系管理员获取目标文件夹信息

## 6. 最佳实践

1. **权限最小化**: 只给予必要的权限
2. **测试验证**: 创建文档后验证权限设置
3. **错误处理**: 对权限相关错误进行适当处理
4. **日志记录**: 记录权限操作以便调试

## 7. 相关API参考

- [创建文档 API](./01-create-document.md)
- [获取文档信息 API](./02-get-document-info.md)
- [文档块操作 API](./03-get-document-blocks.md) 