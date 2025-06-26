
from datetime import datetime
import locale
import cx_Oracle
import base64
import os
import io
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import requests
import qrcode
import json
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.common import I2of5
from pdf2image import convert_from_bytes
from pyzbar.pyzbar import decode


def API(url,params):
    api_key = os.getenv('FOCCO_API_KEY')
    api_token = os.getenv('FOCCO_API_TOKEN')
    params = {'chave': api_key} | params
    dados = requests.get(url, headers={'Authorization':'Bearer ' + api_token}, params=params)
    dados = dados.json() 
    dados = dados['value']
    return dados


def Query(sql, params):
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_service = os.getenv('DB_SERVICE')
    try:
        dsn = cx_Oracle.makedsn(db_host, db_port, service_name=db_service)
        connection = cx_Oracle.connect(user=db_user, password=db_password, dsn=dsn)
        cursor = connection.cursor()
        cursor.execute(sql, params or {})
        if cursor.description:
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            dados = []
            for row in rows:
                item = {}
                for col_name, value in zip(columns, row):
                    col_index = columns.index(col_name)
                    col_type = cursor.description[col_index][1]

                    if col_type == cx_Oracle.DB_TYPE_BLOB or col_type == cx_Oracle.BLOB:
                        if value is not None:
                            blob_data = value.read()
                            base64_data = base64.b64encode(blob_data).decode('utf-8')
                            item[col_name] = base64_data
                        else: item[col_name] = None
                    else: item[col_name] = value
                dados.append(item)
            return dados
        else:
            connection.commit()
            return None
    finally:
        if cursor: cursor.close()
        if connection: connection.close()


def caminho_diretorio():
    caminhos = ['//dc1-srv-otm-01/imagens/','//10.1.57.248/imagens/','/mnt/imagens/']
    for caminho in caminhos:
        if os.path.exists(caminho):
            return caminho
    raise FileNotFoundError("Caminho ao diretório não encontrado.")


def set_locale():
    locais_preferidos = ['pt_BR.utf8','en_US.utf8']
    for loc in locais_preferidos:
        try:
            locale.setlocale(locale.LC_ALL, loc)
            return loc
        except locale.Error:
            continue
    raise locale.Error("Nenhum locale válido foi encontrado ou configurado.")


def executavel_pdf():
    caminhos = ['/usr/local/bin/wkhtmltopdf','../django/plugins/wkhtmltopdf.exe']
    for caminho in caminhos:
        if os.path.exists(caminho):
            return caminho
    raise FileNotFoundError("wkhtmltopdf não encontrado no sistema.")


def get_ordinal_suffix(day):
    """Retorna o sufixo ordinal para um dia."""
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
    return suffix


def format_date(data_ref):
    """Retorna a data atual no formato 'January 1st, 2021'."""
    locale.setlocale(locale.LC_ALL, 'en_US.utf-8') #'en_US.UTF-8' or 'pt_BR.UTF-8'
    data_ref = data_ref.replace ('-','/') 
    if data_ref :
        data = datetime.strptime(data_ref, "%d/%m/%Y")
    else:
        data = datetime.now()
    month_name = data.strftime('%B')
    day = data.day
    year = data.year
    ordinal_suffix = get_ordinal_suffix(day)
    formatted_date = f"{month_name} {day}{ordinal_suffix}, {year}"
    return formatted_date


def processar_imagem(imagem,angulo=0):
    image_file = open(imagem, "rb")
    imagem = base64.b64encode(image_file.read()).decode('utf-8')
    image_data = base64.b64decode(imagem)
    img = Image.open(BytesIO(image_data))
    if angulo !=0:
        img = img.rotate(angulo, expand=True)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_base64  # Retorna a imagem em base64


def image_to_base64(image):
    """Converte uma imagem PIL para uma string base64."""
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
 

def base64_to_image(base64_image):
    """Converte uma string de imagem em base64 para um objeto de imagem PIL."""
    try:
        image_data = base64.b64decode(base64_image)
        image = Image.open(BytesIO(image_data))
        return image
    except Exception as e:
        return None


