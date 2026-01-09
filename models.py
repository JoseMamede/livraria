from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from bson.decimal128 import Decimal128 
from datetime import datetime

# ===========================
# Configuração da conexão
# ===========================
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.livraria 

livros_col = db.livros
usuarios_col = db.usuarios
pedidos_col = db.pedidos

# ===========================
# Classe Livro
# ===========================
class Livro:
    @staticmethod
    def buscar_por_id(id_livro):
        try:
            return livros_col.find_one({"_id": ObjectId(id_livro)})
        except:
            return None

    @staticmethod
    def buscar_todos():
        # Busca tudo para garantir que a tela inicial não fique vazia
        return list(livros_col.find())
    
    @staticmethod
    def buscar_livros(filtros=None, pagina=1, por_pagina=12):
        query = {}
        if filtros:
            # Busca flexível: tenta 'título' (com acento) ou 'titulo' (sem)
            if filtros.get('titulo') or filtros.get('nome'):
                termo = filtros.get('titulo') or filtros.get('nome')
                query['$or'] = [
                    {'título': {'$regex': termo, '$options': 'i'}},
                    {'titulo': {'$regex': termo, '$options': 'i'}}
                ]
            
            # Filtro de preço
            if filtros.get('preco'):
                query['preco'] = filtros['preco']
            
            # Filtro de categoria (tenta com acento se necessário)
            if filtros.get('categoria'):
                cat = filtros['categoria']
                query['categoria'] = {'$in': cat} if isinstance(cat, list) else cat

        skip = (pagina - 1) * por_pagina
        cursor = livros_col.find(query).skip(skip).limit(por_pagina)
        total = livros_col.count_documents(query)
        return list(cursor), total

    @staticmethod
    def categorias_disponiveis():
        # Pega as categorias únicas do seu banco
        categorias = livros_col.distinct("categoria")
        return sorted([c for c in categorias if c])

    @staticmethod
    def tags_disponiveis():
        # Se os livros não tiverem o campo 'tags' no Atlas, usamos uma lista padrão
        tags = livros_col.distinct("tags")
        if not tags:
            return ["Ficção", "Romance", "Aventura", "Clássico", "Fantasia"]
        return sorted([t for t in tags if t])

# ===========================
# Classe Usuario
# ===========================
class Usuario:
    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha 

    def salvar(self):
        dados_usuario = self.__dict__.copy()
        resultado = usuarios_col.insert_one(dados_usuario)
        return resultado.inserted_id

    @staticmethod
    def buscar_por_email(email):
        return usuarios_col.find_one({"email": email})

    @staticmethod
    def buscar_por_id(id_usuario):
        try:
            return usuarios_col.find_one({"_id": ObjectId(id_usuario)})
        except:
            return None

# ===========================
# Classe Pedido
# ===========================
class Pedido:
    def __init__(self, id_usuario, livros, data, total, status="pendente"):
        self.id_usuario = id_usuario
        self.livros = livros 
        self.data = data or datetime.now()
        self.total = total
        self.status = status

    def salvar(self):
        dados_pedido = self.__dict__.copy()
        if isinstance(self.total, (int, float, str)):
            dados_pedido['total'] = Decimal128(str(self.total))
        resultado = pedidos_col.insert_one(dados_pedido)
        return resultado.inserted_id

    @staticmethod
    def buscar_por_usuario(id_usuario):
        return list(pedidos_col.find({"id_usuario": id_usuario}))

    @staticmethod
    def buscar_por_id(id_pedido):
        try:
            return pedidos_col.find_one({"_id": ObjectId(id_pedido)})
        except:
            return None