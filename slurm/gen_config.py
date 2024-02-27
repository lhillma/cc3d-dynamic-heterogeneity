#!/usr/bin/env python
import argparse

import toml


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--set",
        metavar="KEY=VALUE",
        nargs="+",
        help="Set a number of key-value pairs to configure"
        "(do not put spaces before or after the = sign). "
        "If a value contains spaces, you should define "
        "it with double quotes: "
        'foo="this is a sentence". Note that '
        "values are always treated as strings.",
    )

    return parser.parse_args()


def parse_var(s):
    """
    Parse a key, value pair, separated by '='
    That's the reverse of ShellArgs.

    On the command line (argparse) a declaration will typically look like:
        foo=hello
    or
        foo="hello world"
    """
    items = s.split("=")
    key = items[0].strip()  # we remove blanks around keys, as is logical
    value = ""
    if len(items) > 1:
        # rejoin the rest:
        value = "=".join(items[1:])

    if key in ["sim.box_size", "sim.steps", "cell.diameter"]:
        value = int(value)
    else:
        value = float(value)
    key1, key2 = key.split(".")
    return (key1, key2, value)


def update_config(items, config):
    """
    Parse a series of key-value pairs and return a dictionary
    """
    if items:
        for item in items:
            key1, key2, value = parse_var(item)
            config[key1][key2] = value


def main():
    args = parse()

    default_config = {
        "sim": {
            "box_size": 200,
            "steps": 10000,
            "active_fraction": 0.5,
        },
        "cell": {
            "diameter": 40,
            "nucleus_size_ratio": 0.56,
            "propensity": 200,
        },
    }

    update_config(args.set, default_config)
    print(toml.dumps(default_config))


if __name__ == "__main__":
    main()
