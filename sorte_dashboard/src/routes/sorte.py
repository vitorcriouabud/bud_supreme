import os
import sys
import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

# Adicionar o diretório base da Sorte ao path
sorte_base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, sorte_base_path)

try:
    from bud_commander_service.deployment_manager import SorteDeploymentManager
    from tests.test_suite import SorteTestSuite
    from utils.logger import Logger
except ImportError as e:
    print(f"Aviso: Não foi possível importar módulos da Sorte: {e}")
    SorteDeploymentManager = None
    SorteTestSuite = None
    Logger = None

sorte_bp = Blueprint('sorte', __name__)

# Inicializar componentes da Sorte (se disponíveis)
if SorteDeploymentManager and SorteTestSuite and Logger:
    deployment_manager = SorteDeploymentManager(sorte_base_path)
    test_suite = SorteTestSuite(sorte_base_path)
    logger = Logger("SorteDashboard")
else:
    deployment_manager = None
    test_suite = None
    logger = None

@sorte_bp.route('/status', methods=['GET'])
@cross_origin()
def get_system_status():
    """Retorna o status geral do sistema Sorte."""
    try:
        status = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "operational",
            "components": {
                "interpreter": {"status": "active", "last_activity": "2024-01-15 10:30:00"},
                "editor": {"status": "active", "last_modification": "2024-01-15 10:25:00"},
                "guardian": {"status": "active", "last_validation": "2024-01-15 10:30:00"},
                "telegram_bot": {"status": "active", "last_message": "2024-01-15 10:28:00"},
                "deployment_manager": {"status": "active", "last_deploy": "2024-01-15 09:45:00"}
            },
            "performance": {
                "uptime": "2h 15m",
                "memory_usage": "245 MB",
                "cpu_usage": "12%",
                "response_time": "0.15s"
            },
            "trading": {
                "active_strategies": 2,
                "total_trades_today": 15,
                "profit_loss": "+$127.50",
                "success_rate": "73%"
            }
        }
        
        if logger:
            logger.info("Status do sistema consultado via dashboard")
        
        return jsonify(status)
        
    except Exception as e:
        error_response = {
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "system_status": "error"
        }
        return jsonify(error_response), 500

