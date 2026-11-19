"""Offline regression tests. No Cloudflare/Telegram credentials used."""
import ast
import asyncio
import base64
import json
from pathlib import Path
from cryptography.fernet import Fernet

source = Path(__file__).with_name('bot.py').read_text()
tree = ast.parse(source)
fnames = {'normalize_cf_token', 'format_cf_errors', 'cf_request', 'verify_token_for_account', 'safe_edit', 'decrypt_token'}
functions = [x for x in tree.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)) and x.name in fnames]
assert len(functions) == len(fnames)

class BadRequest(Exception):
    pass

class Response:
    headers = {'content-type':'application/json'}
    status_code = 200
    is_error = False
    def json(self): return {'success':True,'result':[{'name':'example.com'}], 'errors':[]}

class Client:
    reqs=[]
    def __init__(self, **kwargs): pass
    async def __aenter__(self): return self
    async def __aexit__(self,*args): pass
    async def request(self,method,url,**kwargs):
        self.reqs.append(('request',method,url,kwargs['headers']))
        assert kwargs['headers']['Authorization'] == 'Bearer goodtoken'
        assert kwargs['headers'].get('Content-Type') == 'application/json'
        return Response()
    async def get(self,url,**kwargs):
        self.reqs.append(('get','GET',url,kwargs['headers']))
        assert kwargs['headers']['Authorization'] == 'Bearer goodtoken'
        assert kwargs['params']['account.id'] == 'accountid'
        return Response()

class Httpx:
    AsyncClient=Client

class Query:
    def __init__(self, bad=False): self.bad=bad; self.calls=[]
    async def edit_message_text(self,*a,**kw):
        self.calls.append((a,kw))
        if self.bad: raise BadRequest('Message is not modified: specified new message content and reply markup are exactly the same as a current content and reply markup of the message')
        return 'success'

cipher=Fernet(Fernet.generate_key())
namespace={'BadRequest':BadRequest,'httpx':Httpx,'FERNET':cipher,'InvalidToken':Exception,
           'CF_API':'https://api.cloudflare.com/client/v4'}
exec(compile(ast.Module(body=functions,type_ignores=[]),'bot-extracted','exec'),namespace)
normalize=namespace['normalize_cf_token']
for value in ('goodtoken','Bearer goodtoken','Bearer "goodtoken"','Authorization: Bearer goodtoken'):
    assert normalize(value)=='goodtoken'
assert normalize('cfut_new-tokenABC')=='cfut_new-tokenABC'
for value in ('','Bearer ','hello bad world','valid\ninvalid','cfk_abc'):
    try: normalize(value)
    except ValueError: pass
    else: raise AssertionError(value)

async def main():
    assert await namespace['safe_edit'](Query(),'Hi')=='success'
    assert await namespace['safe_edit'](Query(bad=True),'Hi') is None
    enc=cipher.encrypt(b'Authorization: Bearer goodtoken')
    result=await namespace['cf_request']({'token_enc':enc},'GET','/zones')
    assert result['success']
    assert await namespace['verify_token_for_account']('Bearer goodtoken','accountid')==1
    assert len(Client.reqs)==2

asyncio.run(main())
assert namespace['format_cf_errors']({'errors':[{'code':6003,'message':'Invalid request headers','error_chain':[{'code':6111,'message':'Invalid format for Authorization header'}]}]},400) == 'Invalid request headers (6003); Invalid format for Authorization header (6111)'
print('PASS: token cleaning, auth headers, nested errors, idempotent Telegram menu edits (no network)')
