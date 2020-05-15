from discord.ext import commands


class Args:
    def __init__(self, args=[], options={}):
        self.args = args
        self.options = args

    def get_option(self, key: str):
        value = self.options.get(key)
        return value


class ArgParser(commands.Converter):
    def convert(self, ctx, args: tuple):
        args = []
        options = {}
        for arg in args:
            if not arg.startswith("--"):
                args.append(arg)
                continue

            if "=" not in arg:
                options[arg[3:]] = True
                continue

            split = arg.split("=")
            options[split[0]] = split[1]
        return Args(args, options)
