import os
import base64
from io import StringIO

import paramiko
from cryptography.hazmat.primitives import hashes

############################################################
# Compatibilidade com servidores antigos (ssh-rsa)
############################################################

preferred = list(paramiko.transport.Transport._preferred_pubkeys)

if "ssh-rsa" not in preferred:
    preferred.insert(0, "ssh-rsa")
    paramiko.transport.Transport._preferred_pubkeys = tuple(preferred)

if "ssh-rsa" not in paramiko.rsakey.RSAKey.HASHES:
    paramiko.rsakey.RSAKey.HASHES["ssh-rsa"] = hashes.SHA1

############################################################


def _ensure_remote_dir(sftp, remote_directory):

    remote_directory = remote_directory.rstrip("/")

    if not remote_directory:
        return

    dirs = []

    head = remote_directory

    while head not in ("", "/"):
        dirs.append(head)
        head = os.path.dirname(head)

    dirs.reverse()

    for d in dirs:

        try:

            sftp.stat(d)

        except IOError:

            sftp.mkdir(d)

############################################################


def _load_private_key(private_key, passphrase=None):

    key_classes = [

        paramiko.Ed25519Key,
        paramiko.ECDSAKey,
        paramiko.RSAKey

    ]

    ultimo_erro = None

    for key_class in key_classes:

        try:

            return key_class.from_private_key(

                StringIO(private_key),

                password=passphrase

            )

        except Exception as ex:

            ultimo_erro = ex

    raise Exception(
        f"Não foi possível carregar a chave privada ({ultimo_erro})"
    )

############################################################


def _connect(conexao):

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    connect = {

        "hostname": conexao["host"],

        "port": conexao.get("port", 22),

        "username": conexao["username"],

        "look_for_keys": False,

        "allow_agent": False,

        "timeout": conexao.get("timeout", 30)

    }

    ########################################################
    # Autenticação por chave privada
    ########################################################

    if conexao.get("private_key_base64"):

        private_key = base64.b64decode(

            conexao["private_key_base64"]

        ).decode("utf-8")

        key = _load_private_key(

            private_key,

            conexao.get("passphrase")

        )

        connect["pkey"] = key

        #
        # Alguns servidores exigem senha junto da chave
        #

        if conexao.get("password"):

            connect["password"] = conexao["password"]

    ########################################################
    # Autenticação por senha
    ########################################################

    elif conexao.get("password"):

        connect["password"] = conexao["password"]

    else:

        raise Exception(
            "Nenhum método de autenticação configurado."
        )

    ssh.connect(**connect)

    return ssh

############################################################


def _upload_sftp(
    arquivos,
    referencia,
    conexao
):

    ssh = None
    sftp = None

    resultado = []

    try:

        ssh = _connect(conexao)

        sftp = ssh.open_sftp()

        remoto = os.path.join(
            conexao["remote_dir"],
            referencia
        ).replace("\\", "/")

        _ensure_remote_dir(
            sftp,
            remoto
        )

        for arquivo in arquivos:

            nome = os.path.basename(arquivo)

            destino = os.path.join(
                remoto,
                nome
            ).replace("\\", "/")

            tamanho = os.path.getsize(arquivo)

            try:

                print(f"Enviando {nome}...")

                sftp.put(
                    arquivo,
                    destino
                )

                resultado.append({

                    "arquivo": nome,

                    "local": arquivo,

                    "remoto": destino,

                    "tamanho": tamanho,

                    "sucesso": True,

                    "erro": None

                })

                print(f"OK: {nome}")

            except Exception as ex:

                print(f"ERRO: {nome} -> {ex}")

                resultado.append({

                    "arquivo": nome,

                    "local": arquivo,

                    "remoto": destino,

                    "tamanho": tamanho,

                    "sucesso": False,

                    "erro": str(ex)

                })

        sucesso = sum(
            1
            for item in resultado
            if item["sucesso"]
        )

        falha = len(resultado) - sucesso

        return {

            "total": len(resultado),

            "sucesso": sucesso,

            "falha": falha,

            "arquivos": resultado

        }

    finally:

        try:

            if sftp:
                sftp.close()

        except Exception:
            pass

        try:

            if ssh:
                ssh.close()

        except Exception:
            pass

############################################################


def upload(
    arquivos,
    referencia,
    conexao
):

    tipo = conexao.get("tipo")

    dispatch = {

        "sftp": _upload_sftp

    }

    if tipo not in dispatch:

        raise Exception(
            f"Tipo de conexão '{tipo}' não suportado."
        )

    return dispatch[tipo](

        arquivos=arquivos,

        referencia=referencia,

        conexao=conexao

    )
