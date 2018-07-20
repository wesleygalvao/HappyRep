from flask import *
from funcoes import *
import psycopg2

app = Flask(__name__)
app.secret_key = 'labBD'
conn_string = "host=localhost dbname=LabBD user=postgres password=qwer20"
conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/autenticar',methods =['GET','POST'])
def autenticar():
    if(valida_usuario(request.form['usuario'],request.form['senha'],cursor)):
        flash(request.form['usuario'] + ' logou com sucesso!')
        session['usuario_logado'] = request.form['usuario']
        cursor.execute("""SELECT TIPO FROM "HappyRep".USUARIOS WHERE LOGIN='%s'"""%request.form['usuario'])
        tipo = cursor.fetchone()[0]
        session['tipo_usuario'] = tipo
        return redirect('/sistema')
    else:
        flash('Usuário não encontrado.')
        return redirect('/')

@app.route('/cadastrar')
def cadastra_usuario():
    return render_template('cadastra_usuario.html')

@app.route('/autentica_cadastro',methods =['GET','POST'])
def autentica_usuario():
    cursor.execute("""SELECT * FROM "HappyRep".USUARIOS WHERE LOGIN ='%s'"""%request.form['usuario'])
    achou_usuario = cursor.fetchone()
    cursor.execute("""SELECT * FROM "HappyRep".morador WHERE cpf ='%s'"""%request.form['cpf'])
    achou_morador = cursor.fetchone()
    if(achou_usuario or achou_morador):
        flash('Usuario já cadastrado.')
        return redirect('/cadastrar')
    else:
        cursor.execute("""INSERT INTO "HappyRep".USUARIOS (LOGIN,SENHA,CPF,TIPO) VALUES ('%s','%s','%s','usuario')"""
                       %(request.form['usuario'],request.form['senha'],request.form['cpf']))
        #CADASTRO MORADOR
    cursor.execute("""SELECT "HappyRep".insere_morador('%s',NULL,'%s','%s','%s','%s','%s','%s')"""%(request.form['cpf'],request.form['nome'],request.form['rg'],request.form['data_nascimento'],
                                                                                                    request.form['sexo'],request.form['universidade'],request.form['trabalho']))
    conn.commit()
    flash(request.form['usuario'] + ' inserido com sucesso!')
    return redirect('/')

@app.route('/deslogar')
def deslogar():
    session['usuario_logado'] = None
    flash('Usuario deslogado.')
    return redirect('/')

@app.route('/sistema')
def sistema():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('sistema.html', tipo_usuario = session['tipo_usuario'])

@app.route('/solicitacoes_pendentes')
def solicitacoes_pendentes():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    cursor.execute("""SELECT CPF FROM "HappyRep".USUARIOS WHERE login='%s'""" % session['usuario_logado'])
    cpf = cursor.fetchone()[0]
    cursor.execute("""SELECT IDREPUBLICA FROM "HappyRep".MORADOR WHERE CPF='%s'"""%cpf)
    id_rep = cursor.fetchone()[0]
    if(not id_rep):
        flash('Você não está cadastrado em nenhuma república.')
        return redirect('/participar_republica')
    cursor.execute("""SELECT * FROM "HappyRep".SERVICO WHERE idrepublica =%s""" %id_rep)
    lista = cursor.fetchall()
    cursor.execute("""SELECT NOMEREPUBLICA FROM "HappyRep".REPUBLICA WHERE IDREPUBLICA=%s"""%id_rep)
    republica = cursor.fetchone()[0]
    cursor.execute("""SELECT SUM(VALOR) FROM "HappyRep".SERVICO WHERE idrepublica =%s""" %id_rep)
    total = cursor.fetchone()[0]
    return render_template('solicitacoes_pendentes.html', lista = lista, tamanho = len(lista), republica = republica, total = total)

@app.route('/cadastrar_republica')
def cadastrar_republica():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('cadastra_republica.html')

