export interface BuddhistBillingPeriod {
  year: number;
  month: number;
}

export function fromGregorianBillingPeriod(
  _period: string,
): BuddhistBillingPeriod {
  const match = /^(\d{4})-(0[1-9]|1[0-2])$/.exec(_period);
  if (!match || Number(match[1]) === 0) {
    throw new RangeError("Invalid Gregorian billing period");
  }

  return {
    year: Number(match[1]) + 543,
    month: Number(match[2]),
  };
}

export function toGregorianBillingPeriod(
  _buddhistYear: number,
  _month: number,
): string {
  if (
    !Number.isInteger(_buddhistYear) ||
    _buddhistYear < 544 ||
    _buddhistYear > 10542
  ) {
    throw new RangeError("Invalid Buddhist year");
  }
  if (!Number.isInteger(_month) || _month < 1 || _month > 12) {
    throw new RangeError("Invalid billing month");
  }

  return `${String(_buddhistYear - 543).padStart(4, "0")}-${String(_month).padStart(2, "0")}`;
}

export function getCurrentGregorianBillingPeriod(_now = new Date()): string {
  const year = _now.getFullYear();
  const month = _now.getMonth() + 1;
  return `${String(year).padStart(4, "0")}-${String(month).padStart(2, "0")}`;
}
