// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 全局 WebSocket 管理器
 * 统一管理所有 WebSocket 连接和消息分发
 */

interface WebSocketMessage {
  type: string;
  task_id?: string;
  thread_id?: string;
  [key: string]: any;
}

type MessageHandler = (message: WebSocketMessage) => void;

class GlobalWebSocketManager {
  private websocket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private readonly maxReconnectAttempts = 5;
  private readonly reconnectDelay = 5000;
  private messageHandlers = new Map<string, Set<MessageHandler>>();
  private isConnecting = false;

  constructor() {
    if (typeof window !== 'undefined') {
      this.init();
    }
  }

  private init() {
    // 等待页面完全加载后再初始化
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.connect());
    } else {
      this.connect();
    }

    // 页面卸载时清理连接
    window.addEventListener('beforeunload', () => this.disconnect());
  }

  private connect() {
    if (this.isConnecting || this.websocket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.isConnecting = true;

    try {
      // 使用后端服务端口 8000，而不是前端端口 3000
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const backendHost = window.location.hostname + ':8000';
      const wsUrl = `${protocol}//${backendHost}/api/ws/progress/global_listener`;

      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('🌐 全局 WebSocket 连接已建立');
        this.reconnectAttempts = 0;
        this.isConnecting = false;
      };

      this.websocket.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('🌐 收到 WebSocket 消息:', message);
          this.handleMessage(message);
        } catch (error) {
          console.error('🌐 解析 WebSocket 消息失败:', error);
        }
      };

      this.websocket.onclose = () => {
        console.log('🌐 全局 WebSocket 连接已关闭');
        this.websocket = null;
        this.isConnecting = false;

        // 尝试重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`🌐 尝试重连 WebSocket (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          setTimeout(() => this.connect(), this.reconnectDelay);
        } else {
          console.error('🌐 WebSocket 重连失败，已达到最大重试次数');
        }
      };

      this.websocket.onerror = (error) => {
        console.error('🌐 WebSocket 连接错误:', error);
        this.isConnecting = false;
      };

    } catch (error) {
      console.error('🌐 创建 WebSocket 连接失败:', error);
      this.isConnecting = false;
    }
  }

  private handleMessage(message: WebSocketMessage) {
    const { type } = message;

    // 分发给注册的处理器
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error(`🌐 消息处理器错误 (${type}):`, error);
        }
      });
    }

    // 同时触发自定义事件（向后兼容）
    const customEvent = new CustomEvent(`websocket-${type}`, {
      detail: message
    });
    window.dispatchEvent(customEvent);
  }

  // 注册消息处理器
  public subscribe(messageType: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, new Set());
    }

    this.messageHandlers.get(messageType)!.add(handler);

    // 返回取消订阅函数
    return () => {
      const handlers = this.messageHandlers.get(messageType);
      if (handlers) {
        handlers.delete(handler);
        if (handlers.size === 0) {
          this.messageHandlers.delete(messageType);
        }
      }
    };
  }

  // 发送消息
  public send(message: any) {
    if (this.websocket?.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    } else {
      console.warn('🌐 WebSocket 未连接，无法发送消息');
    }
  }

  // 断开连接
  public disconnect() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }

  // 获取连接状态
  public get isConnected(): boolean {
    return this.websocket?.readyState === WebSocket.OPEN;
  }
}

// 创建全局实例
export const globalWebSocketManager = new GlobalWebSocketManager();

// 向后兼容的函数
export function initChartWebSocketListener() {
  // 图表消息处理器
  globalWebSocketManager.subscribe('chart', (message) => {
    if (message.chart_config) {
      const chartEvent = new CustomEvent('chart-received', {
        detail: {
          chart_config: message.chart_config,
          data_points: message.data_points,
          title: message.message,
          task_id: message.task_id,
          thread_id: message.thread_id
        }
      });
      window.dispatchEvent(chartEvent);
    }
  });
}

export function closeChartWebSocket() {
  // 现在由全局管理器处理
}

// 自动初始化图表监听器
if (typeof window !== 'undefined') {
  initChartWebSocketListener();
}
