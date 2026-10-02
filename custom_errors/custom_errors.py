class DomainErrors(Exception):
    pass


class DecreasingUnitError(DomainErrors):
    pass

class DoNotNegativeUnitError(DomainErrors):
    pass