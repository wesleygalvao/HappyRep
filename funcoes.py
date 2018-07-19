from random import *

def valida_usuario(usuario,senha,cursor):
    cursor.execute("""SELECT * FROM "HappyRep".USUARIOS WHERE LOGIN = '%s' AND SENHA = '%s'"""%(usuario,senha))
    achou_usuario = cursor.fetchone()
    if(achou_usuario):
        return True
    else:
        return False

def calcula_valor(produtos,cursor):
    soma = 0
    for x in range(len(produtos)):
        print(produtos[x])
        cursor.execute("""SELECT MIN(PRECO) FROM "HappyRep".OFERECE WHERE NOMEMARCA='%s'"""%produtos[x])
        valor = cursor.fetchone()[0]
        convertido = valor[2:len(valor)-3] + '.' + valor[len(valor)-2:len(valor)]
        soma += float(convertido)
    return soma

def calcula_hora(hora):
    hora_fim = str((int(hora[0:2]) + 2) % 24) + hora[2:len(hora)]
    return hora_fim

def seleciona_faxineira(cursor):
    cursor.execute("""SELECT CPF FROM "HappyRep".PROFISSIONALLIMPEZA""")
    profissionais = cursor.fetchall()
    numero = randint(0,len(profissionais)-1)
    return profissionais[numero][0]

def seleciona_reparo(cursor):
    cursor.execute("""SELECT CPF FROM "HappyRep".PROFISSIONALREPAROS""")
    profissionais = cursor.fetchall()
    numero = randint(0,len(profissionais)-1)
    return profissionais[numero][0]

def seleciona_alimentacao(cursor):
    profissionais = []
    cursor.execute("""SELECT CPF FROM "HappyRep".NUTRICIONISTA""")
    nutricionistas = cursor.fetchall()
    numero_nutri = randint(0, len(nutricionistas) - 1)
    profissionais.append(nutricionistas[numero_nutri][0])
    cursor.execute("""SELECT CPF FROM "HappyRep".PROFISSIONALCOZINHA""")
    cozinheiros = cursor.fetchall()
    numero_coz = randint(0, len(cozinheiros) - 1)
    profissionais.append(cozinheiros[numero_coz][0])
    return profissionais

def pode_criar_cardapio(ordem,usuario,cursor):
    cursor.execute("""SELECT CPF FROM "HappyRep".USUARIOS WHERE LOGIN = '%s'"""%usuario)
    cpf = cursor.fetchone()[0]
    cursor.execute("""SELECT ordemservico_alimentacao FROM "HappyRep".ALIMENTACAO WHERE cpf_nutri='%s'"""%cpf)
    servicos = cursor.fetchall()
    for x in range(len(servicos)):
        servicos[x] = servicos[x][0]
    if ordem in servicos:
        return True
    else:
        return False

def encontra_servico(ordem,cursor):
    cursor.execute("""SELECT * FROM "HappyRep".ALIMENTACAO WHERE ordemservico_alimentacao='%s'"""%ordem)
    if(cursor.fetchone()):
        return 'alimentacao'
    cursor.execute("""SELECT * FROM "HappyRep".FAXINA WHERE ordemservico_faxina='%s'"""%ordem)
    if (cursor.fetchone()):
        return 'limpeza'
    cursor.execute("""SELECT * FROM "HappyRep".REPARO WHERE ordemservico_reparo='%s'"""%ordem)
    if (cursor.fetchone()):
        return 'reparo'


