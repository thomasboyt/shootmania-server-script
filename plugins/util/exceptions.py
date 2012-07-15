class CommandDoesNotExist(Exception):
    pass


class UserDoesNotHavePermissions(Exception):
    pass


class ExpectedArg(Exception):
    pass


class MapNotFound(Exception):
    pass


class ModeNotFound(Exception):
    pass


class CouldNotConvertToApiType(Exception):
    pass