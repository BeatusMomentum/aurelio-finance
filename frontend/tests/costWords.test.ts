/* What the Portfolio table's "est.", "cost unknown" and "since situation"
   mean, said behind its "?" (brief AU; the words were the cells' tooltips).

   A cost is estimated when any unit behind it is: a photographed cost derived
   from a reported return, or a plan's buy at the market close. The words
   named the first source only until brief AI, so a position bought by a PAC
   said its price was derived from a reported return. Every expected value is
   written here. */

import assert from "node:assert/strict";
import { test } from "node:test";
import { COST_WORDS } from "../src/components/costWords.ts";

test("the question names the three marks the cells carry", () => {
  assert.equal(COST_WORDS.question, "What do est., cost unknown and since situation mean?");
});

test("an estimated price names both of its sources, and what that does to its P/L", () => {
  assert.ok(
    COST_WORDS.text.startsWith(
      "est.: the price paid is estimated in part. Some or all of it is a plan's buy priced at a market close, or a cost derived from a reported return, not a contract note, so the P/L against it is real but not verified.",
    ),
  );
});

test("an unknown cost: the recorded value is the situation's, and the P/L a movement, not a profit", () => {
  assert.ok(
    COST_WORDS.text.endsWith(
      " Cost unknown: no purchase price is on record. Recorded is then the value the situation was recorded at, not what you paid, and the P/L under it, marked since situation, is the movement since that situation, not a profit.",
    ),
  );
});
