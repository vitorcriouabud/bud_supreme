import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from telegram import Bot
from telegram.error import TelegramError
from utils.logger import Logger

class SorteAlertSystem:
    """
    Sistema de alertas inteligente da Sorte para Telegram.
    Envia notificações preventivas e alertas críticos.
    """
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.logger = Logger("SorteAlertSystem")
        
        # Configurações do Telegram
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not self.bot_token or not self.chat_id:
            self.logger.warning("Token do bot ou chat ID não configurados")
            self.bot = None
        else:
            self.bot = Bot(token=self.bot_token)
        
        # Configurações de alertas
        self.alert_cooldown = {}  # Para evitar spam de alertas
        self.cooldown_minutes = 5  # Tempo mínimo entre alertas do mesmo tipo
        
        # Tipos de alertas e suas configurações
        self.alert_types = {
            'critical_error': {
                'emoji': '🚨',
                'priority': 'high',
                'cooldown': 1  # 1 minuto para erros críticos
            },
            'deployment_success': {
                'emoji': '✅',
                'priority': 'medium',
                'cooldown': 5
            },
            'deployment_failure': {
                'emoji': '❌',
                'priority': 'high',
                'cooldown': 2
            },
            'trading_profit': {
                'emoji': '💰',
                'priority': 'medium',
                'cooldown': 10
            },
            'trading_loss': {
                'emoji': '📉',
                'priority': 'medium',
                'cooldown': 5
            },
            'system_warning': {
                'emoji': '⚠️',
                'priority': 'low',
                'cooldown': 10
            },
            'command_executed': {
                'emoji': '🎯',
                'priority': 'low',
                'cooldown': 2
            },
            'backup_created': {
                'emoji': '💾',
                'priority': 'low',
                'cooldown': 15
            },
            'test_failure': {
                'emoji': '🧪',
                'priority': 'medium',
                'cooldown': 5
            },
            'api_quota_warning': {
                'emoji': '⏰',
                'priority': 'medium',
                'cooldown': 30
            }
        }
    
    async def send_alert(self, alert_type: str, message: str, 
                        additional_data: Optional[Dict] = None) -> bool:
        """
        Envia um alerta via Telegram com controle de cooldown.
        """
        if not self.bot:
            self.logger.warning("Bot do Telegram não configurado")
            return False
        
        # Verificar cooldown
        if not self._check_cooldown(alert_type):
            self.logger.info(f"Alerta {alert_type} em cooldown, não enviado")
            return False
        
        try:
            alert_config = self.alert_types.get(alert_type, {
                'emoji': '📢',
                'priority': 'medium',
                'cooldown': 5
            })
            
            # Formatar mensagem
            formatted_message = self._format_alert_message(
                alert_type, message, alert_config, additional_data
            )
            
            # Enviar mensagem
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=formatted_message,
                parse_mode='HTML'
            )
            
            # Atualizar cooldown
            self._update_cooldown(alert_type, alert_config['cooldown'])
            
            self.logger.info(f"Alerta enviado: {alert_type}")
            return True
            
        except TelegramError as e:
            self.logger.error(f"Erro ao enviar alerta via Telegram: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro inesperado ao enviar alerta: {e}")
            return False
    
    def send_alert_sync(self, alert_type: str, message: str, 
                       additional_data: Optional[Dict] = None) -> bool:
        """
        Versão síncrona do send_alert para compatibilidade.
        """
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                self.send_alert(alert_type, message, additional_data)
            )
        except RuntimeError:
            # Se não há loop em execução, criar um novo
            return asyncio.run(
                self.send_alert(alert_type, message, additional_data)
            )
    
    def _format_alert_message(self, alert_type: str, message: str, 
                             alert_config: Dict, additional_data: Optional[Dict]) -> str:
        """
        Formata a mensagem do alerta com informações contextuais.
        """
        emoji = alert_config.get('emoji', '📢')
        priority = alert_config.get('priority', 'medium')
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Cabeçalho do alerta
        header = f"{emoji} <b>SORTE AI - {alert_type.upper()}</b> {emoji}"
        
        # Prioridade
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(priority, '🟡')
        
        # Corpo da mensagem
        body = f"""
{header}

{priority_emoji} <b>Prioridade:</b> {priority.upper()}
🕐 <b>Horário:</b> {timestamp}

📝 <b>Mensagem:</b>
{message}
"""
        
        # Adicionar dados extras se fornecidos
        if additional_data:
            body += "\n📊 <b>Dados Adicionais:</b>\n"
            for key, value in additional_data.items():
                body += f"• <b>{key}:</b> {value}\n"
        
        # Rodapé
        body += f"\n🤖 <i>Sistema Sorte AI - {datetime.now().strftime('%d/%m/%Y')}</i>"
        
        return body
    
    def _check_cooldown(self, alert_type: str) -> bool:
        """
        Verifica se o alerta pode ser enviado (não está em cooldown).
        """
        if alert_type not in self.alert_cooldown:
            return True
        
        last_sent = self.alert_cooldown[alert_type]
        cooldown_minutes = self.alert_types.get(alert_type, {}).get('cooldown', 5)
        
        time_diff = datetime.now() - last_sent
        return time_diff.total_seconds() >= (cooldown_minutes * 60)
    
    def _update_cooldown(self, alert_type: str, cooldown_minutes: int):
        """
        Atualiza o timestamp do último alerta enviado.
        """
        self.alert_cooldown[alert_type] = datetime.now()
    
    # Métodos de conveniência para tipos específicos de alertas
    
    def alert_critical_error(self, error_message: str, component: str = "Unknown"):
        """Alerta para erros críticos do sistema."""
        return self.send_alert_sync(
            'critical_error',
            f"Erro crítico detectado no componente {component}: {error_message}",
            {'component': component, 'severity': 'CRITICAL'}
        )
    
    def alert_deployment_success(self, deployment_info: Dict):
        """Alerta para deploy bem-sucedido."""
        return self.send_alert_sync(
            'deployment_success',
            f"Deploy executado com sucesso: {deployment_info.get('description', 'N/A')}",
            {
                'timestamp': deployment_info.get('timestamp', 'N/A'),
                'files_modified': len(deployment_info.get('files_modified', [])),
                'tests_passed': deployment_info.get('tests_passed', 'N/A')
            }
        )
    
    def alert_deployment_failure(self, deployment_info: Dict):
        """Alerta para falha no deploy."""
        return self.send_alert_sync(
            'deployment_failure',
            f"Falha no deploy: {deployment_info.get('error', 'Erro desconhecido')}",
            {
                'timestamp': deployment_info.get('timestamp', 'N/A'),
                'rollback_performed': deployment_info.get('rollback_performed', False),
                'backup_available': deployment_info.get('pre_deploy_backup', {}).get('success', False)
            }
        )
    
    def alert_trading_profit(self, profit_amount: float, trade_details: Dict):
        """Alerta para lucro significativo."""
        return self.send_alert_sync(
            'trading_profit',
            f"Lucro realizado: ${profit_amount:.2f}",
            {
                'strategy': trade_details.get('strategy', 'N/A'),
                'symbol': trade_details.get('symbol', 'N/A'),
                'duration': trade_details.get('duration', 'N/A'),
                'success_rate_today': trade_details.get('success_rate_today', 'N/A')
            }
        )
    
    def alert_trading_loss(self, loss_amount: float, trade_details: Dict):
        """Alerta para perda significativa."""
        return self.send_alert_sync(
            'trading_loss',
            f"Perda registrada: ${abs(loss_amount):.2f}",
            {
                'strategy': trade_details.get('strategy', 'N/A'),
                'symbol': trade_details.get('symbol', 'N/A'),
                'risk_level': trade_details.get('risk_level', 'N/A'),
                'stop_loss_triggered': trade_details.get('stop_loss_triggered', False)
            }
        )
    
    def alert_system_warning(self, warning_message: str, component: str = "System"):
        """Alerta para avisos do sistema."""
        return self.send_alert_sync(
            'system_warning',
            f"Aviso do sistema ({component}): {warning_message}",
            {'component': component, 'severity': 'WARNING'}
        )
    
    def alert_command_executed(self, command: str, result: Dict):
        """Alerta para comando executado com sucesso."""
        return self.send_alert_sync(
            'command_executed',
            f"Comando executado: '{command}'",
            {
                'category': result.get('category', 'N/A'),
                'target_file': result.get('target_file', 'N/A'),
                'validation_passed': result.get('validation_results', {}).get('syntax_valid', False),
                'tests_passed': result.get('validation_results', {}).get('tests_passed', False)
            }
        )
    
    def alert_backup_created(self, backup_info: Dict):
        """Alerta para backup criado."""
        return self.send_alert_sync(
            'backup_created',
            f"Backup criado: {backup_info.get('backup_name', 'N/A')}",
            {
                'reason': backup_info.get('reason', 'N/A'),
                'files_backed_up': len(backup_info.get('files_backed_up', [])),
                'size': backup_info.get('size', 'N/A')
            }
        )
    
    def alert_test_failure(self, test_results: Dict):
        """Alerta para falha nos testes."""
        failed_tests = []
        for test_type, result in test_results.items():
            if isinstance(result, dict) and not result.get('passed', True):
                failed_tests.append(test_type)
        
        return self.send_alert_sync(
            'test_failure',
            f"Falha nos testes: {', '.join(failed_tests)}",
            {
                'total_failed': len(failed_tests),
                'test_types': ', '.join(failed_tests),
                'overall_status': test_results.get('overall_status', 'N/A')
            }
        )
    
    def alert_api_quota_warning(self, api_name: str, usage_percent: float):
        """Alerta para cota de API próxima do limite."""
        return self.send_alert_sync(
            'api_quota_warning',
            f"Cota da API {api_name} em {usage_percent:.1f}%",
            {
                'api_name': api_name,
                'usage_percent': f"{usage_percent:.1f}%",
                'recommendation': 'Considere reduzir o uso ou aumentar a cota'
            }
        )
    
    def send_daily_summary(self, summary_data: Dict):
        """Envia resumo diário das atividades."""
        try:
            message = f"""
📊 <b>RESUMO DIÁRIO - SORTE AI</b> 📊

🤖 <b>Atividade da IA:</b>
• Comandos processados: {summary_data.get('commands_processed', 0)}
• Modificações de código: {summary_data.get('code_modifications', 0)}
• Backups criados: {summary_data.get('backups_created', 0)}
• Deploys realizados: {summary_data.get('deployments', 0)}

💰 <b>Trading:</b>
• Total de trades: {summary_data.get('total_trades', 0)}
• Taxa de sucesso: {summary_data.get('success_rate', 0):.1f}%
• P&L do dia: ${summary_data.get('daily_pnl', 0):.2f}
• Melhor trade: ${summary_data.get('best_trade', 0):.2f}

🔧 <b>Sistema:</b>
• Uptime: {summary_data.get('uptime_hours', 0):.1f}h
• Testes executados: {summary_data.get('tests_run', 0)}
• Alertas enviados: {summary_data.get('alerts_sent', 0)}

🎯 <b>Próximas 24h:</b>
• Estratégias ativas: {summary_data.get('active_strategies', 0)}
• Backups programados: {summary_data.get('scheduled_backups', 0)}
• Manutenções previstas: {summary_data.get('scheduled_maintenance', 0)}

🤖 <i>Relatório gerado automaticamente pela Sorte AI</i>
"""
            
            return self.send_alert_sync('daily_summary', message)
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar resumo diário: {e}")
            return False
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos alertas enviados."""
        try:
            stats = {
                'total_alert_types': len(self.alert_types),
                'alerts_in_cooldown': len(self.alert_cooldown),
                'cooldown_status': {},
                'next_available': {}
            }
            
            for alert_type, last_sent in self.alert_cooldown.items():
                cooldown_minutes = self.alert_types.get(alert_type, {}).get('cooldown', 5)
                time_since_last = datetime.now() - last_sent
                time_remaining = (cooldown_minutes * 60) - time_since_last.total_seconds()
                
                stats['cooldown_status'][alert_type] = time_remaining <= 0
                if time_remaining > 0:
                    stats['next_available'][alert_type] = f"{int(time_remaining // 60)}m {int(time_remaining % 60)}s"
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de alertas: {e}")
            return {'error': str(e)}

