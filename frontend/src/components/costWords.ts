/* What a position's average price and its P/L say about where its cost came
   from, on the Portfolio table (brief AI).

   A cost is estimated when any unit behind it is (`positions.replay` on the
   backend): a photographed cost derived from a reported return, or a plan's
   buy, which is priced at the market close and marked estimated until the
   reader corrects it. The words named the first source only, so a position
   bought by a PAC said its price was "derived from a reported return", and
   until brief AI it was not even marked.

   The cells say "est.", "cost unknown" and "since situation". What those
   words mean was a tooltip on every cell, which a phone never shows and a
   keyboard never reaches; it is said once, behind the table's "?" (brief AU).

   Pure, so `tests/costWords.test.ts` runs it under Node without a bundler;
   its shape is ui.tsx's `Explain`, written out so nothing here imports JSX. */

/** The Portfolio table's "?". */
export const COST_WORDS: { question: string; text: string } = {
  question: "What do est., cost unknown and since situation mean?",
  text:
    "est.: the price paid is estimated in part. Some or all of it is a plan's buy priced at a market close, or a cost derived from a reported return, not a contract note, so the P/L against it is real but not verified." +
    " Cost unknown: no purchase price is on record. Recorded is then the value the situation was recorded at, not what you paid, and the P/L under it, marked since situation, is the movement since that situation, not a profit.",
};
