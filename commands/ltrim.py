from yel_utils import StrCommand

def run(options, din, dout):
    cmd = StrCommand("lstrip", options, din, dout)
    return cmd.run()
