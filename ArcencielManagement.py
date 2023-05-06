import streamlit as sl
from streamlit_router import StreamlitRouter
import sqlite3
import uuid
from datetime import date

def wasteForm():
    sqlConnection = sqlite3.connect("FYPDatabase.db", check_same_thread=False)
    cursor = sqlConnection.cursor()
    hospitalsQuery = cursor.execute("SELECT * FROM Hospital")
    hospitals = hospitalsQuery.fetchall()

    col1, col2, col3 = sl.columns(3, gap="small")
    with col2:
        arcencielLogo = sl.image("Logo.jpg", width=275)

    sl.selectbox("Hospital", hospitals, format_func=lambda hospital: hospital[1], key="hospitalSelection")
    sl.number_input('Worker ID', step=1, min_value=0, key="workerID")
    sl.number_input('Truck Number', value=0, step=1, min_value=0, key="truckNumber")
    sl.date_input("Date of Collection", key="date")
    sl.number_input("Amount Collected (in Kg)", min_value=0, key="amountCollected")

    col1, col2, col3, col4, col5, col6, col7 = sl.columns(7, gap="small")

    def submit():
        selectedHospitalId = sl.session_state["hospitalSelection"][0]
        workerId = sl.session_state["workerID"]
        truckNumber = sl.session_state["truckNumber"]
        date = sl.session_state["date"]
        amountCollected = sl.session_state["amountCollected"]

        id = uuid.uuid1()
        insertWasteBatchQuery = cursor.execute(
            f"INSERT INTO WasteBatch(batchNo,hospitalID,batchWeight) VALUES('{id}','{selectedHospitalId}','{amountCollected}')")
        insertWorkerWasteBatchQuery = cursor.execute(
            f"INSERT INTO WorkerWasteBatch(workerID,batchNo,collectionDate) VALUES('{workerId}','{id}','{date}')")
        sqlConnection.commit()
        sqlConnection.close()
        router.redirect(*router.build("index"))

    def reset():
        sl.session_state["hospitalSelection"] = hospitals[0]
        sl.session_state["workerID"] = 0
        sl.session_state["truckNumber"] = 0
        sl.session_state["date"] = date.today()
        sl.session_state["amountCollected"] = 0

    with col5:
        if sl.button("Home"):
            router.redirect(*router.build("index"))

    with col6:
        submitButton = sl.button("Submit", on_click=submit)

    with col7:
        resetButton = sl.button("Reset", on_click=reset)

def hospitalInvoice():
    sqlConnection = sqlite3.connect("FYPDatabase.db", check_same_thread=False)
    cursor = sqlConnection.cursor()
    hospitalsQuery = cursor.execute("SELECT * FROM Hospital")
    hospitals = hospitalsQuery.fetchall()

    col1, col2, col3 = sl.columns(3, gap="small")
    with col2:
        arcencielLogo = sl.image("Logo.jpg", width=275)

    sl.selectbox("Hospital", hospitals, format_func=lambda hospital: hospital[1], key="hospitalSelection")
    sl.date_input("Date of Collection", key="date")

    col1, col2, col3, col4, col5, col6, col7 = sl.columns(7)

    def submit():
        selectedHospitalId = sl.session_state["hospitalSelection"][0]
        date = sl.session_state["date"]
        year = date.year
        month = date.month
        formattedMonth = f"{month:02d}"
        query = f'''
        SELECT sum(WasteBatch.batchWeight), Hospital.hospitalName, strftime("%m-%Y", workerWasteBatch.collectionDate) as 'month-year' 
        FROM WasteBatch, Hospital, WorkerWasteBatch
        Where WasteBatch.hospitalID= HOSPITAL.hospitalID
        AND HOSPITAL.hospitalID = {selectedHospitalId}
        AND strftime("%m-%Y", workerWasteBatch.collectionDate) = '{formattedMonth}-{year}'
        AND workerwastebatch.batchNo=wastebatch.batchNo
        GROUP BY
            strftime("%m-%Y", workerWasteBatch.collectionDate )
      '''
        cursor.execute(query)
        rows = cursor.fetchall()
        if len(rows) == 0:
            sl.success(f"No waste was collected from this hospital during this month.")
        else:
            sl.success(f"Amount of waste collected = {rows[0][0]} Kg\n\rInvoice = {rows[0][0] * 0.22} $")
        sqlConnection.close()
        router.redirect(*router.build("index"))
    with col6:
        if sl.button("Home"):
            router.redirect(*router.build("index"))
    with col7:
        submitButton = sl.button("Submit", on_click=submit)

def index(router):

    if sl.button("Waste Form"):
        router.redirect(*router.build("wasteForm"))
    if sl.button("Hospital Invoice"):
        router.redirect(*router.build("hospitalInvoice"))


router = StreamlitRouter()
router.register(index, '/')
router.register(wasteForm, "/wasteForm")
router.register(hospitalInvoice, "/tasks")


router.serve()