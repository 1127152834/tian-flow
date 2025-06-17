'use client';

'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export type Locale = 'en' | 'zh';

interface LanguageContextType {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  messages: Record<string, any>;
  t: (key: string, params?: Record<string, any>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

interface LanguageProviderProps {
  children: React.ReactNode;
  defaultLocale?: Locale;
}

export function LanguageProvider({ children, defaultLocale = 'en' }: LanguageProviderProps) {
  const [locale, setLocaleState] = useState<Locale>(defaultLocale);
  const [messages, setMessages] = useState<Record<string, any>>({});

  // 加载翻译文件
  useEffect(() => {
    const loadMessages = async () => {
      try {
        const messagesModule = await import(`../../messages/${locale}.json`);
        setMessages(messagesModule.default);
      } catch (error) {
        console.error(`Failed to load messages for locale: ${locale}`, error);
        // 如果加载失败，尝试加载英文作为后备
        if (locale !== 'en') {
          try {
            const fallbackModule = await import(`../../messages/en.json`);
            setMessages(fallbackModule.default);
          } catch (fallbackError) {
            console.error('Failed to load fallback messages', fallbackError);
          }
        }
      }
    };

    loadMessages();
  }, [locale]);

  // 从localStorage恢复语言设置
  useEffect(() => {
    // 确保只在客户端执行
    if (typeof window !== 'undefined') {
      const savedLocale = localStorage.getItem('preferred-locale') as Locale;
      if (savedLocale && (savedLocale === 'en' || savedLocale === 'zh')) {
        setLocaleState(savedLocale);
      }
    }
  }, []);

  const setLocale = (newLocale: Locale) => {
    setLocaleState(newLocale);
    // 确保只在客户端执行
    if (typeof window !== 'undefined') {
      localStorage.setItem('preferred-locale', newLocale);
    }
  };

  // 翻译函数
  const t = (key: string, params?: Record<string, any>): string => {
    const keys = key.split('.');
    let value: any = messages;
    
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        // 如果找不到翻译，返回key本身
        return key;
      }
    }
    
    if (typeof value !== 'string') {
      return key;
    }
    
    // 简单的参数替换
    if (params) {
      return value.replace(/\{(\w+)\}/g, (match, paramKey) => {
        return params[paramKey] || match;
      });
    }
    
    return value;
  };

  return (
    <LanguageContext.Provider value={{ locale, setLocale, messages, t }}>
      {children}
    </LanguageContext.Provider>
  );
}
