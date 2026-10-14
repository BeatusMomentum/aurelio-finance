/* The situation's one form: which fields each group shows, and the request a
   save sends.

   A situation page drew five forms, one per group (Stocks & ETF, Bonds,
   Commodities, Crypto, Other), the same ten controls five times: 35 fields on
   the page, and 1,103 characters of rules per form under the pointer (brief
   AU, measured). The only thing the five sent differently was the class of a
   new row. Now the group is chosen first, in one form, and the rules are said
   once, in words, under their fields.

   Read off the backend, the class decides the bucket a row is shown in, the
   allocation, the look-through's class by region grid and, for a coin, that
   its dividends are never asked about (`pac._follows_dividends`); nothing
   else reads it. So Commodities and Crypto show no ISIN and no dividend
   policy for a new row (the reader's choice, brief AU): the look-through
   cannot see inside a metal or a coin, and neither pays a dividend. A value
   already there, from a catalogue pick or the row being edited, is shown in
   any group: it is never hidden.

   No runtime imports beyond buckets.ts, so `npm test` reaches it. */

import type { HoldingCreate } from "../api/holdings";
import { classOnSave, type Bucket } from "./buckets.ts";

/** The fields some groups leave out. */
export type Optional = "isin" | "policy";

/** The groups, by the class a new row takes, that leave each field out. */
const LEFT_OUT: Record<Optional, readonly string[]> = {
  isin: ["commodity", "crypto"],
  policy: ["commodity", "crypto"],
};

/** Whether a group offers the field for a new row. */
export function offers(group: Bucket, field: Optional): boolean {
  return !LEFT_OUT[field].includes(group.cls);
}

/** Whether the field is shown: the group offers it, or it already holds a
    value (a pick, a row being edited), which is never hidden. */
export function shows(group: Bucket, field: Optional, value: string): boolean {
  return offers(group, field) || value.trim() !== "";
}

/** What the form holds when it is saved, as its boxes hold it. `currency` is
    the one the form shows: the reader's, or its proposal. */
export interface Draft {
  name: string;
  symbol: string;
  isin: string;
  cost: string;
  policy: string;
  mode: "total" | "qty";
  value: string;
  quantity: string;
  unitPrice: string;
  currency: string;
}

/** The request a save sends, field by field what each of the five forms sent:
    a new row takes its group's class, an edited one keeps its own (an ETF
    stays `fund_etf`). Entered as a total, no units and no price; as units
    and a price, no value, which the backend works out. */
export function holdingPayload(
  d: Draft,
  group: Bucket,
  editing: { asset_class?: string | null } | null,
): HoldingCreate {
  const shared = {
    asset_name: d.name.trim(),
    asset_class: classOnSave(group, editing),
    symbol: d.symbol.trim() || null,
    isin: d.isin.trim().toUpperCase() || null,
  };
  const rest = {
    cost_basis: d.cost ? Number(d.cost) : null,
    currency: d.currency,
    distribution_policy: d.policy || null,
  };
  return d.mode === "qty"
    ? { ...shared, quantity: Number(d.quantity), unit_price: Number(d.unitPrice), value: null, ...rest }
    : { ...shared, quantity: null, unit_price: null, value: Number(d.value), ...rest };
}
