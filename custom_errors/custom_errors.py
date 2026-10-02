class DomainErrors(Exception):
    pass


class DecreasingUnitError(DomainErrors):
    pass

class DoNotNegativeUnitError(DomainErrors):
    pass


class InvalidBillingPeriodError(DomainErrors):
    pass


class InvalidPricingError(DomainErrors):
    pass


class InvalidTenantError(DomainErrors):
    pass


class InvalidRoomError(DomainErrors):
    pass


class InvalidRentRateError(DomainErrors):
    pass


class InvalidBillItemError(DomainErrors):
    pass


class DuplicateBillItemError(DomainErrors):
    pass


class MissingRequiredDataError(DomainErrors):
    pass