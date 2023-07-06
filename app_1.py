import pickle
from pathlib import Path
import pandas as pd
import base64
from io import BytesIO
import openai
import streamlit as st


import streamlit_authenticator as stauth

st.set_page_config(page_title="POWER BI Reports", page_icon=": tada :", layout="wide", initial_sidebar_state="expanded")

names = ["Altug Gurgul", "Mehmet Ergan", "Yusuf Yavuzcan", "Ahmet Soyseven"]
usernames = ["agurgul", "mergan", "yyavuzcan", "asoyseven"]

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "report_page", "abcdef",
                                    cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Kullanıcı adı/parola yanlış")

if authentication_status:
#     openai.api_key = st.secrets["OPENAI_API_KEY"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.title("RAPOR SAYFASI")
    with col3:
        st.write("   ")
        st.image("datavadisi.png", width=200)
        st.write(pd.Timestamp('today').strftime("%d/%m/%Y"))

    ############ SIDEBAR
    authenticator.logout("Logout", "sidebar")
    st.sidebar.image("datavadisi.png", width=200)

    df = pd.read_excel("Raporadı.xlsx",index_col='No')

    tab1, tab2 = st.columns(2)
    openai.api_key = st.secrets["OPENAI_API_KEY"]


    options = st.sidebar.multiselect("Rapor Seçiniz",df['Rapor Index'].unique().tolist())




    with tab1:
        st.write('RAPORLAR')
        st.dataframe(df[df["Rapor Index"].isin(options)],
                       column_config={"Rapor Adı": "Rapor Adı", "Link": st.column_config.LinkColumn("Rapor Linki"),
                                      "Preview": st.column_config.ImageColumn("Image",
                                                                              help="Streamlit app preview screenshots")},height=500,width=800)
        # col2.metric("Rapor Sayısı",(int(df[df["Rapor Index"].isin(options)].shape[0])))
        col2.header(f":green[Hoşgeldin] :green[{name}]")

    with tab2:
        df_metrics = pd.read_excel("HR_Metrics_1.xlsx")
        st.write(f"METRİKLER **:red[{options}]**: {len(df_metrics[df_metrics['Baslık'].isin(options)])}")
        df_metrics.drop("Rapor Index", axis=1,inplace=True)
        st.dataframe(df_metrics[df_metrics["Baslık"].isin(options)],hide_index=True,width=800)
        df_metrics_ = df_metrics[df_metrics["Baslık"].isin(options)]


        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            format1 = workbook.add_format({'num_format': '0.00'})
            worksheet.set_column('A:A', None, format1)
            writer.close()
            processed_data = output.getvalue()
            return processed_data


        df_xlsx = to_excel(df_metrics_)
        st.download_button(label='📥 Download Current Result',
                           data=df_xlsx,
                           file_name='metrics.xlsx')


    tema= st.sidebar.radio("Rapor İsimler", df.loc[df["Rapor Index"].isin(options), "Rapor Adı"])

    clear_button = st.sidebar.button("Sohbeti Temizle", key="clear")

    if clear_button:
        st.session_state['generated'] = []
        st.session_state['past'] = []
        st.session_state['messages'] = [
            {"role": "system", "content": "Yardımcı asistanınız burada."}
        ]
        # st.session_state['number_tokens'] = []
        # st.session_state['model_name'] = []
        # st.session_state['cost'] = []
        # st.session_state['total_cost'] = 0.0
        # st.session_state['total_tokens'] = []
        # counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")


    with st.container():
        st.write("---")
        kol1,kol2 = st.columns(2)
        with kol1:
            # acıklama = df.loc[df["Rapor Adı"]== tema,"Rapor Adı"]
            st.header("SORULAR")

    with st.container():
        st.markdown("Lütfen Sorunuzu Yazınız")
        if tema not in st.session_state:

            # openai.api_key = st.secrets["OPENAI_API_KEY"]


            if "openai_model" not in st.session_state:
                st.session_state["openai_model"] = "gpt-3.5-turbo"

            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("What is up?"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    for response in openai.ChatCompletion.create(
                            model=st.session_state["openai_model"],
                            messages=[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages
                            ],
                            stream=True,
                    ):
                        full_response += response.choices[0].delta.get("content", "")
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})