def invert_image_x(base64_image):
    """Inverte uma imagem base64 no eixo X e retorna a nova imagem em base64."""
    try:
        img = base64_to_image(base64_image)
        if img is None: return ''
        img_inverted = img.transpose(Image.FLIP_LEFT_RIGHT)
        return image_to_base64(img_inverted)
    except Exception as e:
        return ''


def remove_background_from_base64(imagem):
    try:
        try:
            image_file = open(imagem, "rb")
            imagem = base64.b64encode(image_file.read()).decode('utf-8')
        except: None

        # Decodificar a imagem base64
        image_data = base64.b64decode(imagem)
        
        # Abrir a imagem usando PIL
        img = Image.open(BytesIO(image_data)).convert("RGBA")
        
        # Converter a imagem para um array numpy para processamento com OpenCV
        np_img = np.array(img)
        
        # Converter a imagem para o formato BGR que o OpenCV usa
        bgr_img = cv2.cvtColor(np_img, cv2.COLOR_RGBA2BGRA)

        # Aplicar filtro de desfoque para suavizar a imagem
        blurred_img = cv2.GaussianBlur(bgr_img, (5, 5), 0)
        
        # Convertendo para o formato de imagem em escala de cinza
        gray_img = cv2.cvtColor(blurred_img, cv2.COLOR_BGRA2GRAY)
        
        # Aplicar um limiar para criar uma máscara binária
        _, mask = cv2.threshold(gray_img, 240, 255, cv2.THRESH_BINARY)
        
        # Inverter a máscara
        mask_inv = cv2.bitwise_not(mask)
        
        # Aplicar a máscara invertida para remover o fundo
        img_no_bg = cv2.bitwise_and(bgr_img, bgr_img, mask=mask_inv)
        
        # Converter a imagem de volta para formato RGBA
        img_no_bg = cv2.cvtColor(img_no_bg, cv2.COLOR_BGRA2RGBA)
        
        # Criar uma imagem PIL a partir do array numpy
        img_no_bg_pil = Image.fromarray(img_no_bg)
        
        # Salvar a imagem resultante em um buffer
        buffer = BytesIO()
        img_no_bg_pil.save(buffer, format="PNG")
        
        # Converter o buffer para base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        return img_base64
    
    except Exception as e:
        return ''    


def encontrar_substituir_x(imagem_path, valor_substituicao):
    # Carregar a imagem
    imagem = cv2.imread(imagem_path)

    # Verificar se a imagem foi carregada corretamente
    if imagem is None:
        print(f"Erro ao carregar a imagem. Verifique o caminho: {imagem_path}")
        return

    # Substituir a cor verde (aproximadamente) por branco (255, 255, 255)
    # Definindo intervalo de cor verde (em BGR)
    lower_green = np.array([50, 230, 150])  # Mais restrito, próximo do verde puro
    upper_green = np.array([70, 255, 255])  # Mais restrito, próximo do verde puro

    # Converter para o espaço de cores HSV
    hsv = cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)
    
    # Criar uma máscara para detectar os pixels verdes
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Substituir os pixels verdes por branco
    imagem[mask > 0] = [255, 255, 255]  # Cor branca em BGR

    # Converter para escala de cinza
    gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Usar um método de detecção de bordas, como o Canny
    edges = cv2.Canny(gray, 50, 150)

    # Aplicar a Transformada de Hough para detectar linhas
    linhas = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=100, maxLineGap=10)

    # Criar uma cópia da imagem original para modificar
    imagem_modificada = imagem.copy()

    if linhas is not None:
        # Iterar sobre as linhas detectadas
        for linha in linhas:
            x1, y1, x2, y2 = linha[0]
            # Desenhar as linhas na imagem
            cv2.line(imagem_modificada, (x1, y1), (x2, y2), (0, 0, 0), 2)  # Linha preta (opcional)

    # Adicionar o texto "1,60M" na parte inferior centralizada da imagem
    altura, largura, _ = imagem_modificada.shape
    texto = "1,60M"
    
    # Definir a fonte e o tamanho do texto
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    escala_fonte = 1
    espaco_fonte = 2

    # Calcular o tamanho do texto para centralizar
    (largura_texto, altura_texto), _ = cv2.getTextSize(texto, fonte, escala_fonte, espaco_fonte)
    
    # Calcular a posição para centralizar o texto na borda inferior
    pos_x = (largura - largura_texto) // 2
    pos_y = altura - 10  # 10 pixels acima da borda inferior

    # Colocar o texto na imagem
    cv2.putText(imagem_modificada, texto, (pos_x, pos_y), fonte, escala_fonte, (0, 0, 0), espaco_fonte, lineType=cv2.LINE_AA)

    # Salvar a imagem modificada
    cv2.imwrite('imagem_modificada.jpg', imagem_modificada)

    # Exibir a imagem modificada
    cv2.imshow('Imagem Modificada', imagem_modificada)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Exemplo de uso
# valor_substituicao = (255, 255, 255)  # Substituir "X" por uma cor verde (em formato BGR)
# imagem_path = 'C:/Users/gustavo.nunes/Desktop/croqui.png'  # Caminho para a imagem que contém o "X"
# encontrar_substituir_x(imagem_path, valor_substituicao)


def report_code(numero):
    # Tamanho da barra, altura da barra e comprimento do código
    tb = 0.254320987654 * mm  # Largura da barra
    bh = 20 * mm  # Altura da barra
    bcl = 180 * mm  # Comprimento do código de barras

    # Criando um buffer de memória para o PDF
    pdf_io = io.BytesIO()

    # Criando o canvas do PDF
    c = canvas.Canvas(pdf_io, pagesize=(bcl, bh))

    # Criando o objeto do código de barras Interleaved 2 of 5
    bc = I2of5(numero, barWidth=tb, ratio=3, barHeight=bh, bearers=0, quiet=0, checksum=0)

    # Ajustando a largura para se ajustar ao comprimento
    tb = (tb * bcl) / bc.width

    # Criando o objeto do código de barras Interleaved 2 of 5
    bc = I2of5(numero, barWidth=tb, ratio=3, barHeight=bh, bearers=0, quiet=0, checksum=0)

    # Desenhando o código de barras no canvas
    bc.drawOn(c, 0, 0)  # Posiciona centralizado

    # Finalizando o desenho no PDF
    c.save()

    # Retorna para o início do buffer de memória do PDF
    pdf_io.seek(0)

    # Usando pdf2image para converter o PDF em imagem
    img = convert_from_bytes(pdf_io.read(), fmt="png")[0]

    # Criando um buffer de memória para armazenar a imagem PNG
    img_io = io.BytesIO()

    # Salvando a imagem como PNG no buffer de memória
    img.save(img_io, format='PNG')

    # Retorna para o início do buffer de imagem PNG
    img_io.seek(0)

    # Codificando a imagem PNG para base64
    img_base64 = base64.b64encode(img_io.read()).decode('utf-8')

    return img_base64


def qrcode_pix(dados):
    # Converte o dicionário em uma string JSON
    json_data = json.dumps(dados)

    # Cria o QR Code a partir do JSON
    qr = qrcode.make(json_data)

    # Cria um buffer de memória para armazenar o QR Code em formato de imagem
    buffer = io.BytesIO()

    # Salva o QR Code no buffer em formato PNG
    qr.save(buffer, format="PNG")

    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Converte o conteúdo do buffer para base64
    return img_base64

def ler_qrcode(imagem_path):
    # Carrega a imagem
    img = Image.open(imagem_path)

    # Decodifica o QR Code da imagem
    qr_codes = decode(img)

    # Verifica se encontrou algum QR Code na imagem
    if qr_codes:
        for qr_code in qr_codes:
            # Extrai os dados (em formato de string)
            dados = qr_code.data.decode('utf-8')
            
    return dados