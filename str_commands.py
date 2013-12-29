from yutil import *
COMMANDS = Commands()

fun_command(COMMANDS, "upper", str.upper)
fun_command(COMMANDS, "lower", str.lower)
fun_command(COMMANDS, "title", str.title)
fun_command(COMMANDS, "capitalize", str.capitalize)
fun_command(COMMANDS, "trim", str.strip)
fun_command(COMMANDS, "rtrim", str.rstrip)
fun_command(COMMANDS, "ltrim", str.lstrip)

@COMMANDS.command(name="starts-with")
def startswith(oin, env, value:EdnStrLike):
    return (obj.startswith(value) for obj in oin)

@COMMANDS.command(name="ends-with")
def endsswith(oin, env, value:EdnStrLike):
    return (obj.endswith(value) for obj in oin)
