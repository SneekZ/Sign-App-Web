from email import message_from_string
from pyexpat.errors import messages

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

from LpuService import LpuService
from SshConnection import SshConnection
from SignParser import SignParser

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",  # Если у вас есть фронтенд на другом порту
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/lpu")
def get_lpu_list():
    service = LpuService()
    data, ok = service.get_data()
    if ok:
        return {"lpudata": data,
                "error_msg": None
            }
    return {
        "error_msg": data
    }

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
            parser = SignParser(lpu_id=id)
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


@app.get("/signs/{id}/check_by_ids/{ids}")
def check_signs_by_id(id: int, ids: str):
    result_data = {
        "id": [],
        "snils": [],
        "result": [],
        "password": []
    }

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

            snilses, ok = ssh.get_snils_by_db_ids(ids)
            if not ok:
                return {
                    "error_msg": snilses
                }

            snilses, ids = snilses

            for snils, db_id in zip(snilses, ids):
                result_data["id"].append(db_id)
                result_data["snils"].append(snils)
                answer, ok = ssh.check_sign(snils, casino=False)
                if ok:
                    result_data["result"].append("OK")
                    result_data["password"].append(answer[0])
                else:
                    if isinstance(answer, tuple):
                        result_data["result"].append(answer[1])
                        result_data["password"].append(answer[0])
                    else:
                        result_data["result"].append(answer)
                        result_data["password"].append(None)

            df = pd.DataFrame(result_data)

            file_path = "output.xlsx"

            df.to_excel(file_path, index=False)
            return FileResponse(file_path,
                                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                filename="output.xlsx")

        except Exception as e:
            return {
                "error_msg": "Exception: " + str(e)
            }
    return {
        "error_msg": "service.get_lpu_data: " + data
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
        host="localhost",
        port=52911
    )
