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
def get_lpu_signs(id: int):
    service = LpuService()
    data, ok = service.get_lpu_data(id)
    if ok:
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
            error_code = parser.get_error_code(text=out)
            # print("parser.check_is_error: ", error_code)
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
        "error_msg": "service.get_lpu_data: " + data
    }


@app.get("/signs/{id}/check/{snils}/{casino}")
def check_sign(id: int, snils, casino: bool):
    service = LpuService()
    conn_data, ok = service.get_lpu_data(id)
    if ok:
        ssh = SshConnection(conn_data)
        connection_error = ssh.connect()
        if connection_error:
            return {
                "error_msg": "ssh.connect: " + connection_error
            }
        answer, ok = ssh.check_sign(snils, casino=casino)
        if not ok:
            if isinstance(answer, tuple):
                return {
                    "error_msg": "ssh.check_sign: " + answer[1],
                    "password": answer[0]
                }
            else:
                return {
                    "error_msg": "ssh.check_sign: " + answer
                }
        return {
            "error_msg": None,
            "password": answer[0],
            "snils": answer[1]
        }
    else:
        return {
            "error_msg": "service.get_lpu_data: " + conn_data
        }


@app.post("signs/{id}/delete/{thumbprint}")
def delete_sign(id: int, thumbprint):
    service = LpuService()
    conn_data, ok = service.get_lpu_data(id)
    if ok:
        ssh = SshConnection(conn_data)
        connection_error = ssh.connect()
        if connection_error:
            return {
                "error_msg": "ssh.connect: " + connection_error
            }
        answer, ok = ssh.delete_sign(thumbprint)
        if not ok:
            return {
                "error_msg": "ssh.delete_sign: " + answer
            }
        return {
            "error_msg": None,
            "answer": answer
        }
    else:
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
