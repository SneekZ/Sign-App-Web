import paramiko
from paramiko.ssh_exception import AuthenticationException, SSHException, NoValidConnectionsError
import logging
from datetime import datetime

from modules.get_ecp_password_from_db import get_passwords_by_snils
from SignParser import SignParser


class SshConnection:
    def __init__(self, data):
        _current_datetime = datetime.now()
        _current_datetime = _current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

        # # logging.basicConfig(
        #     filename=f"log/ssh/log_{_current_datetime}",
        #     level=# logging.DEBUG,
        #     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        # )

        self._data = data

        try:
            self._name = data["name"]
            self._host = data["host"]
            self._port = data["port"]
            self._user = data["user"]
            self._password = data["password"]
        except KeyError as e:
            print(f"Ошибка инициализации: {e}")
            # logging.error(msg)

        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self._connected = False

    def connect(self):
        try:
            self._client.connect(
                hostname=self._host,
                port=self._port,
                username=self._user,
                password=self._password
            )
            self._connected = True
            # logging.info(f"Подключено успешно к {self._name}")

        except AuthenticationException as auth_error:
            msg = f"Ошибка аутентификации: {auth_error}"
            # logging.error(msg)
            return msg
        
        except NoValidConnectionsError as conn_error:
            msg = f"Не удается подключиться к серверу: {conn_error}"
            # logging.error(msg)
            return msg
        
        except SSHException as ssh_error:
            msg = f"Ошибка SSH: {ssh_error}"
            # logging.error(msg)
            return msg
        
        except Exception as e:
            msg = f"Произошла непредвиденная ошибка: {e}"
            # logging.error(msg)
            return msg
        
    def _exec_command(self, command, ans=True):
        if self._connected:
            stdin, stdout, stderr = self._client.exec_command(command)
            # logging.info(f"Была выполнена команда {stdin.read().decode('utf-8')}")

            out = stdout.read().decode("utf-8", errors="replace").strip()
            err = stderr.read().decode("utf-8", errors="replace").strip()

            # out = stdout.read().decode("cp1251", errors="replace").strip()
            # err = stderr.read().decode("cp1251", errors="replace").strip()

            # print(f"{command}: out: {out}, err: {err}")

            if err:
                return err, False
            
            if out:
                self.parser = SignParser()
                error_code = self.parser.get_error_code(text=out)
                if error_code == "0x00000000":
                    return out, True
                else:
                    return out, False

            if not ans:
                return "Вроде выполнилась, хз вообще", True
            
        else:
            msg = "Клиент не был подключен"
            # logging.error(msg)
            return msg, False
    
    def get_signs(self, key=""):
        command = f"/opt/cprocsp/bin/amd64/certmgr -list -dn {key}" if key else "/opt/cprocsp/bin/amd64/certmgr -list"
        out, ok = self._exec_command(command)
        return out, ok
    
    def check_sign(self, snils):
        if not self._connected:
            msg = "Клиент не был подключен"
            # logging.error(msg)
            return msg, False

        command = "touch /home/converter/228.pdf"
        out, ok = self._exec_command(command, ans=False)
        # logging.info(f"Выполнена команда {command}")
        
        if not ok:
            msg = f"Ошибка при создании 228.pdf: {out}"
            # logging.error(msg)
            return msg, False
        
        passwords, ok = get_passwords_by_snils(self._data, snils)

        if not ok:
            return passwords, False

        errors = []

        for password in passwords:
            command = f'/opt/cprocsp/bin/amd64/cryptcp -signf -cert -nochain -dn="{snils}" /home/converter/228.pdf -pin "{password}"'
            out, ok = self._exec_command(command)
            # logging.info(f"Выполнена команда {command}")

            if ok:
                return [password, snils], True
            
            errors.append(out)
        
        if errors:
            from modules.error_codes import get_error
            for i in range(len(errors)):
                error_code = self.parser.get_error_code(text=errors[i])
                if error_code != "0x8010006b":
                    error = get_error(error_code)
                    return error, False
            error_code = self.parser.get_error_code(text=errors[-1])
            error = get_error(error_code)
            return error, False
            
        else:
            msg = "Не найдено ни одного пароля"
            # logging.error(msg)
            return msg, False


if __name__ == "__main__":
    data = {"name": "Гомоамогаома", "host": "dp68vm", "port": 22, "user": "root", "password": "shedF34A", "dbport": 3306, "dbuser": "dbuser", "dbpassword": "dbpassword", "database": "s11"}
    ssh = SshConnection(data)
    print(ssh.connect())
    print(ssh.check_sign(17060307733))