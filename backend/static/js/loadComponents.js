/**
 * 组件加载脚本
 * 负责将HTML组件加载到页面的不同区域
 */

document.addEventListener('DOMContentLoaded', function() {
    // 1. 加载添加监控面板
    loadAddMonitorPanel();
    
    // 2. 加载股票监控列表
    loadStockListPanel();
    
    // 3. 加载告警历史面板
    loadAlertHistoryPanel();
    
    // 4. 加载监控结果模态窗口
    loadMonitorResultsModal();
});

// 异步加载组件HTML
async function loadComponent(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to load component: ${url}`);
        }
        return await response.text();
    } catch (error) {
        console.error(`Error loading component ${url}:`, error);
        return '';
    }
}

// 加载"添加监控"面板内容
async function loadAddMonitorPanel() {
    const addMonitorPanel = document.getElementById('add-monitor-panel');
    if (!addMonitorPanel) return;
    
    try {
        const content = await loadComponent('static/components/addMonitor.html');
        // 保留标题，替换内容区域
        const title = addMonitorPanel.querySelector('h2');
        addMonitorPanel.innerHTML = '';
        addMonitorPanel.appendChild(title);
        
        // 添加加载的内容
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = content;
        addMonitorPanel.appendChild(contentDiv);
    } catch (error) {
        console.error('Failed to load Add Monitor Panel:', error);
    }
}

// 加载股票监控列表内容
async function loadStockListPanel() {
    const stockListPanel = document.getElementById('stock-list-panel');
    if (!stockListPanel) return;
    
    try {
        const content = await loadComponent('static/components/stockList.html');
        
        // 保留标题和按钮
        const header = stockListPanel.querySelector('.flex.justify-between.items-center');
        stockListPanel.innerHTML = '';
        stockListPanel.appendChild(header);
        
        // 添加加载的内容
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = content;
        stockListPanel.appendChild(contentDiv);
    } catch (error) {
        console.error('Failed to load Stock List Panel:', error);
    }
}

// 加载告警历史面板内容
async function loadAlertHistoryPanel() {
    const alertHistoryPanel = document.getElementById('alert-history-panel');
    if (!alertHistoryPanel) return;
    
    try {
        const content = await loadComponent('static/components/alertHistory.html');
        
        // 保留标题
        const title = alertHistoryPanel.querySelector('h2');
        alertHistoryPanel.innerHTML = '';
        alertHistoryPanel.appendChild(title);
        
        // 添加加载的内容
        const contentDiv = document.createElement('div');
        contentDiv.innerHTML = content;
        alertHistoryPanel.appendChild(contentDiv);
    } catch (error) {
        console.error('Failed to load Alert History Panel:', error);
    }
}

// 加载监控结果模态窗口内容
async function loadMonitorResultsModal() {
    const monitorResultsModal = document.getElementById('monitor-results-modal');
    if (!monitorResultsModal) return;
    
    try {
        const content = await loadComponent('static/components/monitorResults.html');
        monitorResultsModal.innerHTML = content;
    } catch (error) {
        console.error('Failed to load Monitor Results Modal:', error);
    }
} 