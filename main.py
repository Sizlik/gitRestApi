from datetime import datetime

from database import db

import json
import string
from random import choice

import requests
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory="templates")

symbols = string.ascii_letters + '0123456789'


@app.get('/')
def index(request: Request):
    session_id = request.cookies.get('session', None)
    response = templates.TemplateResponse('index.html', {'request': request})
    if not session_id:
        response.set_cookie(key="session", value=f"{''.join([choice(symbols) for x in range(15)])}")

    if db.get_by_session(session_id):
        return templates.TemplateResponse('menu.html', {'request': request})

    return response


@app.post('/not_auth')
def not_auth(request: Request, btn: str = Form(), owner: str = Form(), repo: str = Form()):
    return RedirectResponse('/' + btn + f'?owner={owner}&repo={repo}', )


@app.post('/login')
def auth(request: Request, key: str = Form(), owner: str = Form(), repo: str = Form()):
    headers = {'Authorization': f'Bearer {key}'} if len(key) > 10 else None
    data = requests.get(f'https://api.github.com/repos/{owner}/{repo}', headers=headers).json()

    if data.get('security_and_analysis', None):
        session = request.cookies.get('session', None)
        response = templates.TemplateResponse('suc.html', {'request': request})

        if not session:
            session = ''.join([choice(symbols) for x in range(15)])
            response.set_cookie(key='session', value=session)

        db.create_session(session, key, owner, repo)

        return response

    return templates.TemplateResponse('index.html', {'request': request, 'error': 'Не корректные данные'})


@app.post('/git_details')
def git_details(request: Request, owner=None, repo=None):
    session = request.cookies.get('session')
    data = db.get_by_session(session)
    if data:
        key = data[0]
        if not owner and not repo:
            owner = data[1]
            repo = data[2]

        headers = {'Authorization': f'Bearer {key}'}
    else:
        headers = None

    data = requests.get(f'https://api.github.com/repos/{owner}/{repo}', headers=headers).json()
    return data


@app.post('/git_pulls')
def git_pulls(request: Request, owner=None, repo=None):
    session = request.cookies.get('session')
    data = db.get_by_session(session)
    if data:
        key = data[0]
        if not owner and not repo:
            owner = data[1]
            repo = data[2]

        headers = {'Authorization': f'Bearer {key}'}
    else:
        headers = None

    data = requests.get(f'https://api.github.com/repos/{owner}/{repo}/pulls', headers=headers).json()
    return data


@app.post('/git_unused_pulls')
def git_unused_pulls(request: Request, owner=None, repo=None):
    session = request.cookies.get('session')
    data = db.get_by_session(session)
    if data:
        key = data[0]
        if not owner and not repo:
            owner = data[1]
            repo = data[2]

        headers = {'Authorization': f'Bearer {key}'}
    else:
        headers = None

    data = requests.get(f'https://api.github.com/repos/{owner}/{repo}/pulls', headers=headers).json()
    new_data = []

    time_now = datetime.now().timestamp()
    for i in data:
        if i['merged_at']:
            merged_time = datetime.strptime(i['merged_at'].split('T')[0], '%Y-%m-%d').timestamp() + 1209600
            if time_now - merged_time < 0:
                new_data.append(i)
        else:
            new_data.append(i)
    return new_data


@app.post('/git_issues')
def git_issues(request: Request, owner=None, repo=None):
    session = request.cookies.get('session')
    data = db.get_by_session(session)
    if data:
        key = data[0]
        if not owner and not repo:
            owner = data[1]
            repo = data[2]

        headers = {'Authorization': f'Bearer {key}'}
    else:
        headers = None

    data = requests.get(f'https://api.github.com/repos/{owner}/{repo}/issues', headers=headers).json()
    return data


@app.post('/git_forks')
def git_forks(request: Request, owner=None, repo=None):
    session = request.cookies.get('session')
    data = db.get_by_session(session)
    if data:
        key = data[0]
        if not owner and not repo:
            owner = data[1]
            repo = data[2]

        headers = {'Authorization': f'Bearer {key}'}
    else:
        headers = None

    data = requests.get(f'https://api.github.com/repos/{owner}/{repo}/forks', headers=headers).json()
    return data


@app.post('/logout')
def logout(request: Request):
    session = request.cookies.get('session')
    db.remove_by_session(session)
    response = templates.TemplateResponse('suc.html', {'request': request})
    return response
