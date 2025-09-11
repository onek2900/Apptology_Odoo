/**
 * Prompt a specific date and return [startOfDayISO, endOfDayISO]
 * in the user timezone. Minimal and safe outside Owl components.
 */
import { DateTime } from "luxon";

export async function openSpecificDateDialog() {
    const todayLocal = DateTime.local();
    const defaultISO = todayLocal.toISODate();
    const chosen = window.prompt("Enter date (YYYY-MM-DD)", defaultISO);
    if (!chosen) throw new Error("cancelled");
    const start = DateTime.fromISO(chosen).startOf("day");
    const end = DateTime.fromISO(chosen).endOf("day");
    return [start.toISO(), end.toISO()];
}

