import streamlit as st
import gspread
from google.oauth2 import service_account
import datetime
import pandas as pd

st.set_page_config(page_title="My Finans", layout="centered", page_icon="💰")
st.title("📊 Моя финансовая витрина")

# 1. АВТОРИЗАЦИЯ
try:
    # Загружаем секреты из Streamlit Cloud
    info = st.secrets["gcp_service_account"]
    
    # Исправленные области видимости (scopes)
    scopes = [
        "https://googleapis.com",
        "https://googleapis.com"
    ]
    
    creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    client = gspread.authorize(creds)
    
    # 2. ОТКРЫТИЕ ТАБЛИЦЫ
    # Замените 'ВАШ_ID_ТАБЛИЦЫ' на реальный ID из адресной строки браузера
    SHEET_ID = "ВАШ_ID_ТАБЛИЦЫ" 
    sh = client.open_by_key(SHEET_ID)
    
    try:
        worksheet = sh.worksheet("ИСТОРИЯ")
    except:
        worksheet = sh.get_worksheet(0)
    
    st.success(f"✅ Связь установлена! Таблица: {sh.title}")

    # 3. ФОРМА ВВОДА
    with st.form("my_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        amount = col1.number_input("Сумма", min_value=0, step=100)
        category = col2.selectbox("Категория", ["Еда", "Транспорт", "Дом", "Досуг", "Доход", "Другое"])
        comment = st.text_input("Комментарий")
        
        submit = st.form_submit_button("Сохранить запись 🚀")
        
        if submit:
            if amount > 0:
                now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                worksheet.append_row([now, category, amount, comment])
                st.toast("Запись добавлена!", icon="🚀")
                st.rerun()
            else:
                st.warning("Введите сумму больше 0")

    # 4. ВЫВОД ТАБЛИЦЫ
    st.write("---")
    data = worksheet.get_all_records()
    if data:
        st.write("### Последние записи:")
        df = pd.DataFrame(data)
        # Показываем последние 10 записей (с конца)
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.info("В таблице пока нет данных.")

except Exception as e:
    st.error(f"❌ Критическая ошибка: {e}")
    
    if "404" in str(e):
        st.warning("Google не видит таблицу. Проверьте SHEET_ID.")
    
    # Выводим email сервисного аккаунта для удобства копирования
    try:
        sa_email = st.secrets["gcp_service_account"]["client_email"]
        st.info(f"Убедитесь, что дали доступ 'Editor' для: **{sa_email}**")
    except:
        st.info("Проверьте настройки st.secrets")