@app.route('/autentica_republica',methods =['GET','POST'])
def autenticar_republica():
    cursor.execute("""SELECT * FROM "HappyRep".REPUBLICA WHERE NOMEREPUBLICA='%s'"""%request.form['nome'])
    if(cursor.fetchone()):
        flash('República já cadastrada.')
        return redirect('/cadastrar_republica')
    cursor.execute("""SELECT * FROM "HappyRep".view_listarepublicas""")
    id_rep = len(cursor.fetchall()) + 1
    #CADASTRA REPÚBLICA
    cursor.execute("""SELECT "HappyRep".insere_republica(%s,'%s','%s','%s','%s',%s)"""%(id_rep,request.form['nome'],request.form['rua'],request.form['bairro'],
                                                                                        request.form['cidade'],request.form['numero']))
    conn.commit()
    flash('República cadastrada com sucesso.')
    return redirect('/sistema')

@app.route('/participar_republica')
def participar_republica():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    cursor.execute("""SELECT * FROM "HappyRep".view_listarepublicas""")
    lista = cursor.fetchall()
    return render_template('participar_republica.html',lista = lista, tamanho = len(lista))

@app.route('/confirma_participacao',methods =['GET','POST'])
def confirma_participacao():
    cursor.execute("""SELECT idrepublica FROM "HappyRep".REPUBLICA WHERE NOMEREPUBLICA = '%s'"""%request.form['nome'])
    idrep = cursor.fetchone()
    if(idrep):
        cursor.execute("""SELECT cpf FROM "HappyRep".USUARIOS WHERE login = '%s'"""%session['usuario_logado'])
        cpf_usuario = cursor.fetchone()
        cursor.execute("""SELECT "HappyRep".atualiza_morador(%s,'%s')"""%(idrep[0],cpf_usuario[0]))
        conn.commit()
        flash('O usuário ' + session['usuario_logado'] + ' agora está participando da república ' + request.form['nome'])
        return redirect('/sistema')
    flash('República não encontrada.')
    return redirect('/participar_republica')
@app.route('/cadastrar_funcionario')
def cadastrar_funcionario():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('cadastrar_funcionario.html')

@app.route('/autentica_funcionario',methods =['GET','POST'])
def autenticar_funcionario():
    cursor.execute("""SELECT * FROM "HappyRep".FUNCIONARIO WHERE CPF = '%s'"""%request.form['cpf'])
    achou_funcionario = cursor.fetchone()
    cursor.execute("""SELECT * FROM "HappyRep".morador WHERE cpf ='%s'""" % request.form['cpf'])
    achou_morador = cursor.fetchone()
    if(achou_funcionario or achou_morador):
        flash('CPF já cadastrado.')
        return redirect('/cadastrar_funcionario')
    #CADASTRA FUNCIONÁRIOS
    if(not trabalho_valido(request.form['trabalho'])):
        flash('Trabalho inexistente.')
        return redirect('/cadastrar_funcionario')
    cursor.execute("""SELECT "HappyRep".insere_funcionario('%s','%s','%s','%s','%s','%s')"""%(request.form['cpf'],request.form['nome'],request.form['rg'],request.form['email'],request.form['data_nascimento'],request.form['sexo']))
    if(request.form['trabalho'] == 'nutricionista'):
        #CADASTRA NUTRICIONISTA
        cursor.execute("""SELECT "HappyRep".insere_nutricionista('%s')"""%request.form['cpf'])
    elif(request.form['trabalho'] == 'cozinha'):
        #CADASTRA PROFISSIONAL COZINHA
        cursor.execute("""SELECT "HappyRep".insere_profissionalcozinha('%s')"""%request.form['cpf'])
    elif (request.form['trabalho'] == 'limpeza'):
        #CADASTRA PROFISSIONAL LIMPEZA
        cursor.execute("""SELECT "HappyRep".insere_profissionallimpeza('%s')""" % request.form['cpf'])
    elif (request.form['trabalho'] == 'reparo'):
        #CADASTRA PROFISSIONAL REPARO
        cursor.execute("""SELECT "HappyRep".insere_profissionalreparos('%s',NULL)""" % request.form['cpf'])
    conn.commit()
    flash('Funcionário inserido com sucesso.')
    return redirect('/sistema')

