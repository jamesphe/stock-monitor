# 从Streamlit迁移到Alpine.js + TailwindCSS版本

本文档指导您如何从原有的基于Streamlit的股票监控系统迁移到新的基于Alpine.js和TailwindCSS的版本。

## 迁移步骤

1. **安装新的依赖**

   原版本使用Streamlit作为前端框架，新版本使用Flask作为后端API，Alpine.js和TailwindCSS作为前端框架。

   ```bash
   pip install -r requirements.txt
   ```

2. **启动新版本**

   使用新的启动脚本启动服务：

   ```bash
   python start.py
   ```

   系统会自动打开浏览器，访问 http://localhost:5000 页面。

   也可以使用不同的启动选项：
   - 仅启动API服务：`python start.py --api-only`
   - 仅启动定时任务：`python start.py --task-only`
   - 不自动打开浏览器：`python start.py --no-browser`

3. **数据迁移**

   新版本使用与旧版本相同的配置文件格式（monitor_config.json），您可以无缝继续使用原有的配置。

4. **定时任务**

   新版本提供了独立的定时任务脚本（task.py），可以在后台运行并定期检查股票信号。

## 主要变化

1. **界面变化**
   - 采用了更现代化的UI设计
   - 响应式布局，更好地适配移动设备
   - 使用Chart.js实现了更美观的图表展示

2. **架构变化**
   - 前后端分离架构，前端使用Alpine.js和TailwindCSS
   - 后端使用Flask提供API服务
   - 定时任务与Web服务分离

3. **性能提升**
   - 更轻量级的前端框架
   - 更高效的数据处理
   - 更稳定的后台任务管理

## 旧版本文件与新版本对应关系

| 旧版本文件 | 新版本文件 | 说明 |
|------------|------------|------|
| app.py | index.html | 前端UI从Streamlit迁移到HTML+Alpine.js |
| monitor.py | monitor.py | 核心功能库保持不变 |
| monitor_config.json | monitor_config.json | 配置文件格式不变 |
| - | api.py | 新增的Flask API服务 |
| - | task.py | 新增的定时任务脚本 |
| - | start.py | 新增的启动脚本 |

## 问题排查

1. **如果前端页面无法加载**
   - 确认Flask服务是否正常运行
   - 检查浏览器控制台是否有错误信息
   - 尝试清除浏览器缓存后重新加载

2. **如果数据获取失败**
   - 确认网络连接是否正常
   - 检查股票代码格式是否正确
   - 检查API请求是否有错误响应

3. **如果企业微信通知不工作**
   - 确认webhook地址是否正确
   - 检查网络连接是否正常
   - 检查企业微信机器人是否启用 