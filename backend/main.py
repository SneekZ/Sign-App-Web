from email import message_from_string
from pyexpat.errors import messages

import uvicorn
from fastapi import FastAPI, HTTPException
from LpuService import LpuService
from SshConnection import SshConnection
from SignParser import SignParser

app = FastAPI()


@app.get("/lpu")
def get_lpu_list():
    service = LpuService()
    data, ok = service.get_data()
    if ok:
        return {"lpudata": data}
    raise HTTPException(status_code=404)


@app.get("/signs/{id}")
def get_lpu_data(id: int):
    service = LpuService()
    conn_data, ok = service.get_lpu_data(id)
    if ok:
        titles = ["id", "name", "host", "port", "user", "password", "dbhost", "dbport", "dbuser", "dbpassword"]
        data = dict([(titles[i], conn_data[i]) for i in range(1, len(titles))])
        ssh = SshConnection(data)
        try:
            error_msg = ssh.connect()
            # print("ssh.connect: ", error_msg)
            if error_msg:
                return {
                    "error_msg": "ssh.connect: " + error_msg
                }
            out, ok = ssh.get_signs()
            # print("ssh.get_signs: ",  out)
            if not ok:
                return {
                    "error_msg": "ssh.get_signs: " + out
                }
            parser = SignParser()
            error_code = parser.get_error_code(out)
            # print("parser.check_is_error: ",  out)
            if parser.check_is_error(error_code):
                return {
                    "error_msg": "parser.check_is_error: " + out
                }
            error_msg = parser.parse(out)
            # print("parser.parse: ",  error_msg)
            if error_msg:
                return {
                    "error_msg": "parser.parse: " + error_msg
                }
            signs = parser.get_signs()
            return {
                "error_msg": None,
                "signs": signs
            }
        except Exception as e:
            return {
                "error_msg": "Exception: " + str(e)
            }
    return {
        "error_msg": "service.get_lpu_data: " + conn_data
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        host="192.168.0.67",
        port=52911
    )