@app.route('/solicitar_servico')
def solicitar_servico():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('solicitar_servico.html')

@app.route('/cadastrar_produto')
def cadastrar_produto():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('cadastrar_produto.html')

@app.route('/autentica_produto',methods =['GET','POST'])
def autentica_produto():
    cursor.execute("""SELECT * FROM "HappyRep".PRODUTO WHERE NOMEMARCA='%s'"""%request.form['nome'])
    if(cursor.fetchone()):
        flash('Produto já registrado.')
        return redirect('/cadastrar_produto')
    #CADASTRA PRODUTO
    cursor.execute("""SELECT "HappyRep".insere_produto('%s','%s','%s')"""
                   % (request.form['nome'], request.form['descricao'], request.form['categoria']))
    flash('Produto inserido com sucesso.')
    conn.commit()
    return redirect('/sistema')

@app.route('/cadastrar_fornecedor')
def cadastrar_fornecedor():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('cadastrar_fornecedor.html')

@app.route('/autentica_fornecedor',methods =['GET','POST'])
def autentica_fornecedor():
    cursor.execute("""SELECT * FROM "HappyRep".FORNECEDOR WHERE EMPRESA='%s'"""%request.form['empresa'])
    if(cursor.fetchone()):
        flash('Fornecedor já registrado.')
        return redirect('/cadastrar_produto')
    cursor.execute("""SELECT * FROM "HappyRep".view_listafornecedor""")
    id_forn = len(cursor.fetchall()) + 1
    #CADASTRA FORNECEDOR
    cursor.execute("""SELECT "HappyRep".insere_fornecedor(%s,'%s','%s')"""
                   %(id_forn,request.form['contato'],request.form['empresa']))
    flash('Fornecedor inserido com sucesso.')
    conn.commit()
    return redirect('/sistema')

@app.route('/cadastrar_precos')
def cadastrar_precos():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('cadastrar_precos.html')

@app.route('/autentica_precos',methods =['GET','POST'])
def autentica_precos():
    if(len(request.form['produtos'].split()) != len(request.form['precos'].split())):
        flash('Número de preços diferente do numero de produtos.')
        return redirect('/cadastrar_precos')
    cursor.execute("""SELECT codfornecedor FROM "HappyRep".FORNECEDOR WHERE empresa='%s'"""%request.form['fornecedor'])
    id_forn = cursor.fetchone()
    if(not id_forn):
        flash('Fornecedor especificado não existe.')
        return redirect('/cadastrar_precos')
    produtos = request.form['produtos'].split()
    precos = request.form['precos'].split()
    for x in range(len(request.form['produtos'].split())):
        #CADASTRA PRODUTO OFERECIDO POR FORNECEDOR
        cursor.execute("""SELECT "HappyRep".insere_oferece('%s',%s,'%s')"""
                       %(produtos[x],id_forn[0],precos[x]))
    conn.commit()
    flash('Preços de produtos do fornecedor ' + request.form['fornecedor'] + ' cadastrados com sucesso.')
    return redirect('/sistema')

@app.route('/solicitar_reparo')
def solicita_reparo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('solicitar_reparo.html')

