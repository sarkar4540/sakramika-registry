import requests
from flask import Flask, request
from flask_cors import CORS
import sqlite3
import json

app = Flask(__name__)
CORS(app)
db_name = "datastore.db"

DATATYPE_INT = 0
DATATYPE_FLOAT = 1
DATATYPE_TEXT = 2
DATATYPE_STRUCTURE = 3


def setup():
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS UniformService(Id INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT, InputDataTypeId INT, OutputDataTypeId INT);")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS DataType(Id INTEGER PRIMARY KEY AUTOINCREMENT, Title TEXT, Base INT, Length INT);")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS SubDataType(Id INTEGER PRIMARY KEY AUTOINCREMENT, DataTypeId INT, Title INT, SubDataTypeId INT REFERENCES DataType(Id));")
    db.commit()
    db.close()


@app.route("/")
def hello_world():
    return "ok"


@app.route("/datatype")
def datatype():
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    datatypes = []
    for row in cur.execute("SELECT * FROM DataType;"):
        datatype = dict(zip(['id', 'title', 'base','length'], row))
        if datatype['base'] == DATATYPE_STRUCTURE:
            cur2 = db.cursor()
            datatype['subDataTypes'] = [dict(zip(['id', 'title', 'subDataTypeId'], row2)) for row2 in cur2.execute(
                "SELECT Id,Title,SubDataTypeId FROM SubDataType WHERE DataTypeId=?;", [datatype['id']])]
        datatypes.append(datatype)
    db.commit()
    db.close()
    return json.dumps(datatypes)


@app.route("/datatype/<id>", methods=["GET", "POST", "DELETE"])
def datatype_id(id):
    if request.method == "GET":
        db = sqlite3.connect(db_name)
        cur = db.cursor()
        datatype = None
        for row in cur.execute("SELECT * FROM DataType WHERE Id=?;", id):
            datatype = dict(zip(['id', 'title', 'base','length'], row))
            if datatype['base'] == DATATYPE_STRUCTURE:
                cur2 = db.cursor()
                datatype['subDataTypes'] = [dict(zip(['id', 'title', 'subDataTypeId'], row2)) for row2 in cur2.execute(
                    "SELECT Id,Title,SubDataTypeId FROM SubDataType WHERE DataTypeId=?;", [datatype['id']])]
        db.commit()
        db.close()
        return json.dumps(datatype)
    elif request.method == "POST":
        datatype = request.get_json(force=True)
        db = sqlite3.connect(db_name)
        cur = db.cursor()
        if int(id) == 0:
            cur.execute("INSERT INTO DataType (Title,Base,Length) VALUES (?,?,?);",
                        [datatype['title'], datatype['base'], datatype['length'] if 'length' in datatype else 0])
            datatype['id'] = cur.lastrowid
        else:
            cur.execute("UPDATE DataType SET Title=?,Base=?,Length=? WHERE Id=?;",
                        [datatype['title'], datatype['base'], datatype['length'] if 'length' in datatype else 0, id])
            datatype['id'] = id
            cur.execute("DELETE FROM SubDataType WHERE DataTypeId=?;",
                        [id])
        if int(datatype['base']) == DATATYPE_STRUCTURE:
            for i in range(len(datatype['subDataTypes'])):
                cur.execute("INSERT INTO SubDataType (Title,DataTypeId,SubDataTypeId) VALUES (?,?,?);", [
                            datatype['subDataTypes'][i]['title'], id, datatype['subDataTypes'][i]['subDataTypeId']])
                datatype['subDataTypes'][i]['id'] = cur.lastrowid
        db.commit()
        db.close()
        return json.dumps(datatype)
    elif request.method == "DELETE":
        db = sqlite3.connect(db_name)
        cur = db.cursor()
        cur.execute("DELETE FROM DataType WHERE Id=?;",
                    [id])
        cur.execute("DELETE FROM SubDataType WHERE DataTypeId=?;",
                    [id])
        datatype = {"id": id, "deleted": True}
        db.commit()
        db.close()
        return json.dumps(datatype)
    return "{error:'Invalid method'}"


@app.route("/uniformservice")
def uniformservice():
    db = sqlite3.connect(db_name)
    cur = db.cursor()
    uniformservice = []
    for row in cur.execute("SELECT * FROM UniformService;"):
        uniformservice.append(
            dict(zip(['id', 'title', 'inputDataTypeId', 'outputDataTypeId'], row)))
    db.commit()
    db.close()
    return json.dumps(uniformservice)


@app.route("/uniformservice/<id>", methods=["GET", "POST", "DELETE"])
def uniformservice_id(id):
    if request.method == "GET":
        db = sqlite3.connect(db_name)
        cur = db.cursor()
        uniformservice = None
        for row in cur.execute("SELECT * FROM UniformService WHERE Id=?;", id):
            uniformservice = dict(
                zip(['id', 'title', 'inputDataTypeId', 'outputDataTypeId'], row))
        db.commit()
        db.close()
        return json.dumps(uniformservice)
    elif request.method == "POST":
        service = request.get_json(force=True)
        db = sqlite3.connect(db_name)
        cur = db.cursor()
        if int(id) == 0:
            cur.execute("INSERT INTO UniformService (Title,InputDataTypeId,OutputDataTypeId) VALUES (?,?,?);",
                        [service['title'], service['inputDataTypeId'], service['outputDataTypeId']])
            service['id'] = cur.lastrowid
        else:
            cur.execute("UPDATE UniformService SET Title=?,InputDataTypeId=?,OutputDataTypeId=? WHERE id=?;",
                        [service['title'], service['inputDataTypeId'], service['outputDataTypeId'], id])
            service['id'] = id
        db.commit()
        db.close()
        return json.dumps(service)
    elif request.method == "DELETE":
        db = sqlite3.connect(db_name)
        cur = db.cursor()
        cur.execute("DELETE FROM UniformService WHERE Id=?;",
                    [id])
        service = {"id": id, "deleted": True}
        db.commit()
        db.close()
        return json.dumps(service)
    return "{error:'Invalid method'}"


@app.route("/sitemap")
def sitemap():
    routes = []
    i=0
    for r in app.url_map._rules:
        i=i+1
        routes.append([i,r.rule,",".join(list(r.methods))])
    return json.dumps(routes)

setup()

if __name__ == "__main__":
    app.run()
