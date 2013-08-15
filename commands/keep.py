from yel_utils import InputCommand, PREDICATES, get_key, is_eq, unwrap

DEFAULT_PARAM = "is"

class Command(InputCommand):

    def on_data(self, data):
        for field, value in self.options.items():
            if isinstance(value, list) and len(value) == 2 and value[0] in PREDICATES:
                pred_name = value[0]
                predicate = PREDICATES[pred_name]
                comparison = value[1]

            else:
                pred_name = "eq"
                predicate = is_eq
                comparison = value

            val = get_key(data, field, None)
            if not predicate(unwrap(val), comparison):
                return

        self.printer(data)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