@app.route('/autentica_reparo',methods=['GET','POST'])
def autentica_reparo():
    produtos = request.form['produtos'].split()
    for x in range(len(produtos)):
        cursor.execute("""SELECT * FROM "HappyRep".PRODUTO WHERE NOMEMARCA = '%s'""" % produtos[x])
        if (not cursor.fetchone()):
            flash('Produto ' + produtos[x] + ' não registrado.')
            return redirect('/solicitar_limpeza')
    cursor.execute(""""SELECT * FROM HappyRep".view_listaservico""")
    ord_serv = len(cursor.fetchall()) + 1
    cursor.execute("""SELECT CPF FROM "HappyRep".USUARIOS WHERE login='%s'""" % session['usuario_logado'])
    cpf_usuario = cursor.fetchone()
    cursor.execute("""SELECT idrepublica FROM "HappyRep".MORADOR WHERE cpf='%s'""" % cpf_usuario[0])
    id_rep = cursor.fetchone()
    if (not id_rep[0]):
        flash('Usuário não está cadastrado em uma república.')
        return redirect('/participar_republica')
    valor = calcula_valor(produtos, cursor)
    hora_fim = calcula_hora(request.form['hora'])
    cpf = seleciona_reparo(cursor)
    cursor.execute("""INSERT INTO "HappyRep".SERVICO (ordemservico,idrepublica,descricao,data_servico,valor,hora_inicio,hora_fim)
                            VALUES (%s,%s,'%s','%s',%s,'%s','%s')""" % (ord_serv, id_rep[0], request.form['descricao'],
                                                                        request.form['data'], valor,
                                                                        request.form['hora'], hora_fim))
    cursor.execute("""SELECT "HappyRep".cria_servico_reparo('%s','%s')""" % (ord_serv, cpf))
    for x in range(len(produtos)):
        cursor.execute("""SELECT "HappyRep".insere_gera('%s','%s')"""%(ord_serv,produtos[x]))
    conn.commit()
    flash('Solicitação de reparo efetuada com sucesso.')
    return redirect('/sistema')

@app.route('/solicitar_limpeza')
def solicita_limpeza():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('solicitar_limpeza.html')

@app.route('/autentica_limpeza',methods=['GET','POST'])
def autentica_limpeza():
    produtos = request.form['produtos'].split()
    for x in range(len(produtos)):
        cursor.execute("""SELECT * FROM "HappyRep".PRODUTO WHERE NOMEMARCA = '%s'"""%produtos[x])
        if(not cursor.fetchone()):
            flash('Produto ' + produtos[x] + ' não registrado.')
            return redirect('/solicitar_limpeza')
    cursor.execute("""SELECT * FROM "HappyRep".view_listaservico""")
    ord_serv = len(cursor.fetchall()) + 1
    cursor.execute("""SELECT CPF FROM "HappyRep".USUARIOS WHERE login='%s'"""%session['usuario_logado'])
    cpf_usuario = cursor.fetchone()
    cursor.execute("""SELECT idrepublica FROM "HappyRep".MORADOR WHERE cpf='%s'""" %cpf_usuario[0])
    id_rep = cursor.fetchone()
    if(not id_rep[0]):
        flash('Usuário não está cadastrado em uma república.')
        return redirect('/participar_republica')
    valor = calcula_valor(produtos,cursor)
    hora_fim = calcula_hora(request.form['hora'])
    cpf = seleciona_faxineira(cursor)
    #CADASTRO DE SERVICO
    cursor.execute("""INSERT INTO "HappyRep".SERVICO (ordemservico,idrepublica,descricao,data_servico,valor,hora_inicio,hora_fim)
                        VALUES (%s,%s,'%s','%s',%s,'%s','%s')""" % (ord_serv, id_rep[0], request.form['descricao'], request.form['data']
                                                                                       , valor, request.form['hora'], hora_fim))
    #CADASTRO SERVICO FAXINA
    cursor.execute("""SELECT "HappyRep".cria_servico_faxina('%s','%s')"""%(ord_serv,cpf))
    for x in range(len(produtos)):
        #INSERE EM GERA
        cursor.execute("""SELECT "HappyRep".insere_gera('%s','%s')"""%(ord_serv,produtos[x]))
    conn.commit()
    flash('Solicitação de limpeza efetuada com sucesso.')
    return redirect('/sistema')

@app.route('/solicitar_alimentacao')
def solicita_alimentacao():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('solicitar_alimentacao.html')

