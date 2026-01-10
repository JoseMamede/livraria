from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.decimal128 import Decimal128
from decimal import Decimal
import os
from datetime import datetime

# ===========================
# Configuração da conexão com o MongoDB Atlas
# ===========================
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client.livraria  
livros_col = db.books
usuarios_col = db.usuarios
pedidos_col = db.pedidos

# ===========================
# Classe Livro
# ===========================
class Livro:
    def __init__(self, titulo, preco, categoria, tags, autores, mais_recente_edicao, numero_autores, data_publicacao, editora, descricao, isbn, estoque, imagem_capa):
        self.titulo = titulo
        self.preco = preco
        self.categoria = categoria
        self.tags = tags
        self.autores = autores
        self.mais_recente_edicao = mais_recente_edicao
        self.numero_autores = numero_autores
        self.data_publicacao = data_publicacao
        self.editora = editora
        self.descricao = descricao
        self.isbn = isbn
        self.estoque = estoque
        self.imagem_capa = imagem_capa

    def salvar(self):
        dados = self.__dict__.copy()
        dados['preco'] = Decimal128(Decimal(str(self.preco)))
        resultado = livros_col.insert_one(dados)
        return resultado.inserted_id

    @staticmethod
    def buscar_por_id(id_livro):
        try:
            return livros_col.find_one({"_id": ObjectId(id_livro)})
        except:
            return None

    @staticmethod
    def buscar_todos():
        return list(livros_col.find())
    
    @staticmethod
    def buscar_livros(filtros=None, pagina=1, por_pagina=12):
        query = {}
        if filtros:
            # 1. Pesquisa por Nome/Título (O Campo 'nome' do HTML)
            if filtros.get('nome'):
                # Usamos 'titulo' porque é como salvamos no popula_banco.py
                query['titulo'] = {'$regex': filtros['nome'], '$options': 'i'}
            
            # 2. Filtro de Categorias
            if filtros.get('categorias'):
                query['categoria'] = {'$in': filtros['categorias']}
                
            # 3. Filtro de Preço (Conversão segura para Decimal128)
            if filtros.get('preco_min') or filtros.get('preco_max'):
                query['preco'] = {}
                try:
                    if filtros.get('preco_min') and filtros.get('preco_min') != '':
                        query['preco']['$gte'] = Decimal128(Decimal(str(filtros['preco_min'])))
                    if filtros.get('preco_max') and filtros.get('preco_max') != '':
                        query['preco']['$lte'] = Decimal128(Decimal(str(filtros['preco_max'])))
                    # Se o dicionário de preço ficar vazio após o try, removemos a chave
                    if not query['preco']:
                        del query['preco']
                except:
                    if 'preco' in query: del query['preco']

        # Paginação
        skip = (pagina - 1) * por_pagina
        
        # Execução no banco 'books' (livros_col)
        cursor = livros_col.find(query).skip(skip).limit(por_pagina)
        total = livros_col.count_documents(query)
        
        # Log para você ver no terminal se a busca está chegando certa
        print(f"DEBUG MONGO: Query={query} | Encontrados={total}")
        
        return list(cursor), total

    @staticmethod
    def categorias_disponiveis():
        categorias = livros_col.distinct("categoria") + livros_col.distinct("categor...")
        return sorted(list(set([c for c in categorias if c])))

    @staticmethod
    def tags_disponiveis():
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
        dados = self.__dict__.copy()
        resultado = usuarios_col.insert_one(dados)
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
        dados = self.__dict__.copy()
        if isinstance(self.total, (int, float, str)):
            dados['total'] = Decimal128(Decimal(str(self.total)))
        resultado = pedidos_col.insert_one(dados)
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