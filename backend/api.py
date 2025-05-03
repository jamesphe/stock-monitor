from flask import Flask, request, jsonify, send_from_directory
import logging
import pandas as pd
import os
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from monitor import (
    load_config, 
    save_config, 
    evaluate_rules, 
    fetch_data,
    AKSHARE_AVAILABLE
)


# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("stock_api")


# 获取当前脚本的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(current_dir, 'static')
frontend_dist = os.path.join(os.path.dirname(current_dir), 'frontend-dist')

app = Flask(__name__, static_folder=None)  # 禁用默认的静态文件处理
# 启用CORS支持
CORS(
    app, 
    resources={r"/api/*": {"origins": "*", "supports_credentials": True}}, 
    allow_headers=["Content-Type", "Authorization"]
)

# 创建API文档对象
api = Api(
    app,
    version='1.0',
    title='股票监控系统API',
    description='股票监控系统后端API接口文档',
    doc='/api/docs',
    default='股票监控',
    default_label='股票监控系统API',
    prefix='/api',
    ordered=True
)

# 定义命名空间
ns = api.namespace('', description='股票监控API')

# 定义数据模型
config_model = api.model('配置', {
    'stocks': fields.List(fields.Raw, description='股票列表'),
    'rules': fields.List(fields.Raw, description='规则列表')
})

stock_data_model = api.model('股票数据', {
    'date': fields.String(description='日期'),
    'open': fields.Float(description='开盘价'),
    'high': fields.Float(description='最高价'),
    'low': fields.Float(description='最低价'),
    'close': fields.Float(description='收盘价'),
    'volume': fields.Float(description='成交量'),
    'rsi': fields.Float(description='RSI指标值')
})

status_model = api.model('API状态', {
    'akshare_available': fields.Boolean(description='AKShare库是否可用')
})

evaluate_response_model = api.model('规则评估结果', {
    'status': fields.String(description='评估状态'),
    'alerts': fields.List(fields.Raw, description='告警列表')
})

evaluate_input_model = api.model('规则评估输入', {
    'stocks': fields.List(fields.Raw, description='股票列表'),
    'rules': fields.List(fields.Raw, description='规则列表')
})


# 静态文件路由 (用于兼容旧版本)
@app.route('/static/<path:path>')
def serve_static(path):
    logger.info(f"提供静态文件: {path}")
    return send_from_directory(static_folder, path)


# 请求前日志记录
@app.before_request
def before_request_logging():
    logger.debug(f"接收到请求: {request.method} {request.path}")
    logger.debug(f"请求头: {dict(request.headers)}")
    if request.args:
        logger.debug(f"请求参数: {dict(request.args)}")
    if request.is_json:
        logger.debug(f"请求体: {request.json}")


# 响应后日志记录
@app.after_request
def after_request_logging(response):
    logger.debug(f"响应状态码: {response.status_code}")
    logger.debug(f"响应头: {dict(response.headers)}")
    return response


# 根路径提供前端页面
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    logger.info(f"提供前端页面: {path}")
    
    # API路径交给Flask-RESTX处理
    if path.startswith('api/'):
        return "Not Found", 404
    
    # 检查前端构建目录是否存在
    if os.path.exists(frontend_dist):
        # 检查请求的文件是否存在
        file_path = os.path.join(frontend_dist, path)
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            return send_from_directory(frontend_dist, path)
            
        # 返回index.html用于处理前端路由
        return send_from_directory(frontend_dist, 'index.html')
    else:
        # 如果前端构建目录不存在，尝试使用项目根目录中的index.html
        try:
            root_dir = os.path.dirname(current_dir)
            return send_from_directory(root_dir, 'index.html')
        except Exception as e:
            logger.error(f"提供前端页面失败: {e}")
            return jsonify({"error": f"提供前端页面失败: {str(e)}"}), 500


