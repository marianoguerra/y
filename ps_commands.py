import psutil
import yutil

COMMANDS = yutil.Commands()

def dictify(value):
    if hasattr(value, "_asdict"):
        return dictify(value._asdict())
    elif isinstance(value, dict):
        return {key: dictify(val) for key, val in value.items()}
    elif yutil.is_seq(value):
        return [dictify(item) for item in value]
    else:
        return value

@COMMANDS.command()
def ps(oin, env, state):
    for pid in psutil.get_pid_list():
        try:
            yield dictify(psutil.Process(pid).as_dict())
        except psutil.NoSuchProcess:
            pass
        except Exception:
            # TODO warn?
            pass

@COMMANDS.command("net-io")
def net_io(oin, env, state):
    for iface, item in psutil.net_io_counters(pernic=True).items():
        data = item._asdict()
        data["name"] = iface
        yield dictify(data)

@COMMANDS.command()
def users(oin, env, state):
    for item in psutil.get_users():
        yield dictify(item)

@COMMANDS.command()
def partitions(oin, env, state):
    for partition in psutil.disk_partitions():
        yield dictify(partition)

