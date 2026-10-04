import {describe, expect, it} from "vitest";

import {
    fromGregorianBillingPeriod,
    getCurrentGregorianBillingPeriod,
    toGregorianBillingPeriod,
} from "./buddhistBillingPeriod";

describe("Buddhist billing period conversion", () => {
  it("converts a Buddhist year to the Gregorian API period", () => {
    expect(toGregorianBillingPeriod(2569, 10)).toBe("2026-10");
  });

  it("converts a Gregorian API period to a Buddhist year", () => {
    expect(fromGregorianBillingPeriod("2026-10")).toEqual({
      year: 2569,
      month: 10,
    });
  });

  it("gets the default billing period from the local date", () => {
    expect(getCurrentGregorianBillingPeriod(new Date(2026, 9, 1))).toBe("2026-10");
  });
});
