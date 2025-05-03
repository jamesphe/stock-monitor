# 股票监控系统 API 文档

本文档介绍如何访问股票监控系统的API在线文档。

## 安装依赖

确保已安装所需的Python依赖：

```bash
pip install -r requirements.txt
```

## 访问API文档

API文档已集成到主API服务中，只需启动API服务即可访问文档。

运行以下命令启动API服务：

```bash
cd /Users/james/work/stock-monitor
./start_backend.sh
```

服务器将在默认端口5001启动。成功启动后，打开浏览器访问：

```
http://localhost:5001/api/docs
```

这将显示交互式Swagger UI界面，你可以在其中：

- 浏览所有可用的API端点
- 查看每个API的详细参数和响应说明
- 直接从界面测试API调用
- 下载OpenAPI规范

## 可用的API端点

API文档中包含以下主要端点：

1. `/api/config` - 获取和更新系统配置
2. `/api/status` - 获取API服务状态
3. `/api/test` - API服务测试
4. `/api/stock_data` - 获取股票数据
5. `/api/evaluate` - 评估股票规则

## 注意事项

- API文档现已集成到主API服务中
- 如果你修改了API端点，文档将自动更新
- 生产环境建议关闭调试模式（不设置FLASK_ENV=development） 