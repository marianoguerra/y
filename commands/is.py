from yel_utils import InputCommand, is_truthy, PREDICATES

class Command(InputCommand):

    def on_start(self):
        filter_name = self.options.get("value", "true?")
        self.predicate = PREDICATES.get(filter_name, None)

        if self.predicate is None:
            self.error("Invalid predicate '{}'".format(filter_name), 404)
            self.end()

    def on_data(self, data):
        self.printer(self.predicate(data))

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
