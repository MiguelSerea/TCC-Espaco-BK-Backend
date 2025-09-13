import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import logging
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDB:
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.connect()
    
    def connect(self):
        """Conecta ao MongoDB Atlas"""
        try:
            # Usar a string de conexão completa do .env
            connection_string = os.getenv('DB_HOST')
            database_name = os.getenv('MONGO_DATABASE', 'Espaco_BK')
            
            if not connection_string:
                raise ValueError("DB_HOST não encontrado no arquivo .env")
            
            logger.info(f"🔗 Conectando ao MongoDB Atlas...")
            logger.info(f"🎯 Database: {database_name}")
            
            # Conectar com configurações otimizadas para Atlas
            self._client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=20000,
                maxPoolSize=50,
                retryWrites=True
            )
            
            # Testar conexão
            self._client.admin.command('ping')
            
            # Definir database
            self._db = self._client[database_name]
            
            logger.info(f"✅ Conectado ao MongoDB Atlas: {database_name}")
            
            # Listar collections para confirmar
            collections = self._db.list_collection_names()
            logger.info(f"📋 Collections encontradas: {collections}")
            
            # Mostrar contadores
            for collection_name in collections:
                try:
                    count = self._db[collection_name].count_documents({})
                    logger.info(f"   📊 {collection_name}: {count} documentos")
                except:
                    pass
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar MongoDB Atlas: {e}")
            raise
    
    @property
    def db(self):
        """Retorna a instância do banco de dados"""
        if self._db is None:
            self.connect()
        return self._db
    
    def get_collection(self, name):
        """Retorna uma collection específica"""
        return self.db[name]
    
    def list_collections(self):
        """Lista todas as collections"""
        return self.db.list_collection_names()
    
    def close(self):
        """Fecha a conexão"""
        if self._client:
            self._client.close()

# Instância global
mongodb = MongoDB()

class UsuarioService:
    def __init__(self):
        # Collection correta: Usuario (como mostrado no Compass)
        self.collection = mongodb.get_collection('Usuario')
    
    def find_all(self, limit=None):
        """Busca todos os usuários"""
        try:
            cursor = self.collection.find({})
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Erro ao buscar usuários: {e}")
            return []
    
    def find_by_id(self, user_id):
        """Busca usuário por ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(user_id)})
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID: {e}")
            return None
    
    def find_by_email(self, email):
        """Busca usuário por email"""
        try:
            return self.collection.find_one({'email': email})
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por email: {e}")
            return None
    
    def create(self, user_data):
        """Cria um novo usuário"""
        try:
            user_data['created_at'] = datetime.now()
            user_data['updated_at'] = datetime.now()
            
            result = self.collection.insert_one(user_data)
            logger.info(f"✅ Usuário criado: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return None
    
    def update(self, user_id, update_data):
        """Atualiza um usuário"""
        try:
            update_data['updated_at'] = datetime.now()
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)}, 
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erro ao atualizar usuário: {e}")
            return False
    
    def delete(self, user_id):
        """Remove um usuário"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erro ao deletar usuário: {e}")
            return False
    
    def count(self):
        """Conta total de usuários"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Erro ao contar usuários: {e}")
            return 0
    
    def authenticate(self, email, senha):
        """Autentica um usuário"""
        try:
            user = self.find_by_email(email)
            if user and user.get('senha') == senha:
                logger.info(f"✅ Usuário autenticado: {email}")
                return user
            logger.warning(f"❌ Falha na autenticação: {email}")
            return None
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return None

class TarefaService:
    def __init__(self):
        # Collection correta: Tarefa
        self.collection = mongodb.get_collection('Tarefa')
    
    def find_all(self, limit=None):
        """Busca todas as tarefas"""
        try:
            cursor = self.collection.find({})
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Erro ao buscar tarefas: {e}")
            return []
    
    def find_by_user(self, user_id):
        """Busca tarefas por usuário"""
        try:
            # Tentar diferentes formatos de ID
            queries = [
                {'idUsuario': ObjectId(user_id)},
                {'idUsuario': user_id},
                {'usuario_id': ObjectId(user_id)},
                {'usuario_id': user_id}
            ]
            
            for query in queries:
                try:
                    result = list(self.collection.find(query))
                    if result:
                        return result
                except:
                    continue
            
            return []
        except Exception as e:
            logger.error(f"Erro ao buscar tarefas por usuário: {e}")
            return []
    
    def find_by_id(self, task_id):
        """Busca tarefa por ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(task_id)})
        except Exception as e:
            logger.error(f"Erro ao buscar tarefa por ID: {e}")
            return None
    
    def create(self, task_data):
        """Cria uma nova tarefa"""
        try:
            task_data['created_at'] = datetime.now()
            task_data['updated_at'] = datetime.now()
            
            # Converter datas se necessário
            for field in ['data_inicio', 'data_termino']:
                if field in task_data and isinstance(task_data[field], str):
                    try:
                        task_data[field] = datetime.fromisoformat(task_data[field].replace('Z', '+00:00'))
                    except:
                        pass
            
            result = self.collection.insert_one(task_data)
            logger.info(f"✅ Tarefa criada: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Erro ao criar tarefa: {e}")
            return None
    
    def update(self, task_id, update_data):
        """Atualiza uma tarefa"""
        try:
            update_data['updated_at'] = datetime.now()
            result = self.collection.update_one(
                {'_id': ObjectId(task_id)}, 
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erro ao atualizar tarefa: {e}")
            return False
    
    def delete(self, task_id):
        """Remove uma tarefa"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(task_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erro ao deletar tarefa: {e}")
            return False
    
    def count(self):
        """Conta total de tarefas"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Erro ao contar tarefas: {e}")
            return 0

class ClienteService:
    def __init__(self):
        # Collection correta: Cliente
        self.collection = mongodb.get_collection('Cliente')
    
    def find_all(self, limit=None):
        """Busca todos os clientes"""
        try:
            cursor = self.collection.find({})
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
            return []
    
    def find_by_id(self, client_id):
        """Busca cliente por ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(client_id)})
        except Exception as e:
            logger.error(f"Erro ao buscar cliente por ID: {e}")
            return None
    
    def search(self, query):
        """Busca clientes por nome, cidade, etc."""
        try:
            regex_query = {'$regex': query, '$options': 'i'}
            search_filter = {
                '$or': [
                    {'nome': regex_query},
                    {'cidade': regex_query},
                    {'razao_social': regex_query}
                ]
            }
            return list(self.collection.find(search_filter))
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
            return []
    
    def create(self, client_data):
        """Cria um novo cliente"""
        try:
            client_data['created_at'] = datetime.now()
            client_data['updated_at'] = datetime.now()
            
            result = self.collection.insert_one(client_data)
            logger.info(f"✅ Cliente criado: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Erro ao criar cliente: {e}")
            return None
    
    def update(self, client_id, update_data):
        """Atualiza um cliente"""
        try:
            update_data['updated_at'] = datetime.now()
            result = self.collection.update_one(
                {'_id': ObjectId(client_id)}, 
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erro ao atualizar cliente: {e}")
            return False
    
    def delete(self, client_id):
        """Remove um cliente"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(client_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erro ao deletar cliente: {e}")
            return False
    
    def count(self):
        """Conta total de clientes"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Erro ao contar clientes: {e}")
            return 0

class CampanhaService:
    def __init__(self):
        # Collection: Campanha
        self.collection = mongodb.get_collection('Campanha')
    
    def find_all(self, limit=None):
        """Busca todas as campanhas"""
        try:
            cursor = self.collection.find({})
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Erro ao buscar campanhas: {e}")
            return []
    
    def find_by_id(self, campaign_id):
        """Busca campanha por ID"""
        try:
            return self.collection.find_one({'_id': ObjectId(campaign_id)})
        except Exception as e:
            logger.error(f"Erro ao buscar campanha por ID: {e}")
            return None
    
    def count(self):
        """Conta total de campanhas"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Erro ao contar campanhas: {e}")
            return 0

# Instâncias dos serviços
usuario_service = UsuarioService()
tarefa_service = TarefaService()
cliente_service = ClienteService()
campanha_service = CampanhaService()