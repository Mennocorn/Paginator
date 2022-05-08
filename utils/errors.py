class Paginator(Exception):
    pass


class InvalidIndex(Paginator):
    pass


class NotAPage(Paginator):
    pass


class HelpCommandHandler(Exception):
    pass


class TooManyCommands(HelpCommandHandler):
    pass