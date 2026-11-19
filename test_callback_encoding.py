"""Offline regression tests for Telegram's callback_data <= 64-byte rule.

Tests the real functions extracted from bot.py; no network or credentials.
"""
import ast
import asyncio
import base64
from pathlib import Path
import re

source = Path(__file__).with_name('bot.py').read_text(encoding='utf8')
tree = ast.parse(source)
functions_to_test = {
    'encode_callback_data', 'decode_callback_data', 'InlineKeyboardButton',
    'record_menu', 'dns_menu', 'record_type_menu', 'zone_menu',
    'settings_menu', 'cache_menu', 'dnssec_menu', 'zone_info',
}
selected = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in functions_to_test]
assert len(selected) == len(functions_to_test), [f.name for f in selected]

created_buttons=[]

class TelegramInlineKeyboardButton:
    def __init__(self, text, *args, callback_data=None, **kwargs):
        self.text = text
        self.callback_data = callback_data
        if callback_data is not None:
            assert isinstance(callback_data, str), callback_data
            assert 1 <= len(callback_data.encode('utf-8')) <= 64, (len(callback_data.encode('utf-8')), callback_data)
        created_buttons.append(self)

class InlineKeyboardMarkup:
    def __init__(self, rows):
        self.inline_keyboard = rows

class FakeQuery:
    def __init__(self): self.menus=[]

async def safe_edit(q, content, **kwargs):
    q.menus.append((content, kwargs))

Z='a'*32
R='b'*32
OTHER_Z='0af23c45ee128a997a46ab32ff23da9c'
OTHER_R='f9f0aabb89c02025cb781d85ffc62936'

async def get_zone(z):
    assert z in (Z,OTHER_Z)
    return {'name':'example.com', 'status':'active','plan':{'name':'Free'}, 'id':z,'paused':False,'name_servers':['ns1.example.net']}

async def get_record(z,r):
    assert z in (Z,OTHER_Z) and r in (R,OTHER_R)
    return {'name':'api.example.com','type':'A','content':'1.1.1.1','id':r,'proxied':True,'proxiable':True,'ttl':1,'comment':'test'}

async def list_records(z):
    assert z in (Z,OTHER_Z)
    return [await get_record(z,r) for r in (R,OTHER_R)]

async def cf_request(a, method, path, **kwargs):
    if path.endswith('/dnssec'): return {'result':{'status':'active'}}
    if '/settings/' in path: return {'result':{'value':'on'}}
    return {'result':[]}

ns={'tr':lambda x:x,
    'base64':base64, 're':re,'_CF_HEX_ID':re.compile(r'(?<=:)[0-9a-fA-F]{32}(?=:|$)'),
    '_SHORT_CF_ID':re.compile(r'^~[A-Za-z0-9_-]{22}$'),
    'TelegramInlineKeyboardButton':TelegramInlineKeyboardButton,
    'InlineKeyboardMarkup':InlineKeyboardMarkup, 'safe_edit':safe_edit,
    'PAGE_SIZE':8, 'PROXY_TYPES':{'A','AAAA','CNAME'},
    'DNS_TYPES':['A','AAAA','CAA','CERT','CNAME','DNSKEY','DS','HTTPS','LOC','MX','NAPTR','NS','OPENPGPKEY','PTR','SMIMEA','SRV','SSHFP','SVCB','TLSA','TXT','URI'],
    'TYPE_GROUPS': [('⭐ رایج', ['A','AAAA','CNAME','TXT','MX','NS','PTR']),('🔐 امنیتی',['CAA','DS','DNSKEY','TLSA','SSHFP','SMIMEA','CERT','OPENPGPKEY']),('🧩 پیشرفته',['SRV','NAPTR','SVCB','HTTPS','URI','LOC'])],
    'ParseMode':type('ParseMode',(),{'HTML':'HTML'}),
    'get_zone':get_zone,'get_record':get_record,'list_records':list_records,'cf_request':cf_request,'active_account':lambda: {'account_id':'abc'},
    'esc':lambda v:str(v), 'short':lambda s,n=38: str(s)[:n],
    'record_label':lambda r: r['type'] + ' ' + r['name'],
}
exec(compile(ast.Module(body=selected,type_ignores=[]),'bot.py','exec'),ns)
encode=ns['encode_callback_data']; decode=ns['decode_callback_data']; btn=ns['InlineKeyboardButton']

# Previously these callbacks ranged from 69 to 79 bytes and were rejected.
actions=[
    f'rec:{Z}:{R}',f'rproxy:{Z}:{R}',f'rdeleteask:{Z}:{R}',f'rdelete:{Z}:{R}',
    *(f'redit:{f}:{Z}:{R}' for f in ('name','content','ttl','comment')),
    f'settoggle:{Z}:automatic_https_rewrites',
    f'dns:{Z}:999',f'zone:{Z}',f'rtypepage:{Z}:2',
]
for action in actions:
    wire=encode(action)
    assert len(wire.encode()) <= 64, (action,wire)
    assert decode(wire)==action, (action,wire)
    assert decode(action)==action
    b=btn('test', callback_data=action)
    assert b.callback_data == wire

assert decode(encode(f'rec:{OTHER_Z}:{OTHER_R}'))==f'rec:{OTHER_Z}:{OTHER_R}'
assert encode('noop')=='noop'
try:
    encode('long:'+'X'*100)
except ValueError: pass
else: raise AssertionError('Oversized callback must fail locally')

async def test_menus():
    for z,r in ((Z,R),(OTHER_Z,OTHER_R)):
        q=FakeQuery()
        await ns['zone_menu'](q,z)
        await ns['dns_menu'](q,z,0)
        await ns['record_menu'](q,z,r)
        await ns['settings_menu'](q,z)
        await ns['cache_menu'](q,z)
        await ns['dnssec_menu'](q,z)
        await ns['zone_info'](q,z)
        for idx in range(3): await ns['record_type_menu'](q,z,idx)
        assert len(q.menus)==10
        for _,kwargs in q.menus:
            for row in kwargs['reply_markup'].inline_keyboard:
                for b in row:
                    if b.callback_data:
                        assert len(b.callback_data.encode('utf8'))<=64
                        assert encode(decode(b.callback_data))==b.callback_data

asyncio.run(test_menus())
print(f'PASS: {len(created_buttons)} generated buttons; all within 64 bytes; reversible IDs; 10 live menus per zone.')
