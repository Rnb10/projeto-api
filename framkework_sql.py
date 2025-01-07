from flask import Flask
from flask_sqlalchemy import SQLAlchemy


#Criar uma API FLASK 
app = Flask(__name__)
#Criar uma instancia de SQL alchemy
app.config['SECRET_KEY'] = 'RicardoNB19@#'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blogricardo.db'

db = SQLAlchemy(app)
db:SQLAlchemy
#definir a estrutura da tabela Postagem 
class Postagem(db.Model):
    __tablename__ = 'postagem'
    id_postagem = db.Column(db.Integer , primary_key=True)
    titulo = db.Column(db.String)
    id_autor= db.Column(db.Integer, db.ForeignKey('autor.id_autor') )
#definir a estrutura da tabela Autor
class Autor(db.Model):
    __tablename__ = 'autor'
    id_autor = db.Column(db.Integer, primary_key=True)
    nome= db.Column(db.String)
    email= db.Column(db.String) 
    senha= db.Column(db.String)
    admin= db.Column(db.Boolean)
    postagens= db.relationship('Postagem')

#Executar os comandos para criar o banco de dados
print("Criando o banco de dados...")
def inicializar_banco():
    with app.app_context():
        db.drop_all()
        print("Tabelas excluídas.")
        db.create_all()
        print("Tabelas criadas.")

        # Criar usuários adms
        autor1 = Autor(nome='Ricardo Nardao', email='nardaoricardo@gmail.com', senha='123', admin=True)
        db.session.add(autor1)
        db.session.commit()
        print("Autor criado.")

if __name__ == '__main__':
    inicializar_banco()