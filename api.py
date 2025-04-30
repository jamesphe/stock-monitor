from flask import Flask, request, jsonify, send_from_directory
import logging
import pandas as pd
from flask_cors import CORS
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


app = Flask(__name__, static_folder='.')
# 启用CORS支持
CORS(app)


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
@app.route('/')
def index():
    logger.info("提供前端页面")
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f"提供前端页面失败: {e}")
        return jsonify({"error": f"提供前端页面失败: {str(e)}"}), 500


# API接口：获取配置
@app.route('/api/config', methods=['GET'])
def get_config():
    logger.info("获取配置")
    try:
        config = load_config()
        logger.debug(f"加载配置成功: {config}")
        return jsonify(config)
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        return jsonify({"error": f"获取配置失败: {str(e)}"}), 500


# API接口：保存配置
@app.route('/api/config', methods=['POST'])
def update_config():
    logger.info("保存配置")
    try:
        config = request.json
        logger.debug(f"收到配置: {config}")
        save_config(config)
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        return jsonify({"error": f"保存配置失败: {str(e)}"}), 500


# API接口：获取API状态
@app.route('/api/status')
def get_status():
    logger.info("获取API状态")
    try:
        status = {"akshare_available": AKSHARE_AVAILABLE}
        logger.debug(f"API状态: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"获取API状态失败: {e}")
        return jsonify({"error": f"获取API状态失败: {str(e)}"}), 500


# API测试端点
@app.route('/api/test')
def test_api():
    logger.info("API测试")
    return jsonify({
        "status": "ok", 
        "message": "API服务正常运行"
    })


# API接口：获取股票数据
@app.route('/api/stock_data')
def get_stock_data():
    logger.info("获取股票数据")
    try:
        stock_code = request.args.get('code')
        if not stock_code:
            logger.warning("缺少股票代码参数")
            return jsonify({"error": "缺少股票代码参数"}), 400
        
        period = request.args.get('period', 'daily')
        count = int(request.args.get('count', 120))
        
        logger.debug(f"获取股票 {stock_code} 的{period}数据，{count}条")
        df = fetch_data(stock_code, period, count)
        
        if df is None:
            logger.error(f"获取股票 {stock_code} 数据失败")
            return jsonify({"error": f"获取股票 {stock_code} 数据失败"}), 500
        
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
                "high": float(row["high"]) if "high" in df.columns else 0,
                "low": float(row["low"]) if "low" in df.columns else 0,
                "close": float(row["close"]) if "close" in df.columns else 0,
                "volume": float(row["volume"]) if "volume" in df.columns else 0
            }
            
            # 单独处理RSI以避免行太长
            if "rsi" in df.columns:
                if pd.notna(row["rsi"]):
                    item["rsi"] = float(row["rsi"])
                else:
                    item["rsi"] = None
            
            data.append(item)
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"获取股票数据异常: {e}", exc_info=True)
        return jsonify({"error": f"获取股票数据异常: {str(e)}"}), 500


# API接口：评估规则
@app.route('/api/evaluate', methods=['POST'])
def api_evaluate_rules():
    logger.info("评估规则 - 开始处理请求")
    try:
        # 可以手动传入规则或使用配置文件中的规则
        if request.json and 'stocks' in request.json:
            config = request.json
            logger.debug(f"使用请求中的规则配置: {config}")
            stocks_count = len(config.get('stocks', []))
            logger.info(f"请求包含 {stocks_count} 只股票")
            for idx, stock in enumerate(config.get('stocks', [])):
                stock_code = stock.get('code', '')
                stock_name = stock.get('name', '')
                logger.debug(f"股票 {idx+1}/{stocks_count}: {stock_code} {stock_name}")
        else:
            config = load_config()
            logger.debug("使用配置文件中的规则配置")
        
        # 添加超时处理
        import threading
        import time
        import json
        
        evaluation_result = []
        evaluation_error = [None]
        evaluation_completed = [False]
        
        def evaluation_worker():
            try:
                logger.info("开始执行股票评估...")
                start_time = time.time()
                result = evaluate_rules(config)
                
                # 完全避免序列化问题的方法：预处理结果
                try:
                    # 将结果先转成JSON字符串，再解析回Python对象
                    # 这样会自动处理所有不兼容的数据类型
                    json_str = json.dumps(result, default=str)
                    processed_result = json.loads(json_str)
                    logger.debug("JSON预处理成功")
                except Exception as e:
                    logger.error(f"JSON预处理失败: {e}", exc_info=True)
                    
                    # 回退方案：手动序列化
                    processed_result = []
                    for item in result:
                        processed_item = process_dict(item)
                        processed_result.append(processed_item)
                    logger.debug("使用手动序列化作为回退")
                
                elapsed_time = time.time() - start_time
                logger.info(f"股票评估完成，耗时 {elapsed_time:.2f} 秒")
                evaluation_result.extend(processed_result)
                evaluation_completed[0] = True
            except Exception as e:
                logger.error(f"评估线程中发生异常: {e}", exc_info=True)
                evaluation_error[0] = str(e)
                evaluation_completed[0] = True
        
        def process_dict(item):
            """递归处理字典，确保所有值都是JSON可序列化的"""
            if isinstance(item, dict):
                return {k: process_dict(v) for k, v in item.items()}
            elif isinstance(item, list):
                return [process_dict(x) for x in item]
            elif isinstance(item, bool):
                return str(item).lower()  # 将布尔值转为字符串
            else:
                return item
        
        # 启动评估线程
        eval_thread = threading.Thread(target=evaluation_worker)
        eval_thread.daemon = True
        eval_thread.start()
        
        # 最多等待60秒
        max_wait_time = 60
        wait_interval = 0.5
        waited_time = 0
        
        while not evaluation_completed[0] and waited_time < max_wait_time:
            time.sleep(wait_interval)
            waited_time += wait_interval
            if waited_time % 5 == 0:  # 每5秒记录一次等待状态
                logger.info(f"等待评估完成...已等待 {waited_time} 秒")
        
        if not evaluation_completed[0]:
            error_msg = f"评估规则超时（超过 {max_wait_time} 秒）"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 504  # Gateway Timeout
        
        if evaluation_error[0]:
            error_msg = f"评估规则失败: {evaluation_error[0]}"
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 500
        
        logger.debug(f"评估成功，返回 {len(evaluation_result)} 条结果")
        
        # 返回结果
        return jsonify(evaluation_result)
    except Exception as e:
        logger.error(f"评估规则失败: {e}", exc_info=True)
        return jsonify({"error": f"评估规则失败: {str(e)}"}), 500


# 错误处理
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404错误: {request.path}")
    return jsonify({"error": f"找不到路径: {request.path}"}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"500错误: {error}")
    return jsonify({"error": "服务器内部错误"}), 500


if __name__ == '__main__':
    logger.info("启动API服务器，监听所有网络接口，端口8080")
    app.run(debug=True, host='0.0.0.0', port=8080) 