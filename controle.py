import streamlit as st
import pandas as pd

st.set_page_config(page_title="Controle Logístico", layout="centered")


# carregar estoque
estoque = pd.read_csv("estoque.csv")

st.title("📦 Controle Logístico Simples")
st.write("Sistema web para controle de pedidos, produção e estoque.")

st.subheader("⚠️ Alerta de Estoque Baixo")

limite = st.number_input(
    "Defina o limite mínimo de estoque",
    min_value=1,
    value=10
)

estoque_baixo = estoque[estoque["quantidade"] <= limite]

if estoque_baixo.empty:
    st.success("Nenhum produto com estoque baixo.")
else:
    st.warning("Produtos com estoque abaixo do limite:")
    st.dataframe(estoque_baixo)

# =========================
# CADASTRO DE PRODUTO
# =========================
st.subheader("➕ Cadastrar Novo Produto")

with st.form("cadastro_produto"):
    novo_produto = st.text_input("Nome do produto")
    categoria = st.text_input("Categoria")
    pedido_total = st.number_input("Pedido total", min_value=0, step=1)
    quantidade_inicial = st.number_input("Quantidade produzida (inicial)", min_value=0, step=1)
    cadastrar = st.form_submit_button("Cadastrar")

    if cadastrar:
        if novo_produto.strip() == "":
            st.warning("Informe o nome do produto.")
        elif novo_produto in estoque["produto"].values:
            st.error("Produto já cadastrado.")
        else:
            novo = pd.DataFrame({
                "produto": [novo_produto],
                "categoria": [categoria],
                "quantidade": [quantidade_inicial],
                "pedido_total": [pedido_total]
            })
            estoque = pd.concat([estoque, novo], ignore_index=True)
            estoque.to_csv("estoque.csv", index=False)
            st.success("Produto cadastrado com sucesso!")
            st.rerun()

# =========================
# CALCULAR FALTANTE
# =========================
estoque["faltante"] = estoque["pedido_total"] - estoque["quantidade"]

# =========================
# ESTOQUE / PRODUÇÃO
# =========================
st.subheader("📊 Controle de Produção e Pedidos")
st.dataframe(estoque)

# =========================
# MOVIMENTAÇÃO
# =========================
st.subheader("🔄 Registrar Produção (Entrada) ou Saída")

with st.form("movimentacao"):
    produto = st.selectbox("Produto", estoque["produto"])
    tipo = st.radio("Tipo", ["Produção (Entrada)", "Saída"])
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    enviar = st.form_submit_button("Registrar")

    if enviar:
        if tipo == "Produção (Entrada)":
            estoque.loc[estoque["produto"] == produto, "quantidade"] += quantidade
        else:
            estoque.loc[estoque["produto"] == produto, "quantidade"] -= quantidade

        estoque.to_csv("estoque.csv", index=False)
        st.success("Movimentação registrada com sucesso!")
        st.rerun()
        
        st.subheader("🗑️ Excluir Produto")

produto_excluir = st.selectbox(
    "Selecione o produto para excluir",
    estoque["produto"]
)

if st.button("Excluir produto"):
    estoque = estoque[estoque["produto"] != produto_excluir]
    estoque.to_csv("estoque.csv", index=False)
    st.success(f"Produto '{produto_excluir}' excluído com sucesso!")
    st.rerun()

# =========================
# GRÁFICO
# =========================
st.subheader("📈 Produção Atual x Pedido Total")
grafico = estoque.set_index("produto")[["quantidade", "pedido_total"]]
st.bar_chart(grafico)
