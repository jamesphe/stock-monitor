/**
 * 股票监控系统组件模块
 * 包含各种可重用的HTML模板函数
 */

// 策略类型标签生成函数
function strategyTypeLabel(strategyType) {
    const classes = {
        '建仓': 'bg-green-100 text-green-800',
        '加仓': 'bg-blue-100 text-blue-800',
        '减仓': 'bg-orange-100 text-orange-800',
        '清仓': 'bg-red-100 text-red-800',
        '基础监控': 'bg-gray-100 text-gray-800'
    };
    
    const type = strategyType || '基础监控';
    const className = classes[type] || classes['基础监控'];
    
    return `<span class="text-xs px-2 py-1 rounded ml-2 ${className}">${type}</span>`;
}

// 监控结果类型标签生成函数
function monitorResultLabel(action) {
    const classes = {
        'buy': 'bg-green-100 text-green-800',
        'sell': 'bg-red-100 text-red-800',
        'warning': 'bg-yellow-100 text-yellow-800',
        'none': 'bg-gray-100 text-gray-800'
    };
    
    const displayText = {
        'buy': '买入信号',
        'sell': '卖出信号',
        'warning': '监控信号',
        'none': '无动作'
    };
    
    const className = classes[action] || classes['none'];
    const text = displayText[action] || displayText['none'];
    
    return `<span class="px-2 py-1 rounded text-xs font-semibold ${className}">${text}</span>`;
}

// 监控详情条目生成函数
function monitorDetailItem(detail, title) {
    if (!detail) return '';
    
    const passClass = detail.pass ? 'text-green-600' : 'text-red-600';
    const passText = detail.pass ? '通过' : '未通过';
    
    return `
    <div class="ml-2 p-2 bg-white rounded border border-gray-200">
        <p class="flex justify-between">
            <span>${title || '条件'}:</span>
            <span class="${passClass}">${passText}</span>
        </p>
        <p class="text-xs text-gray-600 mt-1">${detail.description}</p>
    </div>
    `;
} 