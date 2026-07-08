import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from io import BytesIO
from PIL import Image as PILImage
import datetime

# 1. Configuração de Página Avançada
st.set_page_config(
    page_title="Portal de Laudos Técnicos", 
    page_icon="📋",
    layout="wide", # Tela cheia para um visual mais profissional e espaçado
    initial_sidebar_state="collapsed"
)

# --- CABEÇALHO CORPORATIVO ---
st.markdown("""
    <div style="background-color: #1E3A8A; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
        <h1 style="color: white; margin: 0; font-size: 28px; font-family: sans-serif;">📋 Sistema de Relatórios Fotográficos</h1>
        <p style="color: #93C5FD; margin: 5px 0 0 0; font-size: 14px;">Emissão rápida de laudos técnicos e vistorias em campo</p>
    </div>
""", unsafe_allow_html=True)

# --- CORPO DO APLICATIVO (Layout em Colunas) ---
col_dados, col_camera = st.columns([1, 1.2], gap="large")

with col_dados:
    st.subheader("📝 Dados do Inspetor")
    with st.container(border=True): # Cria um card elegante ao redor dos inputs
        nome_responsavel = st.text_input(
            "Nome Completo do Responsável:",
            placeholder="Ex: Rogério Ferreira",
            help="Este nome constará formalmente no rodapé e assinatura do documento."
        )
        
        data_exibicao = datetime.datetime.now().strftime("%d/%m/%Y")
        st.text_input("Data da Inspeção:", value=data_exibicao, disabled=True, help="Data gerada automaticamente pelo sistema.")

    st.subheader("🔍 Informações da Ocorrência")
    with st.container(border=True):
        descricao = st.text_area(
            "Descrição Detalhada dos Fatos Constatados:", 
            placeholder="Descreva minuciosamente os detalhes técnicos do objeto, ambiente ou inconformidade capturada...",
            height=200,
            help="Evite termos informais. O texto digitado aqui preencherá o corpo principal do PDF."
        )

with col_camera:
    st.subheader("📸 Registro Fotográfico")
    with st.container(border=True):
        foto_capturada = st.camera_input("Ativar Câmera do Dispositivo")

    # --- ÁREA DE PROCESSAMENTO E EMISSÃO DO PDF ---
    st.subheader("🚀 Emissão do Documento")
    with st.container(border=True):
        if foto_capturada:
            if nome_responsavel.strip():
                st.success("✅ Tudo pronto! Os dados e a foto foram validados.")
                
                # Função auxiliar para gerar o PDF na memória
                def gerar_pdf(imagem_bytes, texto_descricao, nome_usuario):
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(
                        buffer, 
                        pagesize=letter,
                        rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
                    )
                    
                    elementos = []
                    estilos = getSampleStyleSheet()
                    
                    estilo_titulo = ParagraphStyle(
                        'TituloRelatorio',
                        parent=estilos['Heading1'],
                        fontSize=22, leading=26, alignment=TA_CENTER, spaceAfter=15, textColor="#1E3A8A"
                    )
                    estilo_subtitulo = ParagraphStyle(
                        'SubtituloRelatorio',
                        parent=estilos['Normal'],
                        fontSize=11, leading=14, alignment=TA_LEFT, spaceAfter=5, textColor="#333333"
                    )
                    estilo_texto = ParagraphStyle(
                        'TextoRelatorio',
                        parent=estilos['Normal'],
                        fontSize=12, leading=18, alignment=TA_JUSTIFY, spaceAfter=15
                    )
                    estilo_assinatura = ParagraphStyle(
                        'AssinaturaRelatorio',
                        parent=estilos['Normal'],
                        fontSize=12, leading=16, alignment=TA_CENTER, spaceAfter=5
                    )

                    elementos.append(Paragraph("<b>RELATÓRIO TÉCNICO FOTOGRÁFICO</b>", estilo_titulo))
                    data_atual = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
                    
                    elementos.append(Paragraph(f"<b>Responsável Técnico:</b> {nome_usuario.upper()}", estilo_subtitulo))
                    elementos.append(Paragraph(f"<b>Data de Emissão:</b> {data_atual}", estilo_subtitulo))
                    elementos.append(HRFlowable(width="100%", thickness=1, color="#1E3A8A", spaceBefore=10, spaceAfter=20))
                    
                    # Processa Imagem
                    img_pil = PILImage.open(imagem_bytes)
                    largura_max = 440
                    w_percent = (largura_max / float(img_pil.size[0]))
                    h_size = int((float(img_pil.size[1]) * float(w_percent)))
                    
                    img_buffer = BytesIO()
                    img_pil.save(img_buffer, format="JPEG")
                    img_buffer.seek(0)
                    
                    pdf_img = Image(img_buffer, width=largura_max, height=h_size)
                    pdf_img.hAlign = 'CENTER'
                    elementos.append(pdf_img)
                    elementos.append(Spacer(1, 25))
                    
                    elementos.append(Paragraph("<b>1. Descrição dos Fatos Constatados:</b>", estilo_texto))
                    texto_final = texto_descricao if texto_descricao.strip() else "Nenhuma descrição detalhada foi fornecida."
                    elementos.append(Paragraph(texto_final, estilo_texto))
                    elementos.append(Spacer(1, 40))
                    
                    elementos.append(HRFlowable(width="40%", thickness=1, color="#A3A3A3", hAlign='CENTER', spaceAfter=5))
                    elementos.append(Paragraph(f"<b>{nome_usuario.upper()}</b>", estilo_assinatura))
                    elementos.append(Paragraph("Responsável pela Inspeção Fotográfica", estilo_assinatura))
                    
                    doc.build(elementos)
                    buffer.seek(0)
                    return buffer

                if st.button("⚙️ Compilar e Gerar PDF", use_container_width=True, type="primary"):
                    with st.spinner("Estruturando laudo e tratando imagem..."):
                        pdf_data = gerar_pdf(foto_capturada, descricao, nome_responsavel)
                        
                        st.download_button(
                            label="📥 DOWNLOAD DO RELATÓRIO PDF",
                            data=pdf_data,
                            file_name=f"laudo_{nome_responsavel.replace(' ', '_').lower()}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            else:
                st.info("⚠️ Para liberar a emissão do laudo, preencha o campo 'Nome Completo do Responsável'.")
        else:
            st.info("📸 Ative a câmera e capture uma foto ao lado para habilitar a geração do relatório.")