#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
飞书消息推送模块
"""

import json
import requests
from datetime import datetime
from pathlib import Path


class FeishuPusher:
    """飞书消息推送器"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def send_message(self, content: dict) -> bool:
        """发送消息到飞书"""
        payload = {
            "msg_type": "interactive",
            "card": content
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            result = response.json()
            if result.get("code") == 0:
                print("[OK] 飞书消息发送成功")
                return True
            else:
                print(f"[ERROR] 飞书消息发送失败: {result}")
                return False
        except Exception as e:
            print(f"[ERROR] 飞书消息发送异常: {e}")
            return False

    def build_report_card(self, report_data: dict) -> dict:
        """构建复盘报告卡片"""

        date = report_data.get("date", datetime.now().strftime("%Y-%m-%d"))
        summary = report_data.get("summary", {})
        market_overview = report_data.get("market_overview", {})
        target_sectors = report_data.get("target_sectors", [])

        # 从 executive_summary 提取关键信息
        exec_summary = summary.get("executive_summary", "")
        market_intent = summary.get("market_intent", {})
        main_capital_flow = market_intent.get("main_capital_flow", "暂无数据")

        # 构建板块列表
        sector_elements = []
        for i, sector in enumerate(target_sectors[:5], 1):
            emotion_info = sector.get("emotion_cycle", {})
            emotion_stage = emotion_info.get("stage", "未知")

            emotion_emoji = {
                "分化期": "🔄",
                "修复期": "🔧",
                "高潮期": "🚀",
                "启动期": "🌱",
                "退潮期": "📉"
            }.get(emotion_stage, "📊")

            is_new = sector.get("is_new_face", False)
            new_badge = "🆕 " if is_new else ""

            sector_name = sector.get("sector_name", "未知")
            strength = sector.get("strength_score", 0)
            limit_up = sector.get("today_limit_up", 0)

            # 从 core_stocks 提取龙头股
            core_stocks = sector.get("core_stocks", {})
            leading_stock = core_stocks.get("leading_stock", {})
            leader_name = leading_stock.get("name", "无") if leading_stock else "无"

            sector_elements.append({
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"**{i}. {new_badge}{sector_name}**\n强度: {strength} | 涨停: {limit_up}只"
                        }
                    },
                    {
                        "is_short": True,
                        "text": {
                            "tag": "lark_md",
                            "content": f"{emotion_emoji} {emotion_stage}\n龙头: {leader_name}"
                        }
                    }
                ]
            })

        # 情绪周期分布
        emotion_dist = market_overview.get("emotion_distribution", {})
        emotion_text = " | ".join([f"{k}: {v}个" for k, v in emotion_dist.items()]) if emotion_dist else "暂无数据"

        # 从 market_overview 提取统计
        target_count = market_overview.get("target_sector_count", len(target_sectors))
        new_count = market_overview.get("new_face_count", 0)
        old_count = market_overview.get("old_face_count", 0)
        confidence = market_overview.get("confidence", 0.85)

        # 构建卡片 - 使用简单文本格式确保兼容性
        card = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"A股题材复盘报告 - {date}"
                },
                "template": "blue"
            },
            "elements": [
                # 执行摘要
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**市场概览**\n目标板块: {target_count}个 | 新面孔: {new_count}个 | 老面孔: {old_count}个\n置信度: {confidence * 100:.0f}%"
                    }
                },
                {
                    "tag": "hr"
                },
                # 资金意图
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**主力资金流向**\n{main_capital_flow[:300]}..."
                    }
                },
                {
                    "tag": "hr"
                },
                # 情绪周期
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**情绪周期分布**\n{emotion_text}"
                    }
                },
                {
                    "tag": "hr"
                },
                # 板块列表标题
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "**核心板块详情**"
                    }
                },
                # 板块列表
                *sector_elements,
                {
                    "tag": "hr"
                },
                # 风险提示
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": "本报告由AI系统自动生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。"
                        }
                    ]
                }
            ]
        }

        return card

    def push_report(self, report_path: str) -> bool:
        """推送复盘报告"""
        # 读取报告JSON
        json_path = Path(report_path).with_suffix('.json')
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            print(f"[OK] 已读取JSON报告: {json_path}")
        else:
            print(f"[ERROR] JSON文件不存在: {json_path}")
            return False

        # 打印数据摘要用于调试
        print(f"[DEBUG] 日期: {report_data.get('date')}")
        print(f"[DEBUG] 板块数: {len(report_data.get('target_sectors', []))}")

        card = self.build_report_card(report_data)
        return self.send_message(card)

    def parse_markdown_report(self, md_path: str) -> dict:
        """解析Markdown报告"""
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 简单解析
        import re

        # 提取日期
        date_match = re.search(r'\*\*分析日期\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
        date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")

        # 提取市场概览
        target_match = re.search(r'目标板块数:\s*(\d+)', content)
        new_match = re.search(r'新面孔:\s*(\d+)', content)
        old_match = re.search(r'老面孔:\s*(\d+)', content)
        confidence_match = re.search(r'\*\*置信度\*\*:\s*([\d.]+)', content)

        # 提取情绪周期分布
        emotion_dist = {}
        emotion_section = re.search(r'\*\*情绪周期分布\*\*:(.*?)(?=##|---)', content, re.DOTALL)
        if emotion_section:
            for line in emotion_section.group(1).strip().split('\n'):
                match = re.search(r'-\s*(\w+):\s*(\d+)', line)
                if match:
                    emotion_dist[match.group(1)] = int(match.group(2))

        # 提取主力资金流向
        capital_match = re.search(r'\*\*主力资金流向\*\*:\s*(.+?)(?:\n\n|\n\*\*)', content, re.DOTALL)
        capital_flow = capital_match.group(1).strip() if capital_match else "暂无数据"

        # 提取板块信息
        sectors = []
        sector_pattern = re.compile(
            r'###\s*(\d+)\.\s*(.+?)\n'
            r'.*?强度分数:\s*(\d+).*?'
            r'今日涨停数:\s*(\d+).*?'
            r'新旧标记:\s*(.+?).*?'
            r'\*\*情绪周期\*\*:\s*(\w+)',
            re.DOTALL
        )

        for match in sector_pattern.finditer(content):
            sectors.append({
                "name": match.group(2).strip(),
                "strength": int(match.group(3)),
                "limit_up_count": int(match.group(4)),
                "is_new": "新" in match.group(5),
                "emotion_stage": match.group(6)
            })

        # 提取龙头股
        leader_pattern = re.compile(r'\*主龙头股\*\*:\s*\*\*(.+?)\s*\(')
        for i, match in enumerate(leader_pattern.finditer(content)):
            if i < len(sectors):
                sectors[i]["leader"] = match.group(1).strip()

        return {
            "date": date,
            "summary": {
                "target_count": int(target_match.group(1)) if target_match else 0,
                "new_count": int(new_match.group(1)) if new_match else 0,
                "old_count": int(old_match.group(1)) if old_match else 0,
                "confidence": float(confidence_match.group(1)) if confidence_match else 0,
                "emotion_distribution": emotion_dist,
                "capital_flow": capital_flow
            },
            "sectors": sectors
        }


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='推送复盘报告到飞书')
    parser.add_argument('--report', '-r', required=True, help='报告文件路径(Markdown)')
    parser.add_argument('--webhook', '-w', required=True, help='飞书Webhook地址')

    args = parser.parse_args()

    pusher = FeishuPusher(args.webhook)
    success = pusher.push_report(args.report)

    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())