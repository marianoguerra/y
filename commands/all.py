from yel_utils import InputCommand, is_truthy, PREDICATES

DEFAULT_PARAM = "are"

class Command(InputCommand):

    def on_start(self):
        filter_name = self.options.get("are", "true?")
        self.predicate = PREDICATES.get(filter_name, None)

        if self.predicate is None:
            self.error("Invalid predicate '{}'".format(filter_name), 404)
            self.end()

    def on_end(self):
        if not self.finish:
            self.printer(True)

    def on_data(self, data):
        if not self.predicate(data): 
            self.end()
            self.printer(False)

def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
