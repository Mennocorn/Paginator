class Paginator(Exception):
    pass


class InvalidIndex(Paginator):
    pass


class NotAPage(Paginator):
    pass