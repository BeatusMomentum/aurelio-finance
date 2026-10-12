"""What a change to an account's cash moves, worked out and said once.

Brief AP (2026-10-12). The chat corrects and deletes a transfer
(`tools.change_transfer`), and the Cash flow page's Delete asks before it
deletes one. What either moves is worked out and said here, so the card and
the page's question cannot disagree: each account's cash today, before and
after, read by `analytics.compute_cash_position` with the change standing in
for the stored rows; the days whose figures change (`analytics.cash_changed`);
and when an account is left with no balance in force, what that does to every
total.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app import analytics, crud, dated, fx, models

# What the card and the page's question say first about a row that goes.
GONE = "It goes, and nothing brings it back."


@dataclass(frozen=True)
class Moved:
    """What a change does to one account's cash: its register today as stored
    (`now`) and with the change (`then`), as `compute_cash_position` reads
    them, and the spans of days whose figures change, each with whether no
    balance is in force there after the change."""

    account: models.Institution
    now: dict
    then: dict
    spans: list[tuple[datetime.date, datetime.date, bool]]


def moved(
    db: Session,
    account_ids: Iterable[int | None],
    since: str,
    *,
    transfers: list[models.Transfer] | None = None,
    anchors: dict[int, list[models.CashAnchor]] | None = None,
) -> list[Moved]:
    """What a change moves on each account it touches, in the order named, an
    outside side (None) left out: `transfers` stands for the transfers table
    with the change made, `anchors` for an account's balances with it made.
    Nothing before `since`, the change's earliest day, can move."""
    today = dated.today()
    on = datetime.date.fromisoformat(today)
    conv = fx.Converter(db, on=today)
    start = datetime.date.fromisoformat(since)
    out: list[Moved] = []
    for iid in dict.fromkeys(i for i in account_ids if i is not None):
        account = crud.get_institution(db, iid)
        if account is None:
            continue
        own = (anchors or {}).get(iid)
        now = analytics.compute_cash_position(db, iid, on, conv)
        then = analytics.compute_cash_position(db, iid, on, conv, transfers=transfers, anchors=own)
        spans = analytics.cash_changed(db, iid, start, on, conv, transfers=transfers, anchors=own)
        out.append(Moved(account, now, then, spans))
    return out


def _today(register: dict) -> str:
    if register["anchor_date"] is None:
        return "not projected, no balance"
    return f"{register['projected']:.2f} {register['base_currency']}"


def _moves_today(m: Moved) -> bool:
    return _today(m.now) != _today(m.then)


def lines(moves: list[Moved]) -> list[dict]:
    """Each account whose cash today moves, as a line of a card's diff."""
    return [
        {"field": f"Cash at {m.account.name} today", "now": _today(m.now), "proposed": _today(m.then)}
        for m in moves
        if _moves_today(m)
    ]


def _spans(m: Moved) -> str:
    """'from 2026-09-14 on', 'from 2026-09-14 to 2026-09-29, with no balance in
    force there', several joined by ', and'."""
    today = datetime.date.fromisoformat(dated.today())
    said = []
    for first, last, unanchored in m.spans:
        if last >= today:
            span = f"from {first.isoformat()} on"
        elif first == last:
            span = f"on {first.isoformat()}"
        else:
            span = f"from {first.isoformat()} to {last.isoformat()}"
        said.append(span + (", with no balance in force there" if unanchored else ""))
    return ", and ".join(said)


def account_said(
    m: Moved, days: Iterable[str], *, figures: bool, held: str = "already holds it"
) -> str:
    """One account's share of the change, in a sentence: from when its cash
    changes, and today's figures when `figures` (the page's question, which
    has no diff to show them in; the card shows them as lines). `days` are
    the days the change is dated on: when the account's latest balance comes
    on or after all of them, its cash today does not move, and `held` says
    why (a transfer it already holds; a balance it is the one after)."""
    name = m.account.name
    was, will = m.now["anchor_date"], m.then["anchor_date"]
    if was is None and will is None:
        return f"{name} has no balance on record, so no cash is projected from it."
    if will is None:
        return (
            f"{name} is then left with no balance: its cash is no longer projected, and every "
            f"total counts 0 for it where it counts {_today(m.now)} today."
        )
    spans = _spans(m)
    if _moves_today(m):
        said = f"{name}'s cash changes {spans}" if spans else f"{name}'s cash changes"
        if figures:
            said += f": today from {_today(m.now)} to {_today(m.then)}"
        if was is not None and will != was:
            said += f"; it then runs from its balance of {will.isoformat()}, with everything dated after it"
        return said + "."
    after_all = was is not None and all(d <= was.isoformat() for d in days)
    why = f": its latest balance, of {was.isoformat()}, {held}" if after_all else ""
    if spans:
        return f"{name}'s cash changes {spans}, and not today{why}."
    return f"{name}'s cash does not change{why}."


def said(
    moves: list[Moved], days: Iterable[str], *, figures: bool, held: str = "already holds it"
) -> list[str]:
    """Every account's sentence, in the order `moved` returned them."""
    days = list(days)
    return [account_said(m, days, figures=figures, held=held) for m in moves]


# --- A transfer ------------------------------------------------------------------


def transfer_moves(
    db: Session, transfer: models.Transfer, replaced_by: models.Transfer | None = None
) -> list[Moved]:
    """What correcting `transfer` into `replaced_by`, or deleting it (None),
    moves on every account either names."""
    table = [t for t in crud.get_transfers(db) if t.id != transfer.id]
    sides = [transfer.from_institution_id, transfer.to_institution_id]
    since = transfer.date
    if replaced_by is not None:
        table.append(replaced_by)
        sides += [replaced_by.from_institution_id, replaced_by.to_institution_id]
        since = min(since, replaced_by.date)
    return moved(db, sides, since, transfers=table)


def transfer_deletion(db: Session, transfer: models.Transfer) -> str:
    """What deleting a transfer does, as the Cash flow page asks it and the
    chat's card says it: the same words, with today's figures."""
    moves = transfer_moves(db, transfer)
    return " ".join([GONE, *said(moves, [transfer.date], figures=True)])