# API接口：获取配置
@ns.route('/config')
class ConfigResource(Resource):
    @ns.doc(description='获取系统配置')
    @ns.response(200, '成功', config_model)
    @ns.response(500, '服务器错误')
    def get(self):
        """获取系统配置"""
        logger.info("获取配置")
        try:
            config = load_config(
                os.path.join(current_dir, "monitor_config.json")
            )
            logger.debug(f"加载配置成功: {config}")
            return config
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            ns.abort(500, f"获取配置失败: {str(e)}")

    @ns.doc(description='更新系统配置')
    @ns.expect(config_model)
    @ns.response(200, '成功')
    @ns.response(500, '服务器错误')
    def post(self):
        """更新系统配置"""
        logger.info("保存配置")
        try:
            config = api.payload
            logger.debug(f"收到配置: {config}")
            save_config(
                config, os.path.join(current_dir, "monitor_config.json")
            )
            return {"status": "success"}
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            ns.abort(500, f"保存配置失败: {str(e)}")


# API接口：获取API状态
@ns.route('/status')
class StatusResource(Resource):
    @ns.doc(description='获取API状态')
    @ns.response(200, '成功', status_model)
    @ns.response(500, '服务器错误')
    def get(self):
        """获取API状态"""
        logger.info("获取API状态")
        try:
            status = {"akshare_available": AKSHARE_AVAILABLE}
            logger.debug(f"API状态: {status}")
            return status
        except Exception as e:
            logger.error(f"获取API状态失败: {e}")
            ns.abort(500, f"获取API状态失败: {str(e)}")


# API测试端点
@ns.route('/test')
class TestResource(Resource):
    @ns.doc(description='测试API是否正常运行')
    @ns.response(200, '成功')
    def get(self):
        """测试API是否正常运行"""
        logger.info("API测试")
        return {
            "status": "ok", 
            "message": "API服务正常运行"
        }


# API接口：获取股票数据
@ns.route('/stock_data')
@ns.param('code', '股票代码')
@ns.param('period', '周期类型 (daily/weekly/monthly)', default='daily')
@ns.param('count', '数据条数', default=120)
class StockDataResource(Resource):
    @ns.doc(description='获取股票数据')
    @ns.response(200, '成功', [stock_data_model])
    @ns.response(400, '参数错误')
    @ns.response(500, '服务器错误')
    def get(self):
        """获取股票数据"""
        logger.info("获取股票数据")
        try:
            stock_code = request.args.get('code')
            if not stock_code:
                logger.warning("缺少股票代码参数")
                ns.abort(400, "缺少股票代码参数")
            
            period = request.args.get('period', 'daily')
            count = int(request.args.get('count', 120))
            
            logger.debug(f"获取股票 {stock_code} 的{period}数据，{count}条")
            df = fetch_data(stock_code, period, count)
            
            if df is None:
                logger.error(f"获取股票 {stock_code} 数据失败")
                ns.abort(500, f"获取股票 {stock_code} 数据失败")
            
            logger.debug(f"获取到 {len(df)} 条数据")
            
            # 转换数据为JSON格式
            data = []
            for _, row in df.iterrows():
                date_str = ""
                if "date" in df.columns:
                    try:
                        date_str = row["date"].strftime("%Y-%m-%d")
                    except Exception as e:
                        logger.warning(f"日期格式化失败: {e}")
                        date_str = str(row["date"])
                
                item = {
                    "date": date_str,
                    "open": float(row["open"]) if "open" in df.columns else 0,
                    "high": float(row["high"]) if "high" in df.columns 
                        else 0,
                    "low": float(row["low"]) if "low" in df.columns else 0,
                    "close": float(row["close"]) if "close" in df.columns 
                        else 0,
                    "volume": float(row["volume"]) if "volume" in df.columns 
                            else 0
                }
                
                # 单独处理RSI以避免行太长
                if "rsi" in df.columns:
                    if pd.notna(row["rsi"]):
                        item["rsi"] = float(row["rsi"])
                    else:
                        item["rsi"] = None
                
                data.append(item)
            
            return data
        except Exception as e:
            logger.error(f"获取股票数据异常: {e}", exc_info=True)
            ns.abort(500, f"获取股票数据异常: {str(e)}")


