"""Statistics service.

Statistika hisoblash va grafik generatsiya qilish.
"""
import io
from datetime import datetime, timedelta
from typing import List, Optional
from collections import defaultdict

from src.core.models import Progress


class StatisticsService:
    """Statistika bilan ishlash uchun service."""

    def __init__(self):
        pass

    def generate_chart(self, progress_list: List[Progress], days: int = 30) -> Optional[bytes]:
        """
        Matplotlib bilan grafik yaratish.
        
        Args:
            progress_list: Progress ro'yxati
            days: Necha kunlik ma'lumot
            
        Returns:
            PNG rasm bytes yoki None
        """
        if not progress_list:
            return None
        
        try:
            import matplotlib
            matplotlib.use('Agg')  # GUI bo'lmagan backend
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
        except ImportError:
            return None
        
        # Kunlik natijalarni guruhlash
        daily_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        
        for p in progress_list:
            if p.completed_at:
                date_key = p.completed_at.date()
                daily_stats[date_key]["correct"] += p.correct_answers
                daily_stats[date_key]["total"] += p.total_questions
        
        if not daily_stats:
            return None
        
        # Ma'lumotlarni tartiblash
        sorted_dates = sorted(daily_stats.keys())
        dates = sorted_dates
        percentages = []
        
        for date in dates:
            stats = daily_stats[date]
            if stats["total"] > 0:
                percent = (stats["correct"] / stats["total"]) * 100
            else:
                percent = 0
            percentages.append(percent)
        
        # Grafik yaratish
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Chiziq grafik
        ax.plot(dates, percentages, marker='o', linewidth=2, markersize=6, 
                color='#2196F3', markerfacecolor='#1976D2')
        
        # O'rtacha chiziq
        if percentages:
            avg = sum(percentages) / len(percentages)
            ax.axhline(y=avg, color='#FF9800', linestyle='--', 
                      label=f'O\'rtacha: {avg:.1f}%', alpha=0.7)
        
        # Stil
        ax.set_xlabel('Sana', fontsize=12)
        ax.set_ylabel('To\'g\'ri javoblar (%)', fontsize=12)
        ax.set_title('Kunlik natijalar', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='lower right')
        
        # Sana formatlash
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates)//7)))
        plt.xticks(rotation=45)
        
        # Fill area
        ax.fill_between(dates, percentages, alpha=0.2, color='#2196F3')
        
        plt.tight_layout()
        
        # Bytes ga o'girish
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        
        return buf.getvalue()

    def calculate_summary(self, total_stats: dict) -> dict:
        """
        Umumiy statistikani hisoblash.
        
        Args:
            total_stats: Database dan kelgan stats
            
        Returns:
            Hisoblangan summary
        """
        total_games = total_stats.get("total_games", 0)
        total_correct = total_stats.get("total_correct", 0)
        total_questions = total_stats.get("total_questions", 0)
        
        percent = 0
        if total_questions > 0:
            percent = int((total_correct / total_questions) * 100)
        
        return {
            "total_games": total_games,
            "correct": total_correct,
            "total": total_questions,
            "percent": percent,
        }