@app.route('/autentica_alimentacao',methods=['GET','POST'])
def autentica_alimentacao():
    cursor.execute("""SELECT * FROM "HappyRep".view_listaservico""")
    ord_serv = len(cursor.fetchall()) + 1
    cursor.execute("""SELECT CPF FROM "HappyRep".USUARIOS WHERE login='%s'"""%session['usuario_logado'])
    cpf_usuario = cursor.fetchone()
    cursor.execute("""SELECT idrepublica FROM "HappyRep".MORADOR WHERE cpf='%s'""" %cpf_usuario[0])
    id_rep = cursor.fetchone()
    if(not id_rep):
        flash('Usuário não está cadastrado em uma república.')
        return redirect('/participar_republica')
    valor = 0
    hora_fim = calcula_hora(request.form['hora'])
    cpf_nutricionista = seleciona_alimentacao(cursor)[0]
    cpf_cozinheira = seleciona_alimentacao(cursor)[1]
    #CADASTRO DE SERVICO
    cursor.execute("""INSERT INTO "HappyRep".SERVICO (ordemservico,idrepublica,descricao,data_servico,valor,hora_inicio,hora_fim)
                        VALUES (%s,%s,'%s','%s',%s,'%s','%s')""" % (ord_serv, id_rep[0], request.form['descricao'], request.form['data']
                                                                                       , valor, request.form['hora'], hora_fim))
    cursor.execute("""SELECT "HappyRep".cria_servico_alimentacao ('%s','%s','%s')"""%(ord_serv,cpf_nutricionista,cpf_cozinheira))
    conn.commit()
    flash('Solicitação de alimentação efetuada com sucesso.')
    return redirect('/sistema')

@app.route('/avaliar_servico')
def avalia_servico():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('avaliar_servico.html')

@app.route('/autentica_avaliacao', methods=['GET','POST'])
def autentica_avaliacao():
    cursor.execute("""SELECT CPF FROM "HappyRep".USUARIOS WHERE login='%s'""" % session['usuario_logado'])
    cpf_usuario = cursor.fetchone()
    cursor.execute("""SELECT idrepublica FROM "HappyRep".MORADOR WHERE cpf='%s'""" % cpf_usuario[0])
    id_rep_usuario = cursor.fetchone()
    if(not id_rep_usuario):
        flash('Você não está cadastrado em nenhuma república.')
        return redirect('/participar_republica')
    cursor.execute("""SELECT idrepublica FROM "HappyRep".SERVICO WHERE ordemservico='%s'"""%request.form['ordem'])
    id_rep_ordem = cursor.fetchone()
    if(not id_rep_ordem):
        flash('Serviço não existe.')
        return redirect('/avaliar_servico')
    if(id_rep_usuario[0] != id_rep_ordem[0]):
        flash('Sua república não solicitou esse serviço!')
        return redirect('/avaliar_servico')
    #CADASTRA AVALIAÇÃO
    cursor.execute("""SELECT "HappyRep".insere_avalia('%s','%s','%s')"""
                   %(cpf_usuario[0],request.form['ordem'],request.form['nota']))
    conn.commit()
    flash('Avaliação efetuada com sucesso.')
    return redirect('/sistema')

@app.route('/servicos_pendentes')
def servicos_pendentes():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    lista = []
    cursor.execute("""SELECT CPF FROM "HappyRep".USUARIOS WHERE login='%s'"""%session['usuario_logado'])
    cpf = cursor.fetchone()[0]
    if(session['tipo_usuario'] == 'nutricionista'):
        cursor.execute("""SELECT ordemservico_alimentacao FROM "HappyRep".ALIMENTACAO WHERE cpf_nutri ='%s'"""%cpf)
        servicos = cursor.fetchall()
    elif(session['tipo_usuario'] == 'cozinha'):
        cursor.execute("""SELECT ordemservico_alimentacao FROM "HappyRep".ALIMENTACAO WHERE cpf_cozin ='%s'"""%cpf)
        servicos = cursor.fetchall()
    elif(session['tipo_usuario'] == 'reparo'):
        cursor.execute("""SELECT ordemservico_reparo FROM "HappyRep".REPARO WHERE cpf ='%s'""" %cpf)
        servicos = cursor.fetchall()
    elif(session['tipo_usuario'] == 'limpeza'):
        cursor.execute("""SELECT ordemservico_faxina FROM "HappyRep".FAXINA WHERE cpf_limpeza ='%s'""" %cpf)
        servicos = cursor.fetchall()
    for x in range(len(servicos)):
        cursor.execute("""SELECT * FROM "HappyRep".SERVICO WHERE ordemservico='%s'"""%servicos[x][0])
        servico = cursor.fetchone()
        lista.append(servico)
    return render_template('servicos_pendentes.html', lista = lista, tamanho = len(lista))

