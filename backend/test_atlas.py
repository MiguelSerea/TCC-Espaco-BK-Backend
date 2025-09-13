import pymongo

try:
    # SUBSTITUA pela sua string de conexão real
    connection_string = "mongodb+srv://Miguelserea01_db_user:Ij59b6tc0Q5b3FpW@cluster0.xpq8jyp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    print("🔗 Tentando conectar ao MongoDB Atlas...")
    print(f"📍 Usuário: Miguelserea01_db_user")
    
    # Conectar
    client = pymongo.MongoClient(connection_string)
    
    # Testar conexão
    client.admin.command('ping')
    print("✅ Conexão com MongoDB Atlas bem-sucedida!")
    
    # Listar bancos
    databases = client.list_database_names()
    print(f"📊 Bancos disponíveis: {databases}")
    
    # Testar operação no banco
    db = client.espaco_backend
    collection = db.test_connection
    
    # Inserir documento de teste
    test_doc = {"usuario": "Miguelserea01_db_user", "teste": "conexao_ok"}
    result = collection.insert_one(test_doc)
    print(f"📝 Documento de teste criado com ID: {result.inserted_id}")
    
    # Limpar teste
    collection.delete_one({"_id": result.inserted_id})
    print("🧹 Documento de teste removido")
    
except Exception as e:
    print(f"❌ Erro na conexão: {str(e)}")
    print("\n🔍 Verificações necessárias:")
    print("1. URL do cluster está correta?")
    print("2. Network Access liberado no Atlas?")
    print("3. Cluster está ativo?")
    print("4. Credenciais estão corretas?")
