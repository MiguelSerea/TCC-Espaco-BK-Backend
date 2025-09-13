# models.py - Versão simplificada sem conflitos
from django.db import models

# Modelo simples apenas para manter a estrutura do Django
# Vamos usar PyMongo diretamente para as operações reais

class DummyModel(models.Model):
    """Modelo dummy para manter a estrutura Django"""
    name = models.CharField(max_length=100)
    
    class Meta:
        managed = False  # Django não vai gerenciar esta tabela
        db_table = 'dummy'