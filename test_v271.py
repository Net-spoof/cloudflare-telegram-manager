"""v2.7.1 offline regression tests for /accounts, /about and project credits.
No Telegram installation, credentials or network requests are required.
"""
import ast
import asyncio
import html
from pathlib import Path
from types import SimpleNamespace

source = Path(__file__).with_name('bot.py').read_text(encoding='utf-8')
tree = ast.parse(source)
names = {
    'accounts_view', 'accounts_menu', 'accounts_command',
    'about_view', 'about_command', 'help_command', 'callback',
}
selected = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names]
assert len(selected) == len(names), 'Missing a function required for account/about commands'

main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
handlers = {
    node.args[0].value: node.args[1].id
    for node in ast.walk(main)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    and node.func.id == 'CommandHandler' and len(node.args) >= 2
    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[1], ast.Name)
}
assert handlers['accounts'] == 'accounts_command'
assert handlers['about'] == 'about_command'
assert handlers['help'] == 'help_command'

class Button:
    def __init__(self, text, *args, callback_data=None, url=None, **kw):
        self.text, self.callback_data, self.url = text, callback_data, url
        if callback_data:
            assert len(callback_data.encode('utf-8')) <= 64

class Markup:
    def __init__(self, keyboard): self.inline_keyboard = keyboard

class Message:
    def __init__(self): self.sent = []
    async def reply_text(self, message, **kw):
        self.sent.append((message, kw))

class Query:
    def __init__(self, data=''):
        self.data, self.messages, self.answers = data, [], []
    async def answer(self, *args, **kw): self.answers.append((args, kw))
    async def edit_message_text(self, message, **kw): self.messages.append((message, kw))

accounts = [{'id': 1, 'label': '<my-account>', 'account_id': 'a'*32, 'active': 1}]
access = {'allowed': True, 'denied': 0}
async def deny(update): access['denied'] += 1
async def safe_edit(query, message, **kw): query.messages.append((message, kw))
async def ignored(*args, **kw): return None

ns = {
    'list_accounts': lambda: accounts,
    'InlineKeyboardButton': Button, 'InlineKeyboardMarkup': Markup,
    'esc': html.escape, 'short': lambda text, n=38: str(text)[:n],
    'ParseMode': SimpleNamespace(HTML='HTML'), 'VERSION': '2.7.1',
    'Update': object, 'ContextTypes': SimpleNamespace(DEFAULT_TYPE=object),
    'is_admin': lambda update: access['allowed'],
    'deny': deny, 'safe_edit': safe_edit,
    'decode_callback_data': lambda s: s,
    'is_private_chat': lambda update: True,
    'active_account': lambda: accounts[0] if accounts else None,
    'log': SimpleNamespace(exception=lambda *args, **kw: None),
    'show_main': ignored, 'guide_menu': ignored,
}
exec(compile(ast.Module(body=selected, type_ignores=[]), 'bot_v271_extract.py', 'exec'), ns)

async def run():
    msg = Message()
    update = SimpleNamespace(effective_message=msg)
    context = SimpleNamespace(user_data={'state': 'editing'})
    await ns['accounts_command'](update, context)
    assert not context.user_data
    text, kw = msg.sent[-1]
    assert '<b>حساب‌های Cloudflare</b>' in text
    assert '&lt;my-account&gt;' in text
    assert kw['parse_mode'] == 'HTML'
    assert any(btn.callback_data == 'acc:view:1' for row in kw['reply_markup'].inline_keyboard for btn in row)
    assert any(btn.callback_data == 'acc:add' for row in kw['reply_markup'].inline_keyboard for btn in row)

    q = Query()
    await ns['accounts_menu'](q)
    assert q.messages[-1][0] == text  # /accounts and inline button share the same UI

    accounts.clear()
    await ns['accounts_command'](update, context)
    assert 'هنوز حسابی متصل نشده' in msg.sent[-1][0]
    accounts.append({'id': 1, 'label': '<my-account>', 'account_id': 'a'*32, 'active': 1})

    await ns['about_command'](update, context)
    text, kw = msg.sent[-1]
    assert 'Net-spoof' in text and 'github.com/Net-spoof/cloudflare-telegram-manager' in text
    assert '@NET_SPOOF' in text
    assert kw['disable_web_page_preview'] is True
    urls = [b.url for row in kw['reply_markup'].inline_keyboard for b in row if b.url]
    assert 'https://github.com/Net-spoof' in urls
    assert 'https://github.com/Net-spoof/cloudflare-telegram-manager' in urls
    assert 'https://t.me/NET_SPOOF' in urls

    q = Query('about')
    await ns['callback'](SimpleNamespace(callback_query=q), SimpleNamespace(user_data={}))
    assert q.messages and q.messages[-1][0] == text

    await ns['help_command'](update, context)
    help_text = msg.sent[-1][0]
    assert '/accounts' in help_text and '/about' in help_text

    access['allowed'] = False
    old_count = len(msg.sent)
    await ns['accounts_command'](update, context)
    await ns['about_command'](update, context)
    assert len(msg.sent) == old_count and access['denied'] == 2

asyncio.run(run())
print('PASS: /accounts and /about commands, shared menus, GitHub/channel buttons, admin checks')
