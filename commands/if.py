from yel_utils import InputCommand, get_key, eval_field, transform, StrSymbol

def replace_placeholder_with(value):
    def visitor(obj):
        if isinstance(obj, StrSymbol) and obj == "%":
            return value
        else:
            return obj

    return visitor

class Command(InputCommand):
    def on_start(self):
        self.cond = self.options.get('cond', True)
        self.then = self.options.get('then', None)
        self.else_ = self.options.get('else', None)

    def on_data(self, data):
        visitor = replace_placeholder_with(data)
        expanded_cond = transform(self.cond, visitor)
        cond_result = eval_field(expanded_cond, data, self.printer,
                self.error)

        print cond_result, type(cond_result)
        if cond_result:
            expanded_then = transform(self.then, visitor)
            result = eval_field(expanded_then, data, self.printer, self.error)
        else:
            expanded_else = transform(self.else_, visitor)
            result = eval_field(expanded_else, data, self.printer, self.error)

        self.printer(result)


def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
