import requests
from bs4 import BeautifulSoup
import urllib.parse
import json


class PAW:
    def __init__(self, username: str, password: str) -> None:
        self.username, self.password = username, password
        self.session = requests.Session()
        self._login()

    def upload_file(self, file, dist):
        session = self.session
        print(dist.rsplit('/', 1)[0])
        resp = session.get(
            f"https://www.pythonanywhere.com/user/{self.username}/files{dist.rsplit('/', 1)[0]}/")
        bs = BeautifulSoup(resp.content.decode(), 'html.parser')
        csrfmiddlewaretoken = bs.find(
            'input', {'type': 'hidden', 'name': 'csrfmiddlewaretoken'})['value']
        resp = session.post(f"https://www.pythonanywhere.com/user/{self.username}/files{dist.rsplit('/', 1)[0]}/", headers={
            'Host': "www.pythonanywhere.com",
            'Origin': "https://www.pythonanywhere.com",
            'Referer': f"https://www.pythonanywhere.com/user/{self.username}/files{dist.rsplit('/', 1)[0]}/",
        }, files={'file': open(file, 'rb')},
        data={
            'csrfmiddlewaretoken': csrfmiddlewaretoken
        }, allow_redirects=False)
        if resp.status_code != 302:
            raise Exception("can't upload file!")

    def reload_server(self):
        session = self.session
        resp = session.get(
            f"https://www.pythonanywhere.com/user/{self.username}/webapps/")
        bs = BeautifulSoup(resp.content.decode(), 'html.parser')
        csrfmiddlewaretoken = bs.find(
            'input', {'type': 'hidden', 'name': 'csrfmiddlewaretoken'})['value']
        session.cookies.set('web_app_tab_type', f"#id_{self.username}_pythonanywhere_com")
        resp = session.post(f"https://www.pythonanywhere.com/user/{self.username}/webapps/{self.username}.pythonanywhere.com/reload", headers={
            'Host': "www.pythonanywhere.com",
            'Origin': "https://www.pythonanywhere.com",
            'Referer': f"https://www.pythonanywhere.com/user/{self.username}/webapps/",
            'X-CSRFToken': csrfmiddlewaretoken,
            'X-Requested-With': "XMLHttpRequest"
        }).content.decode()
        if resp != 'OK':
            raise Exception("can't raload server!")

    def edit_file(self, filepath:str, data:bytes):
        session = self.session
        resp = session.get(
            f"https://www.pythonanywhere.com/user/{self.username}/files{filepath}?edit")
        bs = BeautifulSoup(resp.content.decode(), 'html.parser')
        csrfmiddlewaretoken = bs.find(
            'input', {'type': 'hidden', 'name': 'csrfmiddlewaretoken'})['value']
        resp = session.post(f"https://www.pythonanywhere.com/user/{self.username}/files{filepath}", headers={
            'Host': "www.pythonanywhere.com",
            'Origin': "https://www.pythonanywhere.com",
            'Referer': f"https://www.pythonanywhere.com/user/{self.username}/files{filepath}?edit",
            'X-CSRFToken': csrfmiddlewaretoken,
            'X-Requested-With': "XMLHttpRequest"
        }, data={
            'new_contents': data.decode()
        }).json()
        if not resp['success']:
            raise Exception("can't edit file!")

    def extend(self):
        session = self.session
        resp = session.get(
            f"https://www.pythonanywhere.com/user/{self.username}/webapps/#tab_id_{self.username}_pythonanywhere_com")
        bs = BeautifulSoup(resp.content.decode(), 'html.parser')
        csrfmiddlewaretoken = bs.find(
            'input', {'type': 'hidden', 'name': 'csrfmiddlewaretoken'})['value']
        session.cookies.set('web_app_tab_type',
                            f"#id_{self.username}_pythonanywhere_com")
        resp = session.post(f"https://www.pythonanywhere.com/user/{self.username}/webapps/{self.username}.pythonanywhere.com/extend", headers={
            'Host': "www.pythonanywhere.com",
            'Origin': "https://www.pythonanywhere.com",
            'Referer': f"https://www.pythonanywhere.com/user/{self.username}/webapps/",
        }, data={
            'csrfmiddlewaretoken': csrfmiddlewaretoken
        })
        if resp.status_code != 302:
            raise Exception("can't extend app!")

    def delete_server(self):
        session = self.session
        resp = session.get(
            f"https://www.pythonanywhere.com/user/{self.username}/webapps/#tab_id_{self.username}_pythonanywhere_com")
        bs = BeautifulSoup(resp.content.decode(), 'html.parser')
        csrfmiddlewaretoken = bs.find(
            'input', {'type': 'hidden', 'name': 'csrfmiddlewaretoken'})['value']
        session.cookies.set('web_app_tab_type',
                            f"#id_{self.username}_pythonanywhere_com")
        resp = session.post(f"https://www.pythonanywhere.com/user/{self.username}/webapps/{self.username}.pythonanywhere.com/delete", headers={
            'Host': "www.pythonanywhere.com",
            'Origin': "https://www.pythonanywhere.com",
            'Referer': f"https://www.pythonanywhere.com/user/{self.username}/webapps/",
        }, data={
            'csrfmiddlewaretoken': csrfmiddlewaretoken
        })

        if resp.status_code != 302:
            raise Exception("can't delete server!")

    def create_server(self, address="server/main.py"):
        session = self.session
        resp = session.get(
            f"https://www.pythonanywhere.com/user/{self.username}/webapps/")
        bs = BeautifulSoup(resp.content.decode(), 'html.parser')
        csrfmiddlewaretoken = bs.find(
            'input', {'type': 'hidden', 'name': 'csrfmiddlewaretoken'})['value']
        session.cookies.set('web_app_tab_type', "#tab_id_new_webapp_tab")
        resp = session.post(f"https://www.pythonanywhere.com/user/{self.username}/webapps/quickstart_new_flask_app", headers={
            'Host': "www.pythonanywhere.com",
            'Origin': "https://www.pythonanywhere.com",
            'Referer': f"https://www.pythonanywhere.com/user/{self.username}/webapps/",
            'X-CSRFToken': csrfmiddlewaretoken,
            'X-Requested-With': "XMLHttpRequest"
        }, data={
            'path': f"/home/{self.username}/{address}",
            'domain_name': f"{self.username}.pythonanywhere.com",
            'python_version': "python39"
        }).json()
        if resp['status'] == 'ERROR':
            raise Exception(resp['error_message'])

    def _login(self):
        session = self.session
        resp = session.get("https://www.pythonanywhere.com/login/?next=/")
        bs = BeautifulSoup(resp.content.decode(), "html.parser")
        form = bs.find('form', {'method': 'post'})
        data = {
            "csrfmiddlewaretoken": form.find("input", dict(type='hidden', name='csrfmiddlewaretoken'))['value'],
            "auth-username": self.username,
            "auth-password": self.password,
            "login_view-current_step": "auth",
        }
        resp = session.post("https://www.pythonanywhere.com/login/?next=/", data, allow_redirects=False, headers={
            'Host': "www.pythonanywhere.com",
            'Origin': "https://www.pythonanywhere.com",
            'Referer': "https://www.pythonanywhere.com/login/?next=/"
        })
        if resp.status_code != 302:
            bs = BeautifulSoup(resp.content.decode(), 'html.parser')
            raise Exception(bs.find('p', {'id': 'id_login_error'}).text)
