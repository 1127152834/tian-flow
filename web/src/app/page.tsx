// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from 'next/dynamic';

// 禁用SSR，避免水合问题
function HomePageComponent() {

  const router = useRouter();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [titleRef, setTitleRef] = useState<HTMLElement | null>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  const handleEnterChat = () => {
    router.push("/chat");
  };

  // 防止探照灯效果在页面边缘出现问题
  const clampedMousePosition = {
    x: Math.max(200, Math.min(mousePosition.x, window.innerWidth - 200)),
    y: Math.max(200, Math.min(mousePosition.y, window.innerHeight - 200))
  };

  // 计算探照灯照射到标题文字的具体位置
  const getLightTextIntersection = () => {
    if (!titleRef) return { isLit: false, lightX: 0, lightY: 0, intensity: 0 };
    
    const rect = titleRef.getBoundingClientRect();
    const lightRadius = 300;
    
    // 计算光束中心到文字区域的距离
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    const distance = Math.sqrt(
      Math.pow(clampedMousePosition.x - centerX, 2) + 
      Math.pow(clampedMousePosition.y - centerY, 2)
    );
    
    // 检查光束是否与文字区域相交
    const isIntersecting = (
      clampedMousePosition.x >= rect.left - lightRadius/2 &&
      clampedMousePosition.x <= rect.right + lightRadius/2 &&
      clampedMousePosition.y >= rect.top - lightRadius/2 &&
      clampedMousePosition.y <= rect.bottom + lightRadius/2
    );
    
    return {
      isLit: isIntersecting,
      lightX: clampedMousePosition.x,
      lightY: clampedMousePosition.y,
      intensity: isIntersecting ? Math.max(0, 1 - distance / lightRadius) : 0
    };
  };

  const lightIntersection = getLightTextIntersection();

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-black">
      {/* 背景粒子效果 */}
      <div className="absolute inset-0">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`,
            }}
          >
            <div className="h-1 w-1 rounded-full bg-blue-300 opacity-30"></div>
          </div>
        ))}
      </div>



      {/* 探照灯效果 - 更大的光束跟随鼠标 */}
      <div
        className="pointer-events-none absolute inset-0 z-30"
        style={{
          background: `radial-gradient(circle 300px at ${clampedMousePosition.x}px ${clampedMousePosition.y}px, 
            transparent 0%, 
            transparent 25%, 
            rgba(0, 0, 0, 0.3) 45%, 
            rgba(0, 0, 0, 0.7) 65%, 
            rgba(0, 0, 0, 0.95) 100%)`,
          transition: 'background 0.1s ease-out',
        }}
      ></div>

      {/* 主内容区域 */}
      <div className="relative z-50 flex min-h-screen flex-col items-center justify-center px-8">
        {/* 品牌标识 */}
        <div className="mb-24 text-center">
          <h1 
            ref={setTitleRef}
            className="mb-6 text-8xl font-bold md:text-9xl lg:text-[12rem] xl:text-[14rem] bg-gradient-to-r from-orange-400 via-orange-300 to-yellow-300 bg-clip-text text-transparent relative overflow-hidden"
          >
            {/* 被照射的文字层 */}
            {lightIntersection.isLit && (
              <span 
                className="absolute inset-0 bg-gradient-to-r from-yellow-100 via-white to-yellow-100 bg-clip-text text-transparent transition-all duration-200"
                style={{
                  opacity: lightIntersection.intensity * 0.9,
                  filter: `brightness(2) contrast(1.5) drop-shadow(0 0 30px rgba(255,248,220,${lightIntersection.intensity}))`,
                  textShadow: `0 0 50px rgba(255,248,220,${lightIntersection.intensity * 0.8}), 0 0 100px rgba(255,248,220,${lightIntersection.intensity * 0.4})`,
                  maskImage: `radial-gradient(circle 300px at ${lightIntersection.lightX - (titleRef?.getBoundingClientRect().left || 0)}px ${lightIntersection.lightY - (titleRef?.getBoundingClientRect().top || 0)}px, 
                      rgba(255,255,255,1) 0%, 
                      rgba(255,255,255,0.8) 40%, 
                      rgba(255,255,255,0.3) 70%, 
                      transparent 100%)`,
                  WebkitMaskImage: `radial-gradient(circle 300px at ${lightIntersection.lightX - (titleRef?.getBoundingClientRect().left || 0)}px ${lightIntersection.lightY - (titleRef?.getBoundingClientRect().top || 0)}px, 
                      rgba(255,255,255,1) 0%, 
                      rgba(255,255,255,0.8) 40%, 
                      rgba(255,255,255,0.3) 70%, 
                      transparent 100%)`
                }}
              >
                Olight AI
              </span>
            )}
            {/* 原始文字层 */}
            <span>Olight AI</span>
          </h1>
          <div 
            className="h-1 w-48 mx-auto transition-all duration-200 bg-gradient-to-r from-transparent via-orange-400 to-transparent"
            style={{
              background: lightIntersection.isLit 
                ? 'linear-gradient(to right, transparent, #fef3c7, transparent)' 
                : undefined,
              boxShadow: lightIntersection.isLit 
                ? `0 0 20px rgba(255,248,220,${lightIntersection.intensity * 0.8})` 
                : 'none'
            }}
          ></div>
        </div>

        {/* 主按钮 - 手电筒造型 */}
        <div className="relative">
          <button
            onClick={handleEnterChat}
            className="group relative transform transition-all duration-300 hover:scale-110"
          >
            {/* 按钮光晕效果 */}
            <div className="absolute -inset-6 rounded-full bg-orange-400 opacity-0 blur-xl transition-opacity duration-300 group-hover:opacity-40"></div>
            
            {/* 手电筒主体 */}
            <div className="relative flex items-center space-x-4 rounded-full bg-gradient-to-r from-gray-800 to-gray-700 px-10 py-5 shadow-2xl">
              {/* 手电筒图标 */}
              <div className="relative">
                <div className="h-10 w-10 rounded-full bg-gradient-to-r from-orange-400 to-yellow-400 shadow-lg">
                  <div className="absolute inset-1 rounded-full bg-gradient-to-r from-yellow-300 to-orange-300"></div>
                  <div className="absolute inset-2 rounded-full bg-white opacity-80"></div>
                </div>
                {/* 悬停光束效果 */}
                <div className="absolute -right-3 top-1/2 h-0.5 w-10 -translate-y-1/2 bg-gradient-to-r from-yellow-300 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
              </div>
              
              {/* 按钮文字 */}
              <span className="text-2xl font-semibold text-white">进入 AI 助手</span>
            </div>
          </button>
        </div>


      </div>

      {/* CSS 样式 */}
      <style jsx>{`
        .animate-pulse {
          animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }

        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
      `}</style>
    </div>
  );
}

const HomePage = dynamic(() => Promise.resolve(HomePageComponent), {
  ssr: false,
});

export default HomePage;