import sqlalchemy as sa
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
import pandas as pd

import os
from dotenv import load_dotenv
import urllib

def getEngine():
    load_dotenv()
    ODBCSTR = os.getenv("ODBCSTR")
    sqlalchemy_str = "mssql+pyodbc:///?odbc_connect={}".format( urllib.parse.quote_plus(ODBCSTR))
    engine = sa.create_engine(sqlalchemy_str)
    return engine

def searchCustomer(engine, searchterm):
    select = text(f"""
        select top 100 cust.customerid , cust.lastname,gr.include_exclude_flag 
        from SalesLT.Customer cust 
        left outer join SalesLT.grouping gr on cust.customerid = gr.customerid
        where cust.lastname like '{searchterm}%'        
    """)
    session = sessionmaker(bind=engine)
    curSession = session()
    results = curSession.execute(select)
    data=[]
    for row in results:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        curRow={}
        for column, value in row.items():
            # build up the dictionary
            curField = {column: value}
            curRow.update(curField)
        data.append(curRow)

    return data

def buildInsert(customerid,include_exclude_flag):
    statement=f"INSERT INTO SalesLT.grouping(customerid,include_exclude_flag,my_timestamp) VALUES({customerid},'{include_exclude_flag}', getdate())"
    return statement
def buildUpdate(customerid,include_exclude_flag):
    statement=f"""UPDATE SalesLT.grouping set include_exclude_flag='{include_exclude_flag}',my_timestamp=getdate()
        WHERE customerid={customerid}"""
    return statement
def processDBOperation(engine,statement):
    try:
        conn = engine.raw_connection()
        conn.execute(statement)
        conn.commit()
        return ''
    except Exception as ex:
        print(ex)
        conn.connection.rollback()
        return str(ex)
# eng = getEngine()
# searchCustomer(eng,'l')