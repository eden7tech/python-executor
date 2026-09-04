import base64
from io import BytesIO
from PIL import Image


def abrir_base64(base64_string):
    """
    Abre uma imagem Base64 e retorna um objeto PIL.Image em RGB.
    """
    img = Image.open(BytesIO(base64.b64decode(base64_string)))
    return img.convert("RGB")


def redimensionar(img, largura=1024, altura=768):
    """
    Redimensiona para um tamanho fixo.
    """
    return img.resize(
        (largura, altura),
        Image.LANCZOS
    )


def miniatura(img, fator=3.25):
    """
    Cria uma miniatura proporcional.
    """
    w, h = img.size

    return img.resize(
        (
            max(1, int(round(w / fator))),
            max(1, int(round(h / fator)))
        ),
        Image.LANCZOS
    )


def salvar_jpeg(img, caminho, qualidade=85):
    """
    Salva uma imagem JPEG otimizada.
    """
    img.save(
        caminho,
        "JPEG",
        quality=qualidade,
        optimize=True
    )


def dimensoes(img):
    return img.size


def largura(img):
    return img.size[0]


def altura(img):
    return img.size[1]


def rotacionar(img, graus):
    return img.rotate(graus, expand=True)


def crop(img, esquerda, topo, direita, baixo):
    return img.crop(
        (
            esquerda,
            topo,
            direita,
            baixo
        )
    )


def converter_rgb(img):
    return img.convert("RGB")


def converter_webp(img, caminho, qualidade=80):
    img.save(
        caminho,
        "WEBP",
        quality=qualidade
    )


def converter_png(img, caminho):
    img.save(
        caminho,
        "PNG"
    )
