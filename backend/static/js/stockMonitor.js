function stockMonitor() {
    return {
        config: {
            wecom_webhook: '',
            stocks: []
        },
        akshareAvailable: true,
        tabs: ['基本条件', '均线交叉', 'MACD', '高低点突破', '量价背离', '价格回调'],
        activeTab: 0,
        newStock: {
            code: '',
            name: '',
            strategy_name: '',
            strategy_type: '基础监控',
            rules: {
                price_level: 0,
                consecutive_bars: 1,
                volume_multiple: 0,
                volume_lookback: 5,
                rsi_check: false,
                rsi_overbought: 70,
                rsi_oversold: 30,
                ma_check: false,
                fast_ma: 'ma5',
                slow_ma: 'ma20',
                macd_check: false,
                macd_fast: 12,
                macd_slow: 26,
                macd_signal: 9,
                macd_condition: 'golden_cross',
                price_breakout_check: false,
                breakout_periods: 20,
                breakout_type: 'high_low',
                breakout_threshold: 0
            }
        },
        stockData: [],
        showStockModal: false,
        currentStockIndex: -1,
        editMode: false,
        savedSuccessfully: false,
        showMonitorResults: false,
        isRunningMonitor: false,
        monitorResults: [],
        alertHistory: [],
        stocksRunningStatus: {},
        
        init() {
            // 初始化状态
            this.selectedStock = null;
            this.monitorResults = [];
            this.alertHistory = [];
            this.stocksRunningStatus = {}; // 确保初始化为空对象
            
            // 加载配置和状态
            this.loadConfig();
            this.checkApiStatus();
            this.loadAlertHistory();
        },
        
        loadConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    this.config = data;
                    
                    // 初始化每只股票的执行状态
                    this.config.stocks.forEach(stock => {
                        // 使用Alpine.js兼容方式设置属性
                        this.stocksRunningStatus[stock.code] = false;
                    });
                })
                .catch(error => {
                    console.error('加载配置失败:', error);
                    alert('加载配置失败，请检查网络连接');
                });
        },
        
        saveConfig() {
            fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.config)
            })
            .catch(error => {
                console.error('保存配置失败:', error);
                // 如果API不可用，使用本地存储
                localStorage.setItem('stockMonitorConfig', JSON.stringify(this.config));
            });
        },
        
        checkApiStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    this.akshareAvailable = data.akshare_available;
                })
                .catch(error => {
                    console.error('API状态检查失败:', error);
                    this.akshareAvailable = false;
                });
        },
        
        addStock() {
            if (!this.newStock.code) {
                alert('请输入股票代码');
                return;
            }
            
            if (!this.newStock.strategy_name) {
                alert('请输入策略名称');
                return;
            }
            
            // 创建策略对象
            const strategy = {
                strategy_name: this.newStock.strategy_name,
                strategy_type: this.newStock.strategy_type,
                rules: {...this.newStock.rules}
            };
            
            // 查找是否已存在相同代码的股票
            let stockIndex = this.config.stocks.findIndex(s => s.code === this.newStock.code);
            
            if (stockIndex >= 0) {
                // 已存在相同代码的股票，检查是否有strategies数组
                const stock = this.config.stocks[stockIndex];
                
                if (!stock.strategies) {
                    // 旧格式转换为新格式
                    stock.strategies = [];
                    
                    // 如果有旧的规则，将其转换为策略添加到数组中
                    if (stock.rules) {
                        stock.strategies.push({
                            strategy_name: stock.strategy_name || '基础监控',
                            strategy_type: stock.strategy_type || '基础监控',
                            rules: {...stock.rules}
                        });
                        
                        // 删除旧的属性
                        delete stock.rules;
                        delete stock.strategy_name;
                        delete stock.strategy_type;
                    }
                }
                
                // 检查是否已存在同名策略
                const existingStrategyIndex = stock.strategies.findIndex(
                    s => s.strategy_name === strategy.strategy_name
                );
                
                if (existingStrategyIndex >= 0) {
                    // 更新现有策略
                    stock.strategies[existingStrategyIndex] = strategy;
                    alert(`已更新 ${stock.name} 的 ${strategy.strategy_name} 策略`);
                } else {
                    // 添加新策略
                    stock.strategies.push(strategy);
                    alert(`已为 ${stock.name} 添加 ${strategy.strategy_name} 策略`);
                }
            } else {
                // 不存在相同代码的股票，创建新股票对象
                const stock = {
                    code: this.newStock.code,
                    name: this.newStock.name || this.newStock.code,
                    strategies: [strategy]
                };
                
                // 添加到配置中
                this.config.stocks.push(stock);
                alert(`已添加 ${stock.name} 的 ${strategy.strategy_name} 策略`);
            }
            
            // 保存配置
            this.saveConfig();
            
            // 重置表单
            this.resetForm();
        },
        
        removeStock(index, stockCode, strategyName) {
            if (confirm(`确定要删除 ${stockCode} 的 ${strategyName} 策略吗？`)) {
                if (index !== undefined) {
                    // 找到对应的股票
                    const stock = this.config.stocks[index];
                    
                    if (stock) {
                        if (stock.strategies && stock.strategies.length > 0) {
                            // 查找策略索引
                            const strategyIndex = stock.strategies.findIndex(
                                s => s.strategy_name === strategyName
                            );
                            
                            if (strategyIndex >= 0) {
                                // 删除特定策略
                                stock.strategies.splice(strategyIndex, 1);
                                
                                // 如果没有策略了，删除整个股票
                                if (stock.strategies.length === 0) {
                                    this.config.stocks.splice(index, 1);
                                }
                            }
                        } else {
                            // 旧结构，删除整个股票
                            this.config.stocks.splice(index, 1);
                        }
                    }
                } else {
                    // 通过股票代码和策略名称查找
                    const stockIndex = this.config.stocks.findIndex(s => s.code === stockCode);
                    
                    if (stockIndex >= 0) {
                        const stock = this.config.stocks[stockIndex];
                        
                        if (stock.strategies && stock.strategies.length > 0) {
                            // 查找策略索引
                            const strategyIndex = stock.strategies.findIndex(
                                s => s.strategy_name === strategyName
                            );
                            
                            if (strategyIndex >= 0) {
                                // 删除特定策略
                                stock.strategies.splice(strategyIndex, 1);
                                
                                // 如果没有策略了，删除整个股票
                                if (stock.strategies.length === 0) {
                                    this.config.stocks.splice(stockIndex, 1);
                                }
                            }
                        } else if (stock.strategy_name === strategyName) {
                            // 旧结构，删除整个股票
                            this.config.stocks.splice(stockIndex, 1);
                        }
                    }
                }
                
                this.saveConfig();
            }
        },
        
        fetchStockData(stockCode) {
            if (!stockCode) return;
            
            fetch(`/api/stock_data?code=${stockCode}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (!data || data.error) {
                        throw new Error(data.error || '获取数据失败');
                    }
                    
                    // 找到对应的股票信息
                    const stock = this.config.stocks.find(s => s.code === stockCode);
                    if (!stock) {
                        throw new Error('未找到该股票，请先添加到监控列表');
                    }
                    
                    this.selectedStock = stock;
                    this.updateChart(data, stock);
                    
                    // 处理新的数据结构
                    if (stock.strategies && stock.strategies.length > 0) {
                        // 使用第一个策略的规则填充表单
                        const strategy = stock.strategies[0];
                        this.newStock = {
                            code: stock.code,
                            name: stock.name,
                            strategy_name: strategy.strategy_name,
                            strategy_type: strategy.strategy_type,
                            rules: {...strategy.rules}
                        };
                        
                        // 根据选中的规则自动切换到相应的选项卡
                        if (strategy.rules.macd_check) {
                            this.activeTab = 2; // MACD选项卡
                        } else if (strategy.rules.ma_check) {
                            this.activeTab = 1; // 均线交叉选项卡
                        } else {
                            this.activeTab = 0; // 基本条件选项卡
                        }
                    } else if (stock.rules) {
                        // 兼容旧的数据结构
                        this.newStock = {
                            code: stock.code,
                            name: stock.name,
                            strategy_name: stock.strategy_name,
                            strategy_type: stock.strategy_type,
                            rules: {...stock.rules}
                        };
                        
                        // 根据选中的规则自动切换到相应的选项卡
                        if (stock.rules.macd_check) {
                            this.activeTab = 2; // MACD选项卡
                        } else if (stock.rules.ma_check) {
                            this.activeTab = 1; // 均线交叉选项卡
                        } else {
                            this.activeTab = 0; // 基本条件选项卡
                        }
                    } else {
                        // 如果没有规则，重置表单
                        this.resetForm();
                        this.newStock.code = stock.code;
                        this.newStock.name = stock.name;
                    }
                })
                .catch(error => {
                    console.error('获取股票数据失败:', error);
                    alert('获取股票数据失败，请检查网络连接和股票代码');
                });
        },
        
        updateChart(data, stock) {
            if (!stock) return;
            
            const ctx = document.getElementById('stockChart').getContext('2d');
            
            if (this.stockChart) {
                this.stockChart.destroy();
            }
            
            const dates = data.map(item => item.date);
            const prices = data.map(item => item.close);
            
            this.stockChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: `${stock.name || stock.code} 收盘价`,
                        data: prices,
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    },
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: '日期'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: '价格'
                            }
                        }
                    }
                }
            });
        },
        
        formatDate(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleString('zh-CN');
        },
        
        isUpdatingStock() {
            // 检查当前表单中的股票代码是否已存在于监控列表中
            if (!this.newStock.code) return false;
            return this.config.stocks.some(stock => stock.code === this.newStock.code);
        },
        
        resetForm() {
            this.newStock = {
                code: '',
                name: '',
                strategy_name: '',
                strategy_type: '基础监控',
                rules: {
                    price_level: 0,
                    consecutive_bars: 1,
                    volume_multiple: 0,
                    volume_lookback: 5,
                    rsi_check: false,
                    rsi_overbought: 70,
                    rsi_oversold: 30,
                    ma_check: false,
                    fast_ma: 'ma5',
                    slow_ma: 'ma20',
                    macd_check: false,
                    macd_fast: 12,
                    macd_slow: 26,
                    macd_signal: 9,
                    macd_condition: 'golden_cross',
                    price_breakout_check: false,
                    breakout_periods: 20,
                    breakout_type: 'high_low',
                    breakout_threshold: 0
                }
            };
            this.activeTab = 0; // 重置回第一个选项卡
        },
        
        runMonitoring() {
            if (this.isRunningMonitor) return;
            this.isRunningMonitor = true;
            
            // 同时将所有股票设置为执行中状态
            this.config.stocks.forEach(stock => {
                // 使用Alpine.js兼容方式设置属性
                this.stocksRunningStatus[stock.code] = true;
            });
            
            // 计算超时时间：基础120秒，每只股票增加15秒，最长10分钟
            const stockCount = this.config.stocks.length;
            const baseTimeout = 120000; // 基础120秒
            const perStockTime = 15000; // 每只股票15秒
            const timeoutDuration = Math.min(600000, baseTimeout + stockCount * perStockTime); // 最长10分钟
            
            console.log(`开始执行${stockCount}只股票的监控...设置超时时间为${timeoutDuration/1000}秒`);
            
            // 显示提示消息
            if (stockCount > 5) {
                alert(`正在监控${stockCount}只股票，可能需要较长时间，请耐心等待...`);
            }
            
            // 设置请求超时时间
            const monitoringTimeout = setTimeout(() => {
                if (this.isRunningMonitor) {
                    console.error("监控请求超时");
                    alert(`监控执行超时（${timeoutDuration/1000}秒），请尝试减少监控的股票数量或分批监控`);
                    this.isRunningMonitor = false;
                    
                    // 重置所有股票的状态
                    this.config.stocks.forEach(stock => {
                        // 使用Alpine.js兼容方式设置属性
                        this.stocksRunningStatus[stock.code] = false;
                    });
                }
            }, timeoutDuration); // 动态超时时间
            
            fetch('/api/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.config)
            })
            .then(response => {
                clearTimeout(monitoringTimeout);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
                }
                return response.json();
            })
            .then(results => {
                console.log("监控执行完成", results);
                this.isRunningMonitor = false;
                
                // 重置所有股票的状态
                this.config.stocks.forEach(stock => {
                    this.stocksRunningStatus[stock.code] = false;
                });
                
                this.lastMonitorTime = new Date().getTime();
                
                // 确保结果是数组
                if (!Array.isArray(results)) {
                    console.error('返回结果不是数组:', results);
                    results = [];
                }
                
                // 保存监控结果用于详细显示
                this.monitorResults = results;
                
                // 处理监控结果
                if (results.length === 0) {
                    // 显示空的监控结果窗口
                    this.showMonitorResults = true;
                    return;
                }
                
                // 将结果添加到告警历史
                const now = new Date().getTime();
                results.forEach(result => {
                    if (!result || !result.code || result.action === 'none') return;
                    
                    this.alertHistory.unshift({
                        stock_code: result.code,
                        stock_name: result.name,
                        strategy_name: result.strategy_name || '默认策略',
                        strategy_type: result.strategy_type || '基础监控',
                        action_display: result.action_display || (result.action === 'buy' ? '买入' : result.action === 'sell' ? '卖出' : '提示'),
                        type: result.action === 'buy' ? 'success' : result.action === 'sell' ? 'danger' : 'warning',
                        time: new Date().toLocaleString(),
                        content: result.message || `${result.name}(${result.code}) 触发监控`
                    });
                });
                
                // 只保留最近的50条记录
                if (this.alertHistory.length > 50) {
                    this.alertHistory = this.alertHistory.slice(0, 50);
                }
                
                // 保存告警历史
                this.saveAlertHistory();
                
                // 显示监控结果窗口
                this.showMonitorResults = true;
            })
            .catch(error => {
                clearTimeout(monitoringTimeout);
                console.error('执行监控失败:', error);
                
                let errorMessage = '执行监控失败';
                if (error.message) {
                    errorMessage += `: ${error.message}`;
                }
                
                alert(errorMessage);
                this.isRunningMonitor = false;
                
                // 重置所有股票的状态
                this.config.stocks.forEach(stock => {
                    this.stocksRunningStatus[stock.code] = false;
                });
            });
        },
        
        // 尝试从本地存储加载告警历史
        loadAlertHistory() {
            const storedHistory = localStorage.getItem('stockAlertHistory');
            if (storedHistory) {
                try {
                    this.alertHistory = JSON.parse(storedHistory);
                } catch (e) {
                    console.error('解析告警历史失败:', e);
                    this.alertHistory = [];
                }
            }
            
            // 加载上次监控时间
            const lastTime = localStorage.getItem('lastMonitorTime');
            if (lastTime) {
                this.lastMonitorTime = parseInt(lastTime);
            }
        },
        
        // 保存告警历史到本地存储
        saveAlertHistory() {
            localStorage.setItem('stockAlertHistory', JSON.stringify(this.alertHistory));
            localStorage.setItem('lastMonitorTime', this.lastMonitorTime.toString());
        },
        
        formatMacdCondition(rules) {
            if (!rules || !rules.macd_condition) return '';
            
            // 参数部分
            const params = `${rules.macd_fast}/${rules.macd_slow}/${rules.macd_signal}`;
            
            // 条件描述
            let condition = '';
            switch (rules.macd_condition) {
                case 'golden_cross':
                    condition = '金叉信号';
                    break;
                case 'death_cross':
                    condition = '死叉信号';
                    break;
                case 'histogram_increase':
                    condition = '柱状图放大';
                    break;
                case 'histogram_decrease':
                    condition = '柱状图缩小';
                    break;
                case 'zero_axis_cross_up':
                    condition = '上穿零轴';
                    break;
                case 'zero_axis_cross_down':
                    condition = '下穿零轴';
                    break;
                default:
                    condition = rules.macd_condition;
            }
            
            return `${params} (${condition})`;
        },
        
        formatBreakoutCondition(rules) {
            if (!rules || !rules.price_breakout_check) return '';
            
            // 周期
            const periods = rules.breakout_periods || 20;
            
            // 突破类型
            let breakoutType = '';
            switch (rules.breakout_type) {
                case 'high_only':
                    breakoutType = '高点突破';
                    break;
                case 'low_only':
                    breakoutType = '低点突破';
                    break;
                case 'high_low':
                default:
                    breakoutType = '高低点突破';
            }
            
            // 阈值
            const threshold = rules.breakout_threshold > 0 
                ? `阈值${rules.breakout_threshold}%` 
                : '精确突破';
            
            return `${periods}周期 (${breakoutType}, ${threshold})`;
        },
        
        runMonitoringForStock(stock, index) {
            if (this.stocksRunningStatus[stock.code]) return;
            
            // 更新状态
            this.stocksRunningStatus[stock.code] = true;
            console.log(`执行单只股票监控: ${stock.code} ${stock.name}`);
            
            // 设置请求超时时间
            const monitoringTimeout = setTimeout(() => {
                if (this.stocksRunningStatus[stock.code]) {
                    console.error(`单股票监控请求超时: ${stock.code}`);
                    alert(`监控执行超时: ${stock.name || stock.code}`);
                    this.stocksRunningStatus[stock.code] = false;
                }
            }, 30000); // 30秒超时 - 单只股票处理应该更快
            
            // 构建只包含单只股票的临时配置
            const tempConfig = {
                wecom_webhook: this.config.wecom_webhook,
                stocks: [stock]
            };
            
            fetch('/api/evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(tempConfig)
            })
            .then(response => {
                clearTimeout(monitoringTimeout);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
                }
                return response.json();
            })
            .then(results => {
                console.log(`单股票监控执行完成: ${stock.code}`, results);
                this.stocksRunningStatus[stock.code] = false;
                this.lastMonitorTime = Date.now();
                
                // 确保结果是数组
                if (!Array.isArray(results)) {
                    console.error('返回结果不是数组:', results);
                    results = [];
                }
                
                // 更新结果
                this.monitorResults = results;
                
                // 记录告警
                results.forEach(result => {
                    if (result && result.action !== 'none') {
                        this.alertHistory.unshift({
                            stock_code: result.code,
                            stock_name: result.name,
                            strategy_name: result.strategy_name,
                            strategy_type: result.strategy_type,
                            message: result.message,
                            time: Date.now(),
                            type: result.action === 'buy' ? 'success' : 
                                  result.action === 'sell' ? 'danger' : 'warning',
                            action_display: result.action_display
                        });
                    }
                });
                
                // 仅保留最近100条告警
                if (this.alertHistory.length > 100) {
                    this.alertHistory = this.alertHistory.slice(0, 100);
                }
                
                // 保存告警历史到本地存储
                this.saveAlertHistory();
                
                // 显示监控结果窗口
                this.showMonitorResults = true;
            })
            .catch(error => {
                clearTimeout(monitoringTimeout);
                console.error(`执行单股票监控失败: ${stock.code}`, error);
                
                let errorMessage = `执行监控失败: ${stock.name || stock.code}`;
                if (error.message) {
                    errorMessage += `\n${error.message}`;
                }
                
                alert(errorMessage);
                this.stocksRunningStatus[stock.code] = false;
            });
        }
    };
} 