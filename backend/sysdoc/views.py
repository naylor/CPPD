from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import RectangleObject
from PyPDF2.errors import PdfReadError
from django.utils.text import slugify
from datetime import datetime
from io import BytesIO
import os
import logging
from textwrap import wrap
from rest_framework.response import Response
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from .models import Processo, Itemizacao, TarefaProcesso, UsuarioDocs, UsuarioProcesso
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .api.serializers import ItemizacaoTreeSerializer

logger = logging.getLogger('sysdocLogger')

class ArvoreView(APIView):
    def get(self, request, processo_id):
        raiz = Itemizacao.objects.filter(processo_id=processo_id, itemSuperior=None).order_by('ordem')
        serializer = ItemizacaoTreeSerializer(raiz, many=True)
        return Response({'arvore': serializer.data})
    

    
@api_view(['GET'])
def activate_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({'detail': 'Usuário inválido.'}, status=400)

    if user.is_active:
        return Response({'detail': 'Usuário já ativado.'})

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return Response({'detail': 'Usuário ativado com sucesso!'})
    else:
        return Response({'detail': 'Token de ativação inválido.'}, status=400)

class ResendActivationView(APIView):
    def post(self, request):
        username = request.data.get("username")
        if not username:
            return Response({"error": "Usuário não informado."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
            if user.is_active:
                return Response({"detail": "Usuário já está ativado."}, status=status.HTTP_200_OK)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            domain = "localhost:8080"
            activation_link = f"http://{domain}/activate/{uidb64}/{token}"
            send_mail(
                "Ative sua conta",
                f"Olá,\n\nPor favor, clique no link abaixo para ativar sua conta:\n{activation_link}\n\nSe você não se cadastrou, ignore este e-mail.",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=f"""
                    <p>Olá,</p>
                    <p>Por favor, clique no link abaixo para ativar sua conta:</p>
                    <p>
                    <a href="{activation_link}">{activation_link}</a>
                    </p>
                    <p>Se você não se cadastrou, ignore este e-mail.</p>
                """
            )
            return Response({"detail": "Link de ativação reenviado."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        if not user.check_password(current_password):
            return Response({'detail': 'Senha atual incorreta.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Senha alterada com sucesso.'})
    

def gerar_pdf_processo(request, processo_id, usuario_id, usuario_process_id):
    processo = get_object_or_404(Processo, id=processo_id)
    usuario = get_object_or_404(User, id=usuario_id)
    usuario_processo = get_object_or_404(
        UsuarioProcesso, id=usuario_process_id, usuario=usuario, processo=processo
    )

    writer = PdfWriter()
    outlines = []
    page_counter = 0
    link_annotations = []
    index_pages_by_item = {}
    pontos_por_itemizacao = {}
    links_para_indices = []

    def get_quantidade_final(doc):
        return doc.qdeReajustada if getattr(doc, 'qdeReajustada', None) is not None else getattr(doc, 'quantidade', 0)

    def calcular_pontos_itemizacao(item):
        total = 0
        for tarefa in TarefaProcesso.objects.filter(item=item):
            ponto = tarefa.ponto or 0
            for doc in UsuarioDocs.objects.filter(tarefaProcesso=tarefa, usuarioProcesso=usuario_processo):
                quantidade = get_quantidade_final(doc)
                total += ponto * quantidade
        for sub in item.subitems.all():
            total += calcular_pontos_itemizacao(sub)
        pontos_por_itemizacao[item.id] = total
        return total

    def gerar_pagina_totais_itemizacoes():
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        w, h = letter
        y = h - 50

        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, y, f"Processo: {processo.nome}")
        y -= 30

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, f"Usuário: {usuario.get_full_name() or usuario.username}")
        y -= 40

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Totais de pontos por itemização")
        y -= 30

        def escrever_linhas(it, nivel, y0):
            nonlocal c
            if y0 < 50:
                c.showPage()
                y0 = h - 50

            pontos = pontos_por_itemizacao.get(it.id, 0)
            nome_formatado = f"{'  ' * nivel}{it.nome}"
            texto = f"{nome_formatado}: {pontos} pts"
            x_pos = 50 + nivel * 20

            if nivel == 0:
                c.setFont("Helvetica-Bold", 12)
                c.setFillColorRGB(0, 0, 1)
                c.drawString(x_pos, y0, texto)
                txt_width = c.stringWidth(texto, "Helvetica-Bold", 12)
                c.setLineWidth(0.5)
                c.line(x_pos, y0 - 1, x_pos + txt_width, y0 - 1)
                c.setFillColorRGB(0, 0, 0)
            else:
                c.setFont("Helvetica", 10)
                c.setFillColorRGB(0, 0, 0)
                c.drawString(x_pos, y0, texto)
                txt_width = c.stringWidth(texto, "Helvetica", 10)

            rect = [x_pos, y0 - 2, x_pos + txt_width, y0 + 10]
            links_para_indices.append({"item_id": it.id, "rect": rect, "page": 0})
            y0 -= 20
            for sub in it.subitems.all():
                y0 = escrever_linhas(sub, nivel + 1, y0)
            return y0

        for root in Itemizacao.objects.filter(processo=processo, itemSuperior__isnull=True):
            y = escrever_linhas(root, 0, y)

        total_pontos_documentos = 0
        for item in Itemizacao.objects.filter(processo=processo):
            for tarefa in TarefaProcesso.objects.filter(item=item):
                ponto = tarefa.ponto or 0
                for doc in UsuarioDocs.objects.filter(tarefaProcesso=tarefa, usuarioProcesso=usuario_processo):
                    quantidade = get_quantidade_final(doc)
                    total_pontos_documentos += ponto * quantidade

        total_pontos_processo = processo.pontos or 0

        if y < 80:
            c.showPage()
            y = h - 50
        c.setLineWidth(1)
        c.line(50, y, w - 50, y)
        y -= 20

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"Total de pontos dos documentos: {total_pontos_documentos} pts")
        y -= 20
        c.drawString(50, y, f"Pontuação mínima do processo: {total_pontos_processo} pts")
        y -= 30

        c.showPage()
        c.save()
        buf.seek(0)
        return PdfReader(buf)

    def gerar_quadro_superior(item_nome, ponto_tarefa, quantidade_doc, w, h):
        buf = BytesIO()
        temp_canvas = canvas.Canvas(buf, pagesize=(w, h))

        max_linhas = 3
        largura_max = 50
        linhas = wrap(item_nome, width=largura_max)

        if len(linhas) > max_linhas:
            linhas = linhas[:max_linhas]
            if len(linhas[-1]) > 3:
                linhas[-1] = linhas[-1][:-3] + '...'
            else:
                linhas[-1] += '...'

        alt = 10
        quad_w = 180
        margem = 10

        linhas_totais = 1 + len(linhas[1:]) + 2
        quad_h = linhas_totais * alt + 8

        x = w - quad_w - margem
        y = h - quad_h - margem

        c = canvas.Canvas(buf, pagesize=(w, h))
        c.setFont("Helvetica", 7)

        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.setFillColorRGB(0.95, 0.95, 0.95)
        c.rect(x, y, quad_w, quad_h, fill=1)

        ty = y + quad_h - 12

        texto_voltar = "↩ VOLTAR"
        c.setFillColorRGB(0, 0, 1)
        txt_width_voltar = c.stringWidth(texto_voltar, "Helvetica", 7)
        x_link = x + quad_w - txt_width_voltar - 5
        c.drawString(x_link, ty, texto_voltar)
        voltar_rect = [x_link, ty - 2, x_link + txt_width_voltar, ty + 8]

        texto_item = linhas[0]
        max_text_width = x_link - (x + 5) - 5
        text_width = c.stringWidth(texto_item, "Helvetica", 7)
        if text_width > max_text_width:
            while text_width > max_text_width and len(texto_item) > 3:
                texto_item = texto_item[:-1]
                text_width = c.stringWidth(texto_item + "...", "Helvetica", 7)
            texto_item += "..."

        c.setFillColorRGB(1, 0, 0)
        c.drawString(x + 5, ty, texto_item)
        ty -= alt

        for L in linhas[1:]:
            c.drawString(x + 5, ty, L)
            ty -= alt

        texto_ponto = f"Ponto da tarefa: {ponto_tarefa}"
        texto_qtd = f"Qtd no doc: {quantidade_doc}"
        c.drawString(x + 5, ty, texto_ponto)
        txt_width_qtd = c.stringWidth(texto_qtd, "Helvetica", 7)
        c.drawString(x + quad_w - txt_width_qtd - 5, ty, texto_qtd)
        ty -= alt

        total = ponto_tarefa * quantidade_doc if ponto_tarefa and quantidade_doc else 0
        c.drawString(x + 5, ty, f"Total de pontos: {total}")

        c.save()
        buf.seek(0)
        return PdfReader(buf), voltar_rect

    def gerar_pdf_itemizacao(item):
        nonlocal page_counter
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        w, h = letter
        y = h - 50
        first_text_page = page_counter
        index_pages_by_item[item.id] = first_text_page

        def escreve(it, nivel, y0):
            nonlocal c
            if it.id not in index_pages_by_item:
                index_pages_by_item[it.id] = first_text_page
            if y0 < 100:
                c.showPage()
                y0 = h - 50
            c.setFont("Helvetica-Bold", max(8, 12 - nivel))
            c.drawString(50 + nivel * 20, y0, it.nome)
            y0 -= 20
            for sub in it.subitems.all():
                y0 = escreve(sub, nivel + 1, y0)
            for tarefa in TarefaProcesso.objects.filter(item=it):
                if y0 < 100:
                    c.showPage()
                    y0 = h - 50
                c.setFont("Helvetica", 10)
                c.drawString(50 + (nivel + 1) * 20, y0, f"Tarefa: {tarefa.nome}")
                y0 -= 20
                c.drawString(50 + (nivel + 1) * 20, y0, f"Descrição: {tarefa.descricao}")
                y0 -= 20
                for doc in UsuarioDocs.objects.filter(tarefaProcesso=tarefa, usuarioProcesso=usuario_processo):
                    if y0 < 100:
                        c.showPage()
                        y0 = h - 50
                    x0 = 50 + (nivel + 2) * 20
                    txt_name = os.path.basename(doc.file.name)
                    ponto_unitario = tarefa.ponto or 0
                    quantidade = get_quantidade_final(doc)
                    pontos_total = ponto_unitario * quantidade

                    # Se houver reajuste, mostra em vermelho e justificativa entre parênteses
                    if getattr(doc, 'qdeReajustada', None) is not None:
                        c.setFont("Helvetica-Bold", 9)
                        c.setFillColorRGB(0.83, 0.18, 0.18)  # vermelho
                        justificativa = getattr(doc, 'obsReajuste', '')
                        link_text = f"Documento: {txt_name}  ({pontos_total} pts)"
                        if justificativa:
                            link_text += f"  ({justificativa})"
                    else:
                        c.setFont("Helvetica", 9)
                        c.setFillColorRGB(0, 0, 1)  # azul padrão
                        link_text = f"Documento: {txt_name}  ({pontos_total} pts)"

                    wtxt = c.stringWidth(link_text, c._fontname, 9)
                    c.drawString(x0, y0, link_text)
                    c.setLineWidth(0.5)
                    c.line(x0, y0 - 1, x0 + wtxt, y0 - 1)
                    c.setFillColorRGB(0, 0, 0)
                    link_annotations.append({
                        "page": first_text_page,
                        "rect": [x0, y0 - 2, x0 + wtxt, y0 + 8],
                        "doc_id": doc.id,
                        "item_id": item.id,
                        "item_nome": item.nome,
                        "ponto": tarefa.ponto or 0,
                        "quantidade": quantidade
                    })
                    y0 -= 20

            if y0 < 100:
                c.showPage()
                y0 = h - 50
            total_pts = pontos_por_itemizacao.get(it.id, 0)
            c.setFont("Helvetica-Bold", 10)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.drawString(50 + nivel * 20, y0, f"→ Total de pontos da itemização '{it.nome}': {total_pts} pts")
            y0 -= 30

            return y0

        y = escreve(item, 0, y)
        c.showPage()
        c.save()
        buf.seek(0)
        reader_txt = PdfReader(buf)

        for i, page in enumerate(reader_txt.pages):
            current_page_num = page_counter + i
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)
            w, h = letter
            texto_voltar = "↩ VOLTAR"
            c.setFont("Helvetica-Bold", 10)
            c.setFillColorRGB(0, 0, 1)
            txt_width = c.stringWidth(texto_voltar, "Helvetica-Bold", 10)
            x_link = w - txt_width - 40
            y_link = h - 30
            c.drawString(x_link, y_link, texto_voltar)
            c.setLineWidth(0.5)
            c.line(x_link, y_link - 1, x_link + txt_width, y_link - 1)
            c.save()

            packet.seek(0)
            overlay = PdfReader(packet)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

            voltar_rect = RectangleObject([x_link, y_link - 2, x_link + txt_width, y_link + 10])
            writer.add_link(current_page_num, 0, voltar_rect)

        page_counter += len(reader_txt.pages)

        def anexar(it):
            nonlocal page_counter
            for tarefa in TarefaProcesso.objects.filter(item=it):
                for doc in UsuarioDocs.objects.filter(tarefaProcesso=tarefa, usuarioProcesso=usuario_processo):
                    with open(doc.file.path, 'rb') as f:
                        data = f.read()
                    try:
                        reader_doc = PdfReader(BytesIO(data))
                    except PdfReadError:
                        logger.error(f"Arquivo inválido ou corrompido: {doc.file.path}")
                        continue
                    info = next((la for la in link_annotations if la['doc_id'] == doc.id), None)
                    item_nome = tarefa.item.nome
                    ponto = info['ponto'] if info else tarefa.ponto or 0
                    quantidade = info['quantidade'] if info else get_quantidade_final(doc)
                    quadro, voltar_rect = gerar_quadro_superior(item_nome, ponto, quantidade, float(reader_doc.pages[0].mediabox.width), float(reader_doc.pages[0].mediabox.height))
                    for i, pg in enumerate(reader_doc.pages):
                        pg.merge_page(quadro.pages[0])
                        writer.add_page(pg)
                        if i == 0:
                            voltar_page = index_pages_by_item.get(item.id, 0)
                            writer.add_link(page_counter, voltar_page, RectangleObject(voltar_rect))
                    outlines.append({"doc_id": doc.id, "page_number": page_counter})
                    page_counter += len(reader_doc.pages)
            for sub in it.subitems.all():
                anexar(sub)

        anexar(item)

    for item in Itemizacao.objects.filter(processo=processo):
        calcular_pontos_itemizacao(item)

    pagina_totais = gerar_pagina_totais_itemizacoes()
    writer.append_pages_from_reader(pagina_totais)
    page_counter += len(pagina_totais.pages)

    for root in Itemizacao.objects.filter(processo=processo, itemSuperior__isnull=True):
        gerar_pdf_itemizacao(root)

    doc_map = {o['doc_id']: o['page_number'] for o in outlines}
    for ann in link_annotations:
        rect = RectangleObject(ann['rect'])
        writer.add_link(ann['page'], doc_map[ann['doc_id']], rect)

    for link in links_para_indices:
        item_id = link['item_id']
        if item_id in index_pages_by_item:
            writer.add_link(link['page'], index_pages_by_item[item_id], RectangleObject(link['rect']))

    out = BytesIO()
    writer.write(out)
    out.seek(0)
    usuario_nome = slugify(usuario.get_full_name() or usuario.username).replace("-", "_")
    processo_nome = slugify(processo.nome).replace("-", "_")
    data_atual = datetime.now().strftime("%Y-%m-%d")
    filename = f"{usuario_nome}_{processo_nome}_{data_atual}.pdf"
    resp = HttpResponse(out.read(), content_type='application/pdf')
    resp['Content-Disposition'] = f'inline; filename="{filename}"'
    return resp