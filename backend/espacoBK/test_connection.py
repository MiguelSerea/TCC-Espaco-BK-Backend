import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar diretório do projeto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from database import usuario_service, tarefa_service, cliente_service, campanha_service, mongodb
    print("✅ Imports realizados com sucesso!")
except Exception as e:
    print(f"❌ Erro no import: {e}")
    exit(1)

def test_atlas_connection():
    """Teste completo de conexão com MongoDB Atlas"""
    print("🌐 Testando conexão com MongoDB Atlas...")
    print(f"🎯 Database: {os.getenv('MONGO_DATABASE')}")
    
    try:
        # Listar collections
        collections = mongodb.list_collections()
        print(f"✅ Collections encontradas: {collections}")
        
        # Contar documentos
        print(f"\n📊 Contadores:")
        
        usuarios_count = usuario_service.count()
        print(f"   👥 Usuários: {usuarios_count}")
        
        tarefas_count = tarefa_service.count()
        print(f"   📋 Tarefas: {tarefas_count}")
        
        clientes_count = cliente_service.count()
        print(f"   🏢 Clientes: {clientes_count}")
        
        campanhas_count = campanha_service.count()
        print(f"   📢 Campanhas: {campanhas_count}")
        
        total = usuarios_count + tarefas_count + clientes_count + campanhas_count
        print(f"   🎯 Total de documentos: {total}")
        
        return total > 0
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def test_real_data():
    """Testa com dados reais do Atlas"""
    print("\n📋 Testando dados reais...")
    
    try:
        # Usuários
        print(f"\n👥 Usuários:")
        usuarios = usuario_service.find_all(limit=2)
        if usuarios:
            for i, user in enumerate(usuarios, 1):
                nome = user.get('nome', 'N/A')
                email = user.get('email', 'N/A')
                tipo = user.get('tipo', 'N/A')
                print(f"   {i}. {nome} ({email}) - Tipo: {tipo}")
        else:
            print("   Nenhum usuário encontrado")
        
        # Clientes (primeiros 5)
        print(f"\n🏢 Clientes (primeiros 5):")
        clientes = cliente_service.find_all(limit=5)
        if clientes:
            for i, client in enumerate(clientes, 1):
                nome = client.get('nome', 'N/A')
                cidade = client.get('cidade', 'N/A')
                telefone = client.get('telefone', 'N/A')
                print(f"   {i}. {nome} - {cidade} (Tel: {telefone})")
        else:
            print("   Nenhum cliente encontrado")
        
        # Tarefas
        print(f"\n📋 Tarefas:")
        tarefas = tarefa_service.find_all(limit=3)
        if tarefas:
            for i, task in enumerate(tarefas, 1):
                titulo = task.get('titulo', 'N/A')
                status = task.get('status', 'N/A')
                prioridade = task.get('prioridade', 'N/A')
                print(f"   {i}. {titulo} (Status: {status}, Prioridade: {prioridade})")
        else:
            print("   Nenhuma tarefa encontrada")
        
        # Campanhas
        print(f"\n📢 Campanhas:")
        campanhas = campanha_service.find_all(limit=2)
        if campanhas:
            for i, campaign in enumerate(campanhas, 1):
                print(f"   {i}. Campanha ID: {campaign.get('_id')}")
                # Mostrar alguns campos (adaptaremos baseado na estrutura real)
                for key, value in list(campaign.items())[:4]:
                    if key != '_id':
                        value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"      {key}: {value_str}")
        else:
            print("   Nenhuma campanha encontrada")
            
    except Exception as e:
        print(f"❌ Erro ao buscar dados: {e}")

def test_authentication():
    """Testa autenticação com usuário real"""
    print(f"\n🔑 Testando autenticação...")
    
    try:
        # Pegar um usuário existente para teste
        usuarios = usuario_service.find_all(limit=1)
        if usuarios:
            user = usuarios[0]
            email = user.get('email')
            senha = user.get('senha')
            
            if email and senha:
                print(f"   Testando login com: {email}")
                
                # Testar autenticação
                auth_result = usuario_service.authenticate(email, senha)
                if auth_result:
                    print(f"   ✅ Autenticação bem-sucedida!")
                    print(f"   Nome: {auth_result.get('nome')}")
                    print(f"   Tipo: {auth_result.get('tipo')}")
                else:
                    print(f"   ❌ Falha na autenticação")
            else:
                print(f"   ⚠️ Usuário sem email/senha para teste")
        else:
            print(f"   ⚠️ Nenhum usuário encontrado para teste")
            
    except Exception as e:
        print(f"❌ Erro no teste de autenticação: {e}")

def main():
    """Função principal"""
    print("🚀 Teste completo MongoDB Atlas\n")
    
    # Verificar variáveis de ambiente
    print("🔧 Verificando configuração:")
    print(f"   DB_HOST: {os.getenv('DB_HOST', 'NÃO CONFIGURADO')[:50]}...")
    print(f"   MONGO_DATABASE: {os.getenv('MONGO_DATABASE', 'NÃO CONFIGURADO')}")
    print(f"   MONGO_USERNAME: {os.getenv('MONGO_USERNAME', 'NÃO CONFIGURADO')}")
    
    # Teste 1: Conexão básica
    if not test_atlas_connection():
        print("❌ Falha na conexão básica com Atlas")
        return
    
    # Teste 2: Dados reais
    test_real_data()
    
    # Teste 3: Autenticação
    test_authentication()
    
    print("\n🎉 Testes concluídos! MongoDB Atlas conectado com sucesso!")

if __name__ == "__main__":
    main()