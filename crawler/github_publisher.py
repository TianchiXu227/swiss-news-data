#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
瑞士新闻GitHub Pages发布器 - 简化版
"""

import json
import os
import requests
import time
from datetime import datetime, timezone
from bs4 import BeautifulSoup

class SwissNewsPublisher:
    def __init__(self):
        self.data_dir = 'data'
        self.details_dir = 'details'
        
        # 确保目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.details_dir, exist_ok=True)
        
    def crawl_news(self):
        """抓取瑞士新闻"""
        print("🚀 开始抓取瑞士新闻...")
        
        sources = [
            {
                'name': '瑞士联邦政府',
                'url': 'https://www.admin.ch/gov/en/start/documentation/media-releases.html',
                'base_url': 'https://www.admin.ch'
            },
            {
                'name': '瑞士外交部',
                'url': 'https://www.eda.admin.ch/eda/en/fdfa/fdfa/aktuell/news.html',
                'base_url': 'https://www.eda.admin.ch'
            }
        ]
        
        all_news = []
        
        for source in sources:
            try:
                news_items = self._crawl_single_source(source)
                all_news.extend(news_items)
                print(f"✅ 从 {source['name']} 获取了 {len(news_items)} 条新闻")
                time.sleep(2)
            except Exception as e:
                print(f"❌ 抓取 {source['name']} 失败: {e}")
        
        # 按时间排序
        all_news.sort(key=lambda x: x.get('publishTime', ''), reverse=True)
        
        print(f"🎯 总共抓取了 {len(all_news)} 条新闻")
        return all_news
    
    def _crawl_single_source(self, source):
        """抓取单个新闻源"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        response = requests.get(source['url'], headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        news_items = []
        
        # 查找新闻链接
        links = soup.find_all('a', href=True)[:20]
        
        for i, link in enumerate(links):
            try:
                title = link.get_text(strip=True)
                url = link.get('href', '')
                
                if not title or len(title) < 10:
                    continue
                    
                if url and not url.startswith('http'):
                    url = f"{source['base_url']}{url}"
                
                news_item = {
                    'id': f"{source['name']}_{i}_{int(time.time())}",
                    'title': title,
                    'titleChinese': title,
                    'source': source['name'],
                    'url': url,
                    'publishTime': datetime.now(timezone.utc).isoformat(),
                    'category': 'government',
                    'language': 'en',
                    'extractedAt': datetime.now(timezone.utc).isoformat(),
                    'extractedBy': 'github-pages-crawler'
                }
                
                news_items.append(news_item)
                
                if len(news_items) >= 10:  # 每个源最多10条
                    break
                    
            except Exception as e:
                continue
        
        return news_items
    
    def publish_to_github(self, news_data):
        """发布新闻数据到GitHub Pages"""
        try:
            # 保存完整新闻列表
            news_file = os.path.join(self.data_dir, 'news.json')
            with open(news_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'lastUpdated': datetime.now(timezone.utc).isoformat(),
                    'totalCount': len(news_data),
                    'version': '1.0.0',
                    'source': 'GitHub Pages Crawler',
                    'news': news_data
                }, f, ensure_ascii=False, indent=2)
            
            # 保存最新新闻列表
            latest_file = os.path.join(self.data_dir, 'latest.json')
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'lastUpdated': datetime.now(timezone.utc).isoformat(),
                    'count': min(10, len(news_data)),
                    'news': news_data[:10]
                }, f, ensure_ascii=False, indent=2)
            
            # 保存新闻详情
            for news in news_data:
                detail_file = os.path.join(self.details_dir, f"{news['id']}.json")
                with open(detail_file, 'w', encoding='utf-8') as f:
                    json.dump(news, f, ensure_ascii=False, indent=2)
            
            print("✅ 所有数据文件已生成完成")
            return True
            
        except Exception as e:
            print(f"❌ 发布数据失败: {e}")
            return False

def main():
    """主函数"""
    print("🌐 瑞士新闻 GitHub Pages 发布器启动")
    print("=" * 50)
    
    publisher = SwissNewsPublisher()
    
    # 抓取新闻
    news_data = publisher.crawl_news()
    
    if not news_data:
        print("❌ 没有抓取到任何新闻数据")
        return False
    
    # 发布到GitHub Pages
    success = publisher.publish_to_github(news_data)
    
    if success:
        print("🎉 新闻数据已成功发布到GitHub Pages!")
        return True
    else:
        print("❌ 发布失败")
        return False

if __name__ == '__main__':
    main()
