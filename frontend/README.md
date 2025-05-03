# 股票信号监控系统前端

本项目是股票信号监控系统的前端部分，使用Vue.js 3构建。

## 开发环境设置

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run serve

# 构建生产版本
npm run build
```

## 项目结构

```
frontend/
├── public/              # 静态资源
├── src/
│   ├── api/             # API请求接口
│   ├── assets/          # 资源文件（图片、CSS等）
│   ├── components/      # Vue组件
│   ├── router/          # 路由配置
│   ├── views/           # 页面视图
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── package.json         # 项目依赖及脚本
├── tailwind.config.js   # TailwindCSS配置
└── vue.config.js        # Vue配置
```

## 与后端连接

前端默认通过代理连接到运行在 `http://localhost:5000` 的后端API。
可以通过修改 `vue.config.js` 中的代理配置来更改后端地址。 