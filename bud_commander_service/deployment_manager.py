import os
import shutil
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import git
from utils.logger import Logger

class SorteDeploymentManager:
    """
    Gerenciador de deploy contínuo para a IA Sorte.
    Inclui backup inteligente, rollback automático e validação pré-deploy.
    """
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.logger = Logger("SorteDeploymentManager")
        
        # Configurações de deploy
        self.backup_dir = os.path.join(base_path, "backups")
        self.deploy_history_file = os.path.join(base_path, "deploy_history.json")
        self.max_backups = 10  # Manter apenas os 10 backups mais recentes
        
        # Inicializar diretórios
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Inicializar histórico de deploy
        self.deploy_history = self._load_deploy_history()
        
        # Arquivos críticos para backup
        self.critical_files = [
            "bud_logic/strategy.py",
            "bud_logic/risk_manager.py",
            "core/main_controller.py",
            "bud_interpreter_service/advanced_interpreter.py",
            "bud_editor_service/ast_editor.py",
            "bud_guardian_service/guardian.py",
            "telegram_integration/sorte_telegram_bot.py",
            "config.yaml",
            "requirements.txt"
        ]
    
    def create_intelligent_backup(self, backup_reason: str = "manual") -> Dict[str, Any]:
        """
        Cria um backup inteligente do sistema atual.
        """
        self.logger.info(f"Iniciando backup inteligente. Razão: {backup_reason}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}_{backup_reason}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            os.makedirs(backup_path, exist_ok=True)
            
            backup_info = {
                "timestamp": timestamp,
                "reason": backup_reason,
                "backup_name": backup_name,
                "backup_path": backup_path,
                "files_backed_up": [],
                "git_commit": self._get_current_git_commit(),
                "system_state": self._capture_system_state(),
                "success": False
            }
            
            # Backup dos arquivos críticos
            for file_path in self.critical_files:
                source_path = os.path.join(self.base_path, file_path)
                if os.path.exists(source_path):
                    # Criar estrutura de diretórios no backup
                    backup_file_path = os.path.join(backup_path, file_path)
                    os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
                    
                    # Copiar arquivo
                    shutil.copy2(source_path, backup_file_path)
                    backup_info["files_backed_up"].append(file_path)
                    self.logger.info(f"Arquivo copiado para backup: {file_path}")
            
            # Salvar informações do backup
            backup_info_file = os.path.join(backup_path, "backup_info.json")
            with open(backup_info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            backup_info["success"] = True
            
            # Adicionar ao histórico
            self.deploy_history["backups"].append(backup_info)
            self._save_deploy_history()
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            self.logger.info(f"Backup criado com sucesso: {backup_name}")
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            backup_info["success"] = False
            backup_info["error"] = str(e)
            return backup_info
    
    def deploy_with_validation(self, changes_description: str = "Auto-deploy") -> Dict[str, Any]:
        """
        Executa deploy com validação completa e rollback automático em caso de falha.
        """
        self.logger.info(f"Iniciando deploy com validação: {changes_description}")
        
        deploy_info = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "description": changes_description,
            "pre_deploy_backup": None,
            "validation_results": {},
            "deploy_success": False,
            "rollback_performed": False,
            "error": None
        }
        
        try:
            # 1. Criar backup pré-deploy
            self.logger.info("Criando backup pré-deploy...")
            backup_result = self.create_intelligent_backup("pre_deploy")
            deploy_info["pre_deploy_backup"] = backup_result
            
            if not backup_result["success"]:
                raise Exception("Falha ao criar backup pré-deploy")
            
            # 2. Executar validações pré-deploy
            self.logger.info("Executando validações pré-deploy...")
            validation_results = self._run_pre_deploy_validations()
            deploy_info["validation_results"] = validation_results
            
            if not validation_results["all_passed"]:
                raise Exception(f"Validações pré-deploy falharam: {validation_results['failures']}")
            
            # 3. Executar deploy
            self.logger.info("Executando deploy...")
            deploy_success = self._execute_deploy()
            
            if not deploy_success:
                raise Exception("Falha na execução do deploy")
            
            # 4. Validações pós-deploy
            self.logger.info("Executando validações pós-deploy...")
            post_validation_results = self._run_post_deploy_validations()
            deploy_info["validation_results"]["post_deploy"] = post_validation_results
            
            if not post_validation_results["all_passed"]:
                self.logger.warning("Validações pós-deploy falharam. Iniciando rollback...")
                rollback_result = self.rollback_to_backup(backup_result["backup_name"])
                deploy_info["rollback_performed"] = rollback_result["success"]
                
                if rollback_result["success"]:
                    raise Exception(f"Deploy falhou nas validações pós-deploy. Rollback executado com sucesso.")
                else:
                    raise Exception(f"Deploy falhou e rollback também falhou: {rollback_result['error']}")
            
            # 5. Deploy bem-sucedido
            deploy_info["deploy_success"] = True
            self.logger.info("Deploy executado com sucesso!")
            
            # Adicionar ao histórico
            self.deploy_history["deployments"].append(deploy_info)
            self._save_deploy_history()
            
            return deploy_info
            
        except Exception as e:
            self.logger.error(f"Erro durante deploy: {e}")
            deploy_info["error"] = str(e)
            
            # Se ainda não foi feito rollback, tentar fazer
            if not deploy_info["rollback_performed"] and deploy_info["pre_deploy_backup"]:
                self.logger.info("Tentando rollback devido a erro...")
                rollback_result = self.rollback_to_backup(deploy_info["pre_deploy_backup"]["backup_name"])
                deploy_info["rollback_performed"] = rollback_result["success"]
            
            return deploy_info
    
    def rollback_to_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        Executa rollback para um backup específico.
        """
        self.logger.info(f"Iniciando rollback para backup: {backup_name}")
        
        rollback_info = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "backup_name": backup_name,
            "files_restored": [],
            "success": False,
            "error": None
        }
        
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                raise Exception(f"Backup não encontrado: {backup_name}")
            
            # Carregar informações do backup
            backup_info_file = os.path.join(backup_path, "backup_info.json")
            if os.path.exists(backup_info_file):
                with open(backup_info_file, 'r') as f:
                    backup_info = json.load(f)
                    files_to_restore = backup_info.get("files_backed_up", [])
            else:
                # Fallback: restaurar todos os arquivos críticos
                files_to_restore = self.critical_files
            
            # Restaurar arquivos
            for file_path in files_to_restore:
                backup_file_path = os.path.join(backup_path, file_path)
                target_file_path = os.path.join(self.base_path, file_path)
                
                if os.path.exists(backup_file_path):
                    # Criar diretório de destino se necessário
                    os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
                    
                    # Restaurar arquivo
                    shutil.copy2(backup_file_path, target_file_path)
                    rollback_info["files_restored"].append(file_path)
                    self.logger.info(f"Arquivo restaurado: {file_path}")
            
            rollback_info["success"] = True
            self.logger.info(f"Rollback executado com sucesso para backup: {backup_name}")
            
            # Adicionar ao histórico
            self.deploy_history["rollbacks"].append(rollback_info)
            self._save_deploy_history()
            
            return rollback_info
            
        except Exception as e:
            self.logger.error(f"Erro durante rollback: {e}")
            rollback_info["error"] = str(e)
            return rollback_info
    
    def _run_pre_deploy_validations(self) -> Dict[str, Any]:
        """
        Executa validações antes do deploy.
        """
        validations = {
            "syntax_check": self._validate_python_syntax(),
            "import_check": self._validate_imports(),
            "config_check": self._validate_configuration(),
            "dependencies_check": self._validate_dependencies()
        }
        
        all_passed = all(validation["passed"] for validation in validations.values())
        failures = [name for name, result in validations.items() if not result["passed"]]
        
        return {
            "all_passed": all_passed,
            "failures": failures,
            "details": validations
        }
    
    def _run_post_deploy_validations(self) -> Dict[str, Any]:
        """
        Executa validações após o deploy.
        """
        validations = {
            "service_health": self._check_service_health(),
            "api_endpoints": self._check_api_endpoints(),
            "telegram_bot": self._check_telegram_bot(),
            "file_permissions": self._check_file_permissions()
        }
        
        all_passed = all(validation["passed"] for validation in validations.values())
        failures = [name for name, result in validations.items() if not result["passed"]]
        
        return {
            "all_passed": all_passed,
            "failures": failures,
            "details": validations
        }
    
    def _execute_deploy(self) -> bool:
        """
        Executa o deploy propriamente dito.
        """
        try:
            # Simular deploy (em produção, isso seria restart de serviços, etc.)
            self.logger.info("Executando deploy...")
            
            # Aqui seria implementada a lógica específica de deploy:
            # - Restart de serviços
            # - Atualização de containers Docker
            # - Sincronização de arquivos
            # - Etc.
            
            # Por enquanto, simular sucesso
            time.sleep(2)  # Simular tempo de deploy
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na execução do deploy: {e}")
            return False
    
    def _validate_python_syntax(self) -> Dict[str, Any]:
        """
        Valida a sintaxe de todos os arquivos Python críticos.
        """
        try:
            import ast
            
            syntax_errors = []
            
            for file_path in self.critical_files:
                if file_path.endswith('.py'):
                    full_path = os.path.join(self.base_path, file_path)
                    if os.path.exists(full_path):
                        try:
                            with open(full_path, 'r') as f:
                                content = f.read()
                            ast.parse(content)
                        except SyntaxError as e:
                            syntax_errors.append(f"{file_path}: {e}")
            
            return {
                "passed": len(syntax_errors) == 0,
                "errors": syntax_errors,
                "files_checked": len([f for f in self.critical_files if f.endswith('.py')])
            }
            
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "files_checked": 0
            }
    
    def _validate_imports(self) -> Dict[str, Any]:
        """
        Valida se todas as importações necessárias estão disponíveis.
        """
        try:
            import_errors = []
            
            # Lista de módulos críticos
            critical_modules = [
                'telegram',
                'openai',
                'fastapi',
                'python-telegram-bot',
                'astor',
                'pytest'
            ]
            
            for module in critical_modules:
                try:
                    __import__(module.replace('-', '_'))
                except ImportError:
                    import_errors.append(f"Módulo não encontrado: {module}")
            
            return {
                "passed": len(import_errors) == 0,
                "errors": import_errors,
                "modules_checked": len(critical_modules)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "modules_checked": 0
            }
    
    def _validate_configuration(self) -> Dict[str, Any]:
        """
        Valida se as configurações estão corretas.
        """
        try:
            config_errors = []
            
            # Verificar arquivo .env
            env_file = os.path.join(self.base_path, '.env')
            if not os.path.exists(env_file):
                config_errors.append("Arquivo .env não encontrado")
            
            # Verificar config.yaml
            config_file = os.path.join(self.base_path, 'config.yaml')
            if not os.path.exists(config_file):
                config_errors.append("Arquivo config.yaml não encontrado")
            
            # Verificar variáveis de ambiente críticas
            critical_env_vars = ['TELEGRAM_BOT_TOKEN', 'OPENAI_API_KEY']
            for var in critical_env_vars:
                if not os.getenv(var):
                    config_errors.append(f"Variável de ambiente não configurada: {var}")
            
            return {
                "passed": len(config_errors) == 0,
                "errors": config_errors,
                "checks_performed": 3
            }
            
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "checks_performed": 0
            }
    
    def _validate_dependencies(self) -> Dict[str, Any]:
        """
        Valida se todas as dependências estão instaladas.
        """
        try:
            requirements_file = os.path.join(self.base_path, 'requirements.txt')
            
            if not os.path.exists(requirements_file):
                return {
                    "passed": False,
                    "errors": ["Arquivo requirements.txt não encontrado"],
                    "dependencies_checked": 0
                }
            
            # Executar pip check
            result = subprocess.run(
                ['pip', 'check'],
                capture_output=True,
                text=True,
                cwd=self.base_path
            )
            
            return {
                "passed": result.returncode == 0,
                "errors": [result.stderr] if result.stderr else [],
                "output": result.stdout,
                "dependencies_checked": "all"
            }
            
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "dependencies_checked": 0
            }
    
    def _check_service_health(self) -> Dict[str, Any]:
        """
        Verifica a saúde dos serviços após o deploy.
        """
        try:
            # Simular verificação de saúde dos serviços
            # Em produção, isso verificaria se os serviços estão respondendo
            
            services_status = {
                "main_controller": True,
                "telegram_bot": True,
                "interpreter_service": True,
                "editor_service": True,
                "guardian_service": True
            }
            
            all_healthy = all(services_status.values())
            
            return {
                "passed": all_healthy,
                "services_status": services_status,
                "healthy_services": sum(services_status.values()),
                "total_services": len(services_status)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "services_checked": 0
            }
    
    def _check_api_endpoints(self) -> Dict[str, Any]:
        """
        Verifica se os endpoints da API estão respondendo.
        """
        try:
            # Simular verificação de endpoints
            # Em produção, isso faria requests HTTP para os endpoints
            
            endpoints_status = {
                "/health": True,
                "/status": True,
                "/api/interpret": True
            }
            
            all_responding = all(endpoints_status.values())
            
            return {
                "passed": all_responding,
                "endpoints_status": endpoints_status,
                "responding_endpoints": sum(endpoints_status.values()),
                "total_endpoints": len(endpoints_status)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "endpoints_checked": 0
            }
    
    def _check_telegram_bot(self) -> Dict[str, Any]:
        """
        Verifica se o bot do Telegram está funcionando.
        """
        try:
            # Simular verificação do bot do Telegram
            # Em produção, isso testaria a conexão com a API do Telegram
            
            bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
            
            return {
                "passed": bool(bot_token),
                "token_configured": bool(bot_token),
                "connection_test": "simulated_success"
            }
            
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "token_configured": False
            }
    
    def _check_file_permissions(self) -> Dict[str, Any]:
        """
        Verifica se as permissões dos arquivos estão corretas.
        """
        try:
            permission_errors = []
            
            for file_path in self.critical_files:
                full_path = os.path.join(self.base_path, file_path)
                if os.path.exists(full_path):
                    # Verificar se o arquivo é legível
                    if not os.access(full_path, os.R_OK):
                        permission_errors.append(f"Arquivo não legível: {file_path}")
                    
                    # Verificar se arquivos Python são executáveis (se necessário)
                    if file_path.endswith('.py') and not os.access(full_path, os.X_OK):
                        # Não é necessariamente um erro, mas pode ser um aviso
                        pass
            
            return {
                "passed": len(permission_errors) == 0,
                "errors": permission_errors,
                "files_checked": len(self.critical_files)
            }
            
        except Exception as e:
            return {
                "passed": False,
                "errors": [str(e)],
                "files_checked": 0
            }
    
    def _get_current_git_commit(self) -> Optional[str]:
        """
        Obtém o hash do commit atual do Git.
        """
        try:
            repo = git.Repo(self.base_path)
            return repo.head.commit.hexsha
        except:
            return None
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """
        Captura o estado atual do sistema.
        """
        try:
            import psutil
            
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "timestamp": datetime.now().isoformat()
            }
        except:
            return {
                "timestamp": datetime.now().isoformat(),
                "note": "Sistema de monitoramento não disponível"
            }
    
    def _load_deploy_history(self) -> Dict[str, List]:
        """
        Carrega o histórico de deploys.
        """
        if os.path.exists(self.deploy_history_file):
            try:
                with open(self.deploy_history_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "backups": [],
            "deployments": [],
            "rollbacks": []
        }
    
    def _save_deploy_history(self):
        """
        Salva o histórico de deploys.
        """
        try:
            with open(self.deploy_history_file, 'w') as f:
                json.dump(self.deploy_history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico de deploy: {e}")
    
    def _cleanup_old_backups(self):
        """
        Remove backups antigos, mantendo apenas os mais recentes.
        """
        try:
            backups = self.deploy_history.get("backups", [])
            
            if len(backups) > self.max_backups:
                # Ordenar por timestamp
                backups.sort(key=lambda x: x["timestamp"])
                
                # Remover backups antigos
                backups_to_remove = backups[:-self.max_backups]
                
                for backup in backups_to_remove:
                    backup_path = backup["backup_path"]
                    if os.path.exists(backup_path):
                        shutil.rmtree(backup_path)
                        self.logger.info(f"Backup antigo removido: {backup['backup_name']}")
                
                # Atualizar lista
                self.deploy_history["backups"] = backups[-self.max_backups:]
                
        except Exception as e:
            self.logger.error(f"Erro ao limpar backups antigos: {e}")
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """
        Retorna o status atual do sistema de deploy.
        """
        try:
            recent_backups = self.deploy_history.get("backups", [])[-5:]  # Últimos 5 backups
            recent_deployments = self.deploy_history.get("deployments", [])[-5:]  # Últimos 5 deploys
            recent_rollbacks = self.deploy_history.get("rollbacks", [])[-5:]  # Últimos 5 rollbacks
            
            return {
                "system_status": "operational",
                "total_backups": len(self.deploy_history.get("backups", [])),
                "total_deployments": len(self.deploy_history.get("deployments", [])),
                "total_rollbacks": len(self.deploy_history.get("rollbacks", [])),
                "recent_backups": recent_backups,
                "recent_deployments": recent_deployments,
                "recent_rollbacks": recent_rollbacks,
                "last_successful_deployment": self._get_last_successful_deployment(),
                "backup_directory_size": self._get_backup_directory_size()
            }
            
        except Exception as e:
            return {
                "system_status": "error",
                "error": str(e)
            }
    
    def _get_last_successful_deployment(self) -> Optional[Dict[str, Any]]:
        """
        Retorna informações sobre o último deploy bem-sucedido.
        """
        deployments = self.deploy_history.get("deployments", [])
        
        for deployment in reversed(deployments):
            if deployment.get("deploy_success", False):
                return deployment
        
        return None
    
    def _get_backup_directory_size(self) -> str:
        """
        Calcula o tamanho total do diretório de backups.
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.backup_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            # Converter para MB
            size_mb = total_size / (1024 * 1024)
            return f"{size_mb:.2f} MB"
            
        except:
            return "Desconhecido"

