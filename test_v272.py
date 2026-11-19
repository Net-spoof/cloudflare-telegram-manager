"""v2.7.2: verify visible Telegram commands are the ones that the bot handles.

Runs offline without secrets, Telegram dependencies, or API requests.
"""
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace

source = Path(__file__).with_name("bot.py").read_text(encoding="utf-8")
tree = ast.parse(source)
top_level = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
assert "publish_bot_commands" in top_level
assert "main" in top_level
registered = [
    call.args[0].value
    for call in ast.walk(top_level["main"])
    if isinstance(call, ast.Call)
    and isinstance(call.func, ast.Name) and call.func.id == "CommandHandler"
    and len(call.args) >= 2 and isinstance(call.args[0], ast.Constant)
]
menu_assignment = next(
    n for n in tree.body
    if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "BOT_COMMAND_MENU" for t in n.targets)
)
menu = ast.literal_eval(menu_assignment.value)
menu_names = [name for name, _ in menu]
expected = ["start", "menu", "accounts", "about", "help", "cancel"]
assert registered == expected, registered
assert menu_names == expected, menu_names
assert "id" not in menu_names
assert all(1 <= len(description) <= 256 for _, description in menu)
assert all(1 <= len(name) <= 32 for name, _ in menu)

main_tree = top_level["main"]
assert any(
    isinstance(node, ast.Attribute) and node.attr == "post_init"
    and isinstance(node.value, ast.Call)
    for node in ast.walk(main_tree)
), "ApplicationBuilder.post_init(...) not configured"

class FakeCommand:
    def __init__(self, *, command, description):
        self.command, self.description = command, description

class PrivateScope:
    pass

calls = []
class FakeBot:
    def __init__(self, fail_default=False):
        self.fail_default = fail_default
    async def set_my_commands(self, commands, *, scope):
        calls.append(([(c.command, c.description) for c in commands], scope))
        if scope is None and self.fail_default:
            raise RuntimeError("simulated temporary Telegram error")

warnings = []
class FakeLog:
    def warning(self, *args):
        warnings.append(args)

ns = {
    "Application": object,
    "BotCommand": FakeCommand,
    "BotCommandScopeAllPrivateChats": PrivateScope,
    "BOT_COMMAND_MENU": menu,
    "log": FakeLog(),
}
selected = ast.Module(body=[top_level["publish_bot_commands"]], type_ignores=[])
exec(compile(selected, "bot_v272_extract.py", "exec"), ns)

async def tests():
    await ns["publish_bot_commands"](SimpleNamespace(bot=FakeBot()))
    assert len(calls) == 2
    assert calls[0][1] is None
    assert isinstance(calls[1][1], PrivateScope)
    assert [name for name, _ in calls[0][0]] == expected
    assert calls[0][0] == calls[1][0]
    calls.clear()
    await ns["publish_bot_commands"](SimpleNamespace(bot=FakeBot(fail_default=True)))
    assert len(calls) == 2, "Error in default scope must not block private scope"
    assert warnings and "simulated" not in str(warnings), "Warnings should not leak API details"

asyncio.run(tests())
print("PASS: six actual commands advertised in Telegram, obsolete /id removed, safe startup sync")
