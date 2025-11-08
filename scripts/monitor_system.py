#!/usr/bin/env python3
"""
System Monitoring Script for Phone Unlock AI
Monitors system health and performs self-healing
"""

import time
import logging
import schedule
from datetime import datetime
import json

# Add project root to path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SystemMonitor:
    def __init__(self):
        self.setup_logging()
        self.health_history = []
        self.self_healing = None
        
    def setup_logging(self):
        """Setup monitoring logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/system_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SystemMonitor')
        
    def initialize_self_healing(self):
        """Initialize self-healing system"""
        try:
            from backend.services.self_healing import SelfHealingSystem
            self.self_healing = SelfHealingSystem()
            self.logger.info("Self-healing system initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize self-healing: {e}")
    
    def monitor_health(self):
        """Perform health monitoring"""
        if not self.self_healing:
            self.initialize_self_healing()
            if not self.self_healing:
                return
        
        try:
            health_status = self.self_healing.monitor_system_health()
            self.health_history.append({
                'timestamp': datetime.now().isoformat(),
                'status': health_status
            })
            
            # Keep only last 100 records
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
            # Log health status
            if health_status['overall_health'] != 'healthy':
                self.logger.warning(f"System health degraded: {health_status['issues']}")
            else:
                self.logger.info("System health: ✅ Healthy")
                
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health monitoring failed: {e}")
            return None
    
    def generate_health_report(self) -> dict:
        """Generate health report"""
        if not self.health_history:
            return {'error': 'No health data available'}
        
        recent_status = self.health_history[-1]['status']
        healthy_percentage = self._calculate_health_percentage()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'current_health': recent_status['overall_health'],
            'health_trend': self._calculate_health_trend(),
            'healthy_percentage': healthy_percentage,
            'recent_issues': recent_status.get('issues', []),
            'component_status': recent_status.get('components', {}),
            'recommendations': self._generate_monitoring_recommendations()
        }
        
        return report
    
    def _calculate_health_percentage(self) -> float:
        """Calculate percentage of time system was healthy"""
        if not self.health_history:
            return 0.0
        
        healthy_count = sum(1 for record in self.health_history 
                          if record['status']['overall_health'] == 'healthy')
        
        return healthy_count / len(self.health_history)
    
    def _calculate_health_trend(self) -> str:
        """Calculate health trend (improving/stable/degrading)"""
        if len(self.health_history) < 2:
            return 'unknown'
        
        # Check last 5 records
        recent = self.health_history[-5:]
        health_scores = []
        
        for record in recent:
            status = record['status']['overall_health']
            score = 1 if status == 'healthy' else 0.5 if status == 'degraded' else 0
            health_scores.append(score)
        
        if len(health_scores) < 2:
            return 'stable'
        
        # Simple trend calculation
        first_half = health_scores[:len(health_scores)//2]
        second_half = health_scores[len(health_scores)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        if avg_second > avg_first + 0.1:
            return 'improving'
        elif avg_second < avg_first - 0.1:
            return 'degrading'
        else:
            return 'stable'
    
    def _generate_monitoring_recommendations(self) -> list:
        """Generate recommendations based on monitoring data"""
        recommendations = []
        
        if self._calculate_health_percentage() < 0.8:
            recommendations.append("System reliability below 80%, consider maintenance")
        
        # Check for frequent component issues
        component_issues = {}
        for record in self.health_history[-10:]:  # Last 10 records
            for issue in record['status'].get('issues', []):
                component = issue.split(':')[0]
                component_issues[component] = component_issues.get(component, 0) + 1
        
        for component, count in component_issues.items():
            if count >= 5:  # Appears in 50%+ of recent checks
                recommendations.append(f"Frequent issues with {component}, investigate root cause")
        
        return recommendations
    
    def start_continuous_monitoring(self, interval_minutes: int = 5):
        """Start continuous monitoring"""
        self.logger.info(f"Starting continuous monitoring (interval: {interval_minutes} minutes)")
        
        schedule.every(interval_minutes).minutes.do(self.monitor_health)
        
        # Also schedule daily report generation
        schedule.every().day.at("08:00").do(self.generate_daily_report)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
    
    def generate_daily_report(self):
        """Generate daily health report"""
        report = self.generate_health_report()
        
        report_file = f"reports/daily_health_{datetime.now().strftime('%Y%m%d')}.json"
        
        os.makedirs('reports', exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Daily report generated: {report_file}")
        
        # Send alert if health is poor
        if report['current_health'] != 'healthy':
            self._send_health_alert(report)
    
    def _send_health_alert(self, report: dict):
        """Send health alert (placeholder for notification system)"""
        message = f"🚨 System Health Alert: {report['current_health']}"
        if report.get('recent_issues'):
            message += f"\nIssues: {', '.join(report['recent_issues'])}"
        
        self.logger.warning(f"HEALTH ALERT: {message}")
        # In production, this would send email/SMS/notification

def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='System Monitor for Phone Unlock AI')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in minutes')
    parser.add_argument('--report', action='store_true', help='Generate health report')
    
    args = parser.parse_args()
    
    monitor = SystemMonitor()
    
    if args.report:
        report = monitor.generate_health_report()
        print("System Health Report:")
        print(json.dumps(report, indent=2))
    
    if args.continuous:
        monitor.start_continuous_monitoring(args.interval)
    
    if not args.continuous and not args.report:
        # Single health check
        health = monitor.monitor_health()
        if health:
            print(f"Current Health: {health['overall_health']}")
            if health['issues']:
                print(f"Issues: {health['issues']}")

if __name__ == "__main__":
    main()
