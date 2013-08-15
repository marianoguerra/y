from yel_utils import InputCommand, PREDICATES, is_not_nil, get_key

DEFAULT_PARAM = "is"

class Command(InputCommand):
    def on_start(self):
        filter_name = self.options.get("is", "not-nil?")
        self.key = self.options.get("key", None)
        self.value = self.options.get("value", None)
        self.predicate = PREDICATES.get(filter_name, is_not_nil)

    def on_data(self, data):
        if self.key:
            value = get_key(data, self.key, None)
        else:
            value = data

        if self.predicate(value, self.value):
            self.printer(data)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
