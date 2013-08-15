from yel_utils import InputCommand, is_map, is_seq, TaggedValue
import collections

def humanify(value):
    if value is None:
        return "n.a"
    elif isinstance(value, str):
        return value
    elif isinstance(value, TaggedValue):
        return value.to_human()
    elif is_seq(value):
        return " ".join([str(item) for item in value])
    else:
        return str(value)

def humanify_title(value):
    return value.replace("_", " ").replace("-", " ").title()

class Command(InputCommand):

    def __init__(self, options, din, dout):
        InputCommand.__init__(self, options, din, dout)
        self.accum = []

    def pprint(self):
        if not self.accum:
            return

        keys = self.accum[0].keys()
        human_rows = []
        human_titles = [humanify_title(key) for key in keys]
        col_max_len = [len(title) for title in human_titles]

        for data in self.accum:
            if is_map(data):
                values = [data.get(key) for key in keys]
                human_values = [humanify(field) for field in values]
                value_lengths = [len(value) for value in human_values]

                human_rows.append(human_values)

                col_max_len = map(max, zip(col_max_len, value_lengths))
            else:
                self.error("Expected Mapping, FIXME")

        titles_and_width = zip(human_titles, col_max_len)
        print("-+-".join("-" * width for width in col_max_len))
        print(" | ".join(col.ljust(width) for col, width in titles_and_width))
        print("-+-".join("-" * width for width in col_max_len))

        for row in human_rows:
            col_and_width = zip(row, col_max_len)
            print(" | ".join(col.ljust(width) for col, width in col_and_width))

    def on_end(self):
        self.pprint()

    def on_data(self, data):
        self.accum.append(data)

        if len(self.accum) > 23:
            self.pprint()


def run(options, din, dout):
    cmd = Command(options, din, dout)
    return cmd.run()