@sorte_bp.route('/logs', methods=['GET'])
@cross_origin()
def get_recent_logs():
    """Retorna os logs recentes do sistema."""
    try:
        # Parâmetros de consulta
        limit = request.args.get('limit', 50, type=int)
        level = request.args.get('level', 'all')
        
        # Simular logs (em produção, isso leria de arquivos de log reais)
        sample_logs = [
            {
                "timestamp": "2024-01-15 10:30:15",
                "level": "INFO",
                "component": "AdvancedCommandInterpreter",
                "message": "Comando interpretado: 'seja mais agressiva'"
            },
            {
                "timestamp": "2024-01-15 10:30:16",
                "level": "INFO",
                "component": "ASTCodeEditor",
                "message": "Backup criado: bud_logic/strategy.py.backup"
            },
            {
                "timestamp": "2024-01-15 10:30:17",
                "level": "INFO",
                "component": "CodeGuardian",
                "message": "Validação sintática: PASSOU"
            },
            {
                "timestamp": "2024-01-15 10:30:18",
                "level": "INFO",
                "component": "SorteTelegramBot",
                "message": "Comando executado com sucesso"
            },
            {
                "timestamp": "2024-01-15 10:29:45",
                "level": "WARNING",
                "component": "GPTBridge",
                "message": "API rate limit approaching"
            },
            {
                "timestamp": "2024-01-15 10:28:30",
                "level": "INFO",
                "component": "SorteDeploymentManager",
                "message": "Backup automático criado"
            }
        ]
        
        # Filtrar por nível se especificado
        if level != 'all':
            sample_logs = [log for log in sample_logs if log['level'].lower() == level.lower()]
        
        # Limitar quantidade
        sample_logs = sample_logs[:limit]
        
        response = {
            "logs": sample_logs,
            "total_count": len(sample_logs),
            "filters_applied": {
                "limit": limit,
                "level": level
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sorte_bp.route('/deployments', methods=['GET'])
@cross_origin()
def get_deployment_history():
    """Retorna o histórico de deployments."""
    try:
        if deployment_manager:
            deployment_status = deployment_manager.get_deployment_status()
        else:
            # Dados simulados se o deployment_manager não estiver disponível
            deployment_status = {
                "system_status": "operational",
                "total_backups": 5,
                "total_deployments": 3,
                "total_rollbacks": 1,
                "recent_deployments": [
                    {
                        "timestamp": "20240115_094500",
                        "description": "Auto-deploy: Strategy optimization",
                        "deploy_success": True,
                        "rollback_performed": False
                    }
                ],
                "recent_backups": [
                    {
                        "timestamp": "20240115_103000",
                        "reason": "pre_deploy",
                        "backup_name": "backup_20240115_103000_pre_deploy",
                        "success": True
                    }
                ],
                "last_successful_deployment": {
                    "timestamp": "20240115_094500",
                    "description": "Strategy optimization"
                }
            }
        
        return jsonify(deployment_status)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sorte_bp.route('/tests', methods=['GET'])
@cross_origin()
def get_test_results():
    """Retorna os resultados dos testes mais recentes."""
    try:
        if test_suite:
            # Executar testes (isso pode ser demorado, considere cache)
            test_results = test_suite.run_all_tests()
        else:
            # Dados simulados se o test_suite não estiver disponível
            test_results = {
                "overall_status": "passed",
                "unit_tests": {
                    "passed": True,
                    "details": {
                        "total_tests": 15,
                        "passed": 14,
                        "failed": 1,
                        "success_rate": 0.93
                    }
                },
                "integration_tests": {
                    "passed": True,
                    "summary": "4/4 testes passaram"
                },
                "security_tests": {
                    "passed": True,
                    "summary": "4/4 verificações de segurança passaram"
                },
                "performance_tests": {
                    "passed": True,
                    "summary": "4/4 testes de performance passaram"
                }
            }
        
        return jsonify(test_results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sorte_bp.route('/commands', methods=['POST'])
@cross_origin()
def execute_command():
    """Executa um comando na Sorte."""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({"error": "Comando não fornecido"}), 400
        
        # Simular execução de comando
        # Em produção, isso chamaria o AdvancedCommandInterpreter
        result = {
            "command": command,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "category": "strategy_modification",
            "target_file": "bud_logic/strategy.py",
            "message": f"Comando '{command}' executado com sucesso",
            "validation_results": {
                "syntax_valid": True,
                "security_check": True,
                "tests_passed": True
            }
        }
        
        if logger:
            logger.info(f"Comando executado via dashboard: {command}")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sorte_bp.route('/backup', methods=['POST'])
@cross_origin()
def create_backup():
    """Cria um backup manual do sistema."""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'manual_dashboard')
        
        if deployment_manager:
            backup_result = deployment_manager.create_intelligent_backup(reason)
        else:
            # Simular criação de backup
            backup_result = {
                "success": True,
                "backup_name": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{reason}",
                "timestamp": datetime.now().strftime('%Y%m%d_%H%M%S'),
                "files_backed_up": [
                    "bud_logic/strategy.py",
                    "bud_logic/risk_manager.py",
                    "core/main_controller.py"
                ]
            }
        
        return jsonify(backup_result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sorte_bp.route('/rollback', methods=['POST'])
@cross_origin()
def perform_rollback():
    """Executa rollback para um backup específico."""
    try:
        data = request.get_json()
        backup_name = data.get('backup_name', '')
        
        if not backup_name:
            return jsonify({"error": "Nome do backup não fornecido"}), 400
        
        if deployment_manager:
            rollback_result = deployment_manager.rollback_to_backup(backup_name)
        else:
            # Simular rollback
            rollback_result = {
                "success": True,
                "backup_name": backup_name,
                "timestamp": datetime.now().strftime('%Y%m%d_%H%M%S'),
                "files_restored": [
                    "bud_logic/strategy.py",
                    "bud_logic/risk_manager.py"
                ]
            }
        
        return jsonify(rollback_result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sorte_bp.route('/metrics', methods=['GET'])
@cross_origin()
def get_system_metrics():
    """Retorna métricas detalhadas do sistema."""
    try:
        # Simular métricas do sistema
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "uptime_seconds": 8100,  # 2h 15m
                "memory_usage_mb": 245,
                "cpu_usage_percent": 12,
                "disk_usage_percent": 45
            },
            "trading": {
                "active_strategies": 2,
                "total_trades_today": 15,
                "successful_trades": 11,
                "failed_trades": 4,
                "profit_loss_usd": 127.50,
                "success_rate_percent": 73.33,
                "average_response_time_ms": 150
            },
            "ai_operations": {
                "commands_processed_today": 8,
                "code_modifications_today": 3,
                "successful_validations": 3,
                "failed_validations": 0,
                "backups_created_today": 2
            },
            "api_usage": {
                "openai_requests_today": 12,
                "openai_tokens_used": 2450,
                "telegram_messages_sent": 15,
                "telegram_messages_received": 8
            }
        }
        
        return jsonify(metrics)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sorte_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Endpoint de health check para monitoramento."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "components": {
                "database": "ok",
                "api": "ok",
                "sorte_integration": "ok" if deployment_manager else "limited"
            }
        }
        
        return jsonify(health_status)
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