# API接口：评估规则
@ns.route('/evaluate')
class EvaluateResource(Resource):
    @ns.doc(description='评估规则')
    @ns.expect(evaluate_input_model)
    @ns.response(200, '成功', evaluate_response_model)
    @ns.response(408, '处理超时')
    @ns.response(500, '服务器错误')
    def post(self):
        """评估股票规则"""
        logger.info("评估规则 - 开始处理请求")
        try:
            # 可以手动传入规则或使用配置文件中的规则
            if api.payload and 'stocks' in api.payload:
                config = api.payload
                logger.debug(f"使用请求中的规则配置: {config}")
                stocks_count = len(config.get('stocks', []))
                logger.info(f"请求包含 {stocks_count} 只股票")
                for idx, stock in enumerate(config.get('stocks', [])):
                    stock_code = stock.get('code', '')
                    stock_name = stock.get('name', '')
                    logger.debug(
                        f"股票 {idx+1}/{stocks_count}: {stock_code} {stock_name}"
                    )
            else:
                config = load_config(
                    os.path.join(current_dir, "monitor_config.json")
                )
                logger.debug("使用配置文件中的规则配置")
            
            # 添加超时处理
            import threading
            
            def evaluation_worker():
                nonlocal result, error_msg
                try:
                    result = evaluate_rules(config)
                except Exception as e:
                    import traceback
                    error_msg = f"评估规则时发生错误: {str(e)}\n{traceback.format_exc()}"
                    logger.error(error_msg)
            
            # 创建并启动评估线程
            result = None
            error_msg = None
            worker_thread = threading.Thread(target=evaluation_worker)
            worker_thread.daemon = True
            worker_thread.start()
            
            # 等待线程完成，最多等待60秒
            worker_thread.join(timeout=60)
            
            if worker_thread.is_alive():
                logger.warning("评估规则超时")
                return {
                    "status": "timeout",
                    "message": "评估规则超时，请减少监控股票数量或稍后再试"
                }, 408
            
            if error_msg:
                ns.abort(500, error_msg)
            
            if result:
                logger.info(f"评估完成，得到 {len(result.get('alerts', []))} 条告警")
                return result
            else:
                ns.abort(500, "评估规则返回空结果")
        except Exception as e:
            logger.error(f"评估规则异常: {e}", exc_info=True)
            ns.abort(500, f"评估规则异常: {str(e)}")


def process_dict(item):
    """处理字典，确保所有值都可以被JSON序列化"""
    for key, value in list(item.items()):
        if pd.isna(value):
            item[key] = None
        elif isinstance(value, (pd.Timestamp, pd.DatetimeIndex)):
            item[key] = str(value)
        elif isinstance(value, dict):
            item[key] = process_dict(value)
        elif isinstance(value, (list, tuple)):
            item[key] = [
                process_dict(x) if isinstance(x, dict) else x for x in value
            ]
    return item


@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404错误: {request.path}")
    return jsonify({
        "error": "Not Found",
        "message": f"找不到请求的资源: {request.path}"
    }), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"500错误: {error}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "服务器内部错误，请查看日志获取详细信息"
    }), 500


if __name__ == "__main__":
    # 在开发环境中启用debug模式
    debug_mode = True  # 默认启用调试模式
    
    port = int(os.environ.get('PORT', 5001))  # 默认使用5001端口
    logger.info(f"启动API服务器，端口: {port}, 调试模式: {debug_mode}")
    logger.info(f"API文档可访问: http://localhost:{port}/api/docs")
    
    # 记录PID以便后续操作
    with open(os.path.join(current_dir, 'api.pid'), 'w') as f:
        f.write(str(os.getpid()))
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode) 