from yel_utils import StrCommand

def run(options, din, dout):
    cmd = StrCommand("upper", options, din, dout)
    return cmd.run()