@app.route('/criar_cardapio')
def criar_cardapio():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    return render_template('criar_cardapio.html')

@app.route('/autentica_cardapio',methods=['GET','POST'])
def autentica_cardapio():
    produtos = request.form['produtos'].split()
    if(not pode_criar_cardapio(request.form['ordem'],session['usuario_logado'],cursor)):
        flash('Você não está associado(a) a esse serviço.')
        return redirect('/criar_cardapio')
    for x in range(len(produtos)):
        cursor.execute("""SELECT * FROM "HappyRep".PRODUTO WHERE NOMEMARCA = '%s'"""%produtos[x])
        if(not cursor.fetchone()):
            flash('Produto ' + produtos[x] + ' não registrado.')
            return redirect('/criar_cardapio')
    for x in range(len(produtos)):
        cursor.execute("""INSERT INTO "HappyRep".GERA (ordemservico,nomemarca) VALUES ('%s','%s')""" % (request.form['ordem'], produtos[x]))
    valor = calcula_valor(produtos, cursor)
    cursor.execute("""SELECT "HappyRep".atualiza_servico(%s,'%s')"""%(valor,request.form['ordem']))
    cursor.execute("""SELECT "HappyRep".insere_cardapio('%s','%s')"""
                   %(request.form['ordem'],request.form['descricao']))
    conn.commit()
    flash('Cardápio criado com sucesso.')
    return redirect('/sistema')

@app.route('/produtos_a_comprar')
def produtos_a_comprar():
    quantidades = []
    precos = []
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    cursor.execute("""SELECT DISTINCT nomemarca FROM "HappyRep".GERA""")
    produtos = cursor.fetchall()
    for x in range(len(produtos)):
        produtos[x] = produtos[x][0]
    for produto in produtos:
        cursor.execute("""SELECT * FROM "HappyRep".GERA WHERE nomemarca='%s'"""%produto)
        quantidades.append(len(cursor.fetchall()))
    for x in range(len(produtos)):
        cursor.execute("""SELECT MIN(PRECO) FROM "HappyRep".OFERECE WHERE NOMEMARCA='%s'""" % produtos[x])
        precos.append(cursor.fetchone()[0])
    return render_template('produtos_comprar.html', produtos = produtos, quantidades = quantidades, precos=precos, tamanho=len(produtos))

@app.route('/notas_servicos')
def notas_servicos():
    profissionais = []
    medias = []
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect('/')
    cursor.execute("""SELECT * FROM "HappyRep".view_ordensservico""")
    servicos = cursor.fetchall()
    for x in range(len(servicos)):
        servicos[x] = servicos[x][0]
    for x in range(len(servicos)):
        cursor.execute("""SELECT AVG(nota) FROM "HappyRep".AVALIA WHERE ordemservico = '%s'"""%servicos[x])
        medias.append(cursor.fetchone()[0])
        if(encontra_servico(servicos[x],cursor) == 'alimentacao'):
            cursor.execute("""SELECT cpf_cozin,cpf_nutri FROM "HappyRep".ALIMENTACAO WHERE ordemservico_alimentacao='%s'""" % servicos[x])
            profissionais.append(cursor.fetchone()[0] + ' e ' + cursor.fetchone()[1])
        elif(encontra_servico(servicos[x],cursor) == 'limpeza'):
            cursor.execute("""SELECT cpf_limpeza FROM "HappyRep".FAXINA WHERE ordemservico_faxina='%s'"""%servicos[x])
            profissionais.append(cursor.fetchone()[0])
        elif(encontra_servico(servicos[x],cursor) == 'reparo'):
            cursor.execute("""SELECT cpf FROM "HappyRep".REPARO WHERE ordemservico_reparo='%s'""" % servicos[x])
            profissionais.append(cursor.fetchone()[0])
    return render_template('notas_servicos.html', tamanho=len(servicos), servicos = servicos,profissionais=profissionais,medias=medias)

app.run()
