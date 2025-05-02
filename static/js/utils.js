/**
 * 工具函数模块
 */

// 日期格式化函数
function formatDate(timestamp) {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
}

// MACD条件格式化函数
function formatMacdCondition(rules) {
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
}

// 高低点突破条件格式化函数
function formatBreakoutCondition(rules) {
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
} 