from flask import Flask, jsonify, request, make_response
from framkework_sql import Autor, Postagem, app, db 
import jwt
from datetime import datetime,timedelta
from functools import wraps
#1 Definir o objetivo da API exe: iremos montar um blog onde poderemos excluir, editar, postar e consultar postagens do blog
#2 Qual sera o URL base da API
#3 Quais sao os endpoints ex: se o requisito é de poder consultar, editar, criar, deletar voce tera que criar endpoints para estas operações
#4 Quais recursos serão disponibilizados pela API
#5 Quais verbos HTTP serão disponibilizados 
#get
#put
#post
#delete
#6 Quais são  os URL para cada um
#ex: GET http://localhost:5000/postagens

#Token obrigatorio 
def token_obrigatorio(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
            if not token:
                return jsonify({'mensagem': 'Token não esta incluso'}, 401)
            try:
                resultado = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                autor = Autor.query.filter_by(id_autor= resultado['id_autor']).first()
            except jwt.ExpiredSignatureError:
                return jsonify({'mensagem': 'Token expirado!'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'mensagem': 'Token inválido!'}), 401
            except Exception as e:
                return jsonify({'mensagem': f'Erro inesperado: {str(e)}'}), 500
            return f(autor,*args,**kwargs)
    return decorated


#definindo endpoint para login !!!
@app.route('/login')
def login():
   auth =  request.authorization
   if not auth or not auth.username or not auth.password:
       return make_response('Login invalido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
   usuario = Autor.query.filter_by(nome=auth.username).first()
   if not usuario:
        return make_response('Login invalido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})
   if auth.password == usuario.senha:
      token = jwt.encode({'id_autor': usuario.id_autor, 'exp': (datetime.utcnow()+ timedelta(minutes=30)).timestamp()},
                          app.config['SECRET_KEY'])
      return jsonify({'token': token})
   return make_response('Login invalido', 401, {'WWW-Authenticate': 'Basic realm="Login obrigatório"'})

    

#definindo rota padrao
@app.route('/')
@token_obrigatorio
def obter_postagens(autor):
   postagens =  Postagem.query.all()
   lista_de_postagens = []
   for postagem in postagens:
       postagem_atual = {}
       postagem_atual['id_postagem'] = postagem.id_postagem
       postagem_atual['id_autor'] = postagem.id_autor
       postagem_atual['titulo'] = postagem.titulo
       lista_de_postagens.append(postagem_atual)
       return jsonify({'autores': lista_de_postagens})
   
#criando get com ID
@app.route('/postagem/<int:id_postagem>', methods=['GET'])
@token_obrigatorio  
def obter_postagem_por_indice(autor,id_postagem):
   postagem =  Postagem.query.filter_by(id_postagem = id_postagem).first()
   if not postagem:
       return jsonify({'mensagem': 'Autor não encontrado!'})
   postagem_atual = {}
   postagem_atual['id_postagem'] = postagem.id_postagem
   postagem_atual['titulo'] = postagem.titulo
   postagem_atual['id_autor'] = postagem.id_autor
   return jsonify({'Voce buscou pela postagem': postagem_atual})

#criando post
@app.route('/postagem', methods=['POST'])
@token_obrigatorio
def nova_postagem(autor):
  nova_postagem =  request.get_json()
  postagem = Postagem(id_postagem = nova_postagem['id_postagem'], titulo = nova_postagem['titulo'], id_autor = nova_postagem['id_autor'])
  db.session.add(postagem)
  db.session.commit
  return jsonify({'mensagem': 'Usuario criado com sucesso!'}, 200)
   
#alterar postagem existente 
@app.route('/postagem/<int:id_postagem>', methods= ['PUT'])
@token_obrigatorio
def alterar_postagem(autor,id_postagem):
   postagem_alterar = request.get_json()
   postagem = Postagem.query.filter_by(id_postagem = id_postagem).first()
   if not postagem:
       return({'mensagem': 'Postagem não encontrada!'})
   try:
        postagem.id_postagem = postagem_alterar['id_postagem']
   except:
       pass
   try:
        postagem.titulo = postagem_alterar['titulo']
   except:
       pass
   try:
       postagem.id_autor = postagem_alterar['id_autor']
   except:
       pass
   db.session.commit
   return jsonify({'mensagem': 'Usuario cadastrado com sucesso!'}, 200)
   
#excluir postagem
@app.route('/postagem/<int:id_postagem>', methods= ['DELETE'])
@token_obrigatorio
def excluir_postagem(autor,id_postagem):
    postagem_existente = Postagem.query.filter_by(id_postagem = id_postagem).first()
    if not postagem_existente:
        return jsonify({'mensagem': 'Autor não encontrado!'})
    db.session.delete(postagem_existente)
    db.session.commit
    return jsonify({'mensagem': 'Postagem excluida com sucesso!'})
    
#definindo rota padrao
@app.route('/autores')   
@token_obrigatorio
def obter_autores(autor):
   autores = Autor.query.all()
   lista_de_autores = []
   for autor in autores:
       autor_atual = {}
       autor_atual['id_autor'] = autor.id_autor
       autor_atual['nome'] = autor.nome
       autor_atual['email'] = autor.email
       lista_de_autores.append(autor_atual)
       return jsonify({'autores': lista_de_autores})

#Procurar autores por id
@app.route('/autores/<int:id_autor>', methods=['GET'])
@token_obrigatorio
def obter_autor_por_id(autor,id_autor):
   autor =  Autor.query.filter_by(id_autor = id_autor).first()
   if not autor:
       return jsonify('Autor não encontrado!')
   autor_atual = {}
   autor_atual['id_autor'] = autor.id_autor
   autor_atual['nome'] = autor.nome
   autor_atual['email'] = autor.email
   autor_atual['Admin'] = autor.admin
   return jsonify(f"Voce buscou pelo autor: {autor_atual}")

#Criar autores
@app.route('/autores', methods= ['POST'])
@token_obrigatorio
def adicionar_autor(autor):
   novo_autor = request.get_json()
   autor = Autor(nome= novo_autor['nome'], senha= novo_autor['senha'], email=novo_autor['email'])
   db.session.add(autor)
   db.session.commit
   return jsonify({'mensagem': 'Usuario criado com sucesso!'}, 200)

#Para Alterar autores
@app.route('/autores/<int:id_autor>', methods=['PUT'])
@token_obrigatorio
def altera_autor(autor,id_autor):
    usuario_para_alterar = request.get_json()
    autor = Autor.query.filter_by(id_autor = id_autor).first()
    if not autor:
        return jsonify({'mensagem': 'Autor não foi encontrado!'})
    try:
            autor.nome = usuario_para_alterar['nome']
    except:
        pass
    try:
            autor.email = usuario_para_alterar['email']
    except:
        pass
    try:
            autor.senha = usuario_para_alterar['senha']
    except:
        pass

    db.session.commit
    return jsonify({'mensagem': 'Usuario alterado com sucesso!'}, 200)

#Para deletar autores
@app.route('/autores/<int:id_autor>', methods=['DELETE'])
@token_obrigatorio
def deletar_autor(autor,id_autor):
    autor_existente = Autor.query.filter_by(id_autor = id_autor).filter()
    if not autor_existente:
        return jsonify({'mensagem': 'Autor não encontrado!'})
    db.session.delete(autor_existente)
    db.session.commit()
    return jsonify({'mensagem': 'Autor excluido com sucesso!'})


#rodando API criando sua porta e host
app.run(port= 5000, host='localhost', debug=True)