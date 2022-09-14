#importação de módulos 
from asyncio.windows_events import NULL
from distutils.log import error
from queue import Empty
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import yaml
import random 

#inicialização do framework Flask e todas as suas funções pela variável "app"
app = Flask(__name__)

#"Chave secreta para funcionamento do framework Flash, sem ele não funciona! 42 foi um número que escolhi como senha.
app.secret_key = b'42'

#"Aqui chamo e digo para que o framework Yaml seja completamente carregado através de uma variável chamada "db". Solicito para que abra as configurações localizadas no arquivo "db.yaml". Lá estão carregadas as diretrizes para que o Workbench do MySQL funcione. 
#Abra e edite o arquivo "db.yaml", se precisar. O nome do user, como padrão, está root. Edite tbm a senha, mudando para aquela que você configurou no seu computador! Dica: geralmente a senha dos computadores da fatec é 'fatec'."
db = yaml.full_load(open("db.yaml"))
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]

#inicialização do framework MySQL do flask_mysqldb e todas as suas funções pela varíavel "mysql".
mysql = MySQL(app)

#criação de rota
@app.route("/", methods=["GET", "POST"])
def indexHome():
    return render_template("login.html")
 
#"Rota de página web criada. Ela está localizada em localhost/ ."
#"Utiliza os métodos GET para pegar informações do banco de dados. POST para mandar informações pro banco de dados."
@app.route("/cadastro", methods=["GET", "POST"])
def indexCadastro():
    agenciaBancaria = "0001"
    contaBancaria = None
    saldoBancario = None
    cpfValidator = None
    
#configurando a aquisicão das variaveis do formulario em HTML pelo request em Python
    if request.method == "POST":

        userDetails = request.form
        name = userDetails["nome"]
        cpf = userDetails["cpf"]
        dataAniversario = userDetails["dataAniversario"]
        genero = userDetails["genero"]
        endereço = userDetails["endereço"]        
        senha = userDetails["senha"]
        confirmaçãoSenha = userDetails["confirmaçãoSenha"]  
        senhaCriptografada = generate_password_hash(senha) 
        senhaCriptografada2 = None
        
         #critério preenchimento campos de senha
        if not name or not cpf or not dataAniversario or not genero or not endereço or not senha or not confirmaçãoSenha:
            flash("Preencha todos os campos do formulário")
            return redirect (url_for("indexCadastro"))
        if senha == confirmaçãoSenha:
            if check_password_hash(senhaCriptografada, senha):
                senhaCriptografada2 = senhaCriptografada
        else:
            flash("As senhas precisam ser iguais")
            return redirect (url_for("indexCadastro"))
        
        #gerador de conta bancaria automatico
        numero = []
        for i in range(1, 10):
            numero.append(random.randint(0, 9))
        contaBancaria="".join(map(str,numero))
               
        cur = mysql.connection.cursor()
        
        #verificando se cpf já consta nos registros
        cur.execute("SELECT cpf FROM cadastro WHERE cpf = %s", [cpf])
        cpfValidator = cur.fetchone()
        if cpfValidator is not NULL:
            flash("CPF já cadastrado")
            return redirect (url_for("indexCadastro"))
        
        #salvando dados no BD e finalizando operação
        cur.execute("INSERT INTO cadastro (agenciaBancaria, contaBancaria, saldoBancario, nome, cpf, dataAniversario, genero, endereço, senha, confirmaçãoSenha) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (agenciaBancaria, contaBancaria, saldoBancario, name, cpf, dataAniversario, genero, endereço, senhaCriptografada, senhaCriptografada2))
        mysql.connection.commit()
        cur.close()
        return '''<p>Cadastro criado com sucesso!</p><br><input type="submit" value="Voltar""></input><br>'''
    return render_template("cadastro.html", error=error)

#comando inicia automaticamente o programa, habilitando o debug sempre que algo for atualizado!
app.run(debug=True) 