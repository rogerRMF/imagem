import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from io import BytesIO
from PIL import Image as PILImage
import datetime

# 1. Configuração de Página Avançada
st.set_page_config(
    page_title="Portal de Laudos Técnicos", 
    page_icon="📋",
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Inicialização da Memória do Aplicativo (Session State)
if "lista_registros" not in st.session_state:
    st.session_state.lista_registros = []

# --- CABEÇALHO CORPORATIVO ---
st.markdown("""
    <div style="background-color: #1E3A8A; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
        <h1 style="color: white; margin: 0; font-size: 28px; font-family: sans-serif;">📋 Sistema de Relatórios Multi-Fotográficos</h1>
        <p style="color: #93C5FD; margin: 5px 0 0 0; font-size: 14px;">Tire múltiplas fotos, descreva cada uma e gere o laudo estruturado</p>
    </div>
""", unsafe_allow_html=True)

# --- CORPO DO APLICATIVO (Layout em Colunas) ---
col_dados, col_camera = st.columns([1, 1.2], gap="large")

with col_dados:
    st.subheader("📝 Dados do Inspetor")
    with st.container(border=True):
        nome_responsavel = st.text_input(
            "Nome Completo do Responsável:",
            placeholder="Ex: Rogério Ferreira",
            help="Este nome constará formalmente no rodapé e assinatura do documento."
        )
        
        data_exibicao = datetime.datetime.now().strftime("%d/%m/%Y")
        st.text_input("Data da Inspeção:", value=data_exibicao, disabled=True)

    st.subheader("🔍 Nova Ocorrência / Foto")
    with st.container(border=True):
        descricao_foto = st.text_area(
            "Descrição desta Foto Específica:", 
            placeholder="Descreva minuciosamente os detalhes técnicos observados NESTA imagem...",
            height=120,
            key="temp_descricao"
        )
        
        botao_adicionar = st.button("➕ Adicionar Foto ao Relatório", use_container_width=True, type="secondary")

with col_camera:
    st.subheader("📸 Captura de Imagem")
    with st.container(border=True):
        foto_capturada = st.camera_input("Ativar Câmera do Dispositivo")

# Lógica para salvar a imagem e descrição na memória
if botao_adicionar:
    if foto_capturada is not None:
        st.session_state.lista_registros.append({
            "imagem": foto_capturada.getvalue(),
            "descricao": descricao_foto if descricao_foto.strip() else "Nenhuma descrição detalhada fornecida para este registro."
        })
        st.toast("Foto e descrição adicionadas com sucesso!", icon="✅")
    else:
        st.error("⚠️ Nenhuma imagem capturada! Tire uma foto antes de clicar em adicionar.")

# --- HISTÓRICO VISUAL DAS FOTOS JÁ ADICIONADAS ---
if st.session_state.lista_registros:
    st.divider()
    st.subheader(f"🖼️ Fotos Adicionadas ao Laudo ({len(st.session_state.lista_registros)})")
    
    cols_historico = st.columns(4)
    for idx, item in enumerate(st.session_state.lista_registros):
        with cols_historico[idx % 4]:
            with st.container(border=True):
                st.image(item["imagem"], caption=f"Foto {idx+1}", use_container_width=True)
                st.caption(f"**Descrição:** {item['descricao'][:50]}...")
                if st.button(f"🗑️ Remover", key=f"del_{idx}", use_container_width=True):
                    st.session_state.lista_registros.pop(idx)
                    st.rerun()

# --- ÁREA DE EMISSÃO DO PDF ---
if st.session_state.lista_registros:
    st.divider()
    st.subheader("🚀 Fechamento e Emissão do Documento")
    
    with st.container(border=True):
        if nome_responsavel.strip():
            st.success(f"✅ Tudo pronto! O relatório contém {len(st.session_state.lista_registros)} registro(s) fotográfico(s) estruturado(s).")
            
            # Função auxiliar interna que monta o PDF corrigido e blindado contra quebras órfãs
            def gerar_pdf_multiplo(lista_dados, nome_usuario):
                buffer = BytesIO()
                doc = SimpleDocTemplate(
                    buffer, 
                    pagesize=letter,
                    rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
                )
                
                elementos = []
                estilos = getSampleStyleSheet()
                
                # Definição e Customização de Estilos
                estilo_titulo = ParagraphStyle(
                    'TituloRelatorio', parent=estilos['Heading1'],
                    fontSize=22, leading=26, alignment=TA_CENTER, spaceAfter=15, textColor="#1E3A8A"
                )
                estilo_meta_lbl = ParagraphStyle(
                    'MetaLabel', parent=estilos['Normal'],
                    fontSize=11, leading=15, alignment=TA_LEFT, textColor="#1E3A8A"
                )
                estilo_meta_val = ParagraphStyle(
                    'MetaValue', parent=estilos['Normal'],
                    fontSize=11, leading=15, alignment=TA_LEFT, textColor="#333333"
                )
                estilo_item_titulo = ParagraphStyle(
                    'ItemTitulo', parent=estilos['Heading2'],
                    fontSize=13, leading=17, alignment=TA_LEFT, spaceBefore=5, spaceAfter=8, textColor="#1E3A8A"
                )
                estilo_desc_lbl = ParagraphStyle(
                    'DescLabel', parent=estilos['Normal'],
                    fontSize=11, leading=15, alignment=TA_LEFT, spaceBefore=6, spaceAfter=2, textColor="#1E3A8A"
                )
                estilo_texto = ParagraphStyle(
                    'TextoRelatorio', parent=estilos['Normal'],
                    fontSize=11, leading=16, alignment=TA_JUSTIFY, spaceAfter=5, textColor="#222222"
                )
                estilo_assinatura = ParagraphStyle(
                    'AssinaturaRelatorio', parent=estilos['Normal'],
                    fontSize=11, leading=15, alignment=TA_CENTER, spaceAfter=4
                )

                # 1. Cabeçalho Formal
                elementos.append(Paragraph("<b>RELATÓRIO TÉCNICO FOTOGRÁFICO</b>", estilo_titulo))
                data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
                
                dados_meta = [
                    [Paragraph("<b>Responsável Técnico:</b>", estilo_meta_lbl), Paragraph(nome_usuario.upper(), estilo_meta_val)],
                    [Paragraph("<b>Data de Emissão:</b>", estilo_meta_lbl), Paragraph(data_atual, estilo_meta_val)]
                ]
                tabela_meta = Table(dados_meta, colWidths=[130, 370])
                tabela_meta.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ]))
                elementos.append(tabela_meta)
                elementos.append(HRFlowable(width="100%", thickness=1.5, color="#1E3A8A", spaceBefore=10, spaceAfter=15))
                
                # 2. LOOP: Varre os itens blindando as fotos com KeepTogether
                for idx, registro in enumerate(lista_dados):
                    conteudo_bloco = []
                    
                    conteudo_bloco.append(Paragraph(f"<b>Item {idx + 1} — Registro Fotográfico</b>", estilo_item_titulo))
                    
                    img_pil = PILImage.open(BytesIO(registro["imagem"]))
                    largura_max = 440  
                    w_percent = (largura_max / float(img_pil.size[0]))
                    h_size = int((float(img_pil.size[1]) * float(w_percent)))
                    
                    img_buffer = BytesIO()
                    img_pil.save(img_buffer, format="JPEG")
                    img_buffer.seek(0)
                    
                    pdf_img = Image(img_buffer, width=largura_max, height=h_size)
                    pdf_img.hAlign = 'CENTER'
                    conteudo_bloco.append(pdf_img)
                    conteudo_bloco.append(Spacer(1, 8))
                    
                    conteudo_bloco.append(Paragraph(f"<b>Descrição do Item {idx + 1}:</b>", estilo_desc_lbl))
                    conteudo_bloco.append(Paragraph(registro["descricao"], estilo_texto))
                    
                    if idx < len(lista_dados) - 1:
                        conteudo_bloco.append(Spacer(1, 10))
                        conteudo_bloco.append(HRFlowable(width="100%", thickness=0.5, color="#CCCCCC", spaceBefore=5, spaceAfter=5))
                    
                    elementos.append(KeepTogether(conteudo_bloco))
                    elementos.append(Spacer(1, 10))
                
                elementos.append(Spacer(1, 20))
                
                # 3. Assinatura de Fechamento
                bloco_assinatura = []
                bloco_assinatura.append(HRFlowable(width="40%", thickness=1, color="#A3A3A3", hAlign='CENTER', spaceAfter=6))
                bloco_assinatura.append(Paragraph(f"<b>{nome_usuario.upper()}</b>", estilo_assinatura))
                bloco_assinatura.append(Paragraph("Responsável pela Inspeção Fotográfica", estilo_assinatura))
                elementos.append(KeepTogether(bloco_assinatura))
                
                doc.build(elementos)
                buffer.seek(0)
                return buffer

            # Executa a geração do PDF para deixar em memória
            pdf_data = gerar_pdf_multiplo(st.session_state.lista_registros, nome_responsavel)
            nome_arquivo_pdf = f"laudo_tecnico_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

            # Botão de Download simplificado ocupando a largura total de forma elegante
            st.download_button(
                label="📥 Baixar Relatório PDF Concluído",
                data=pdf_data,
                file_name=nome_arquivo_pdf,
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
            
            # Botão para resetar o app
            st.write("")
            if st.button("🧹 Limpar Dados e Iniciar Novo Relatório", use_container_width=True):
                st.session_state.lista_registros = []
                st.rerun()
        else:
            st.info("⚠️ Preencha o campo 'Nome Completo do Responsável' no topo para liberar o download do relatório.")