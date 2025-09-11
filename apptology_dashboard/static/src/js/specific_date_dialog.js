/**
 * Lightweight dialog wrapper to pick a single date and return
 * a [startOfDay, endOfDay] in the user timezone.
 *
 * Usage:
 *   const [dateFrom, dateTo] = await openSpecificDateDialog(env);
 */
import { registry } from "@web/core/registry";
import { DateTime } from "luxon";

export async function openSpecificDateDialog(env) {
    const dialog = registry.category("services").get("dialog");
    // Lazy-load the generic datepicker dialog from web if available.
    // In Odoo 17, use the generic Prompt with a date input as fallback.
    return new Promise((resolve, reject) => {
        const todayLocal = DateTime.local();
        const defaultISO = todayLocal.toISODate();

        const content = {
            title: env._t ? env._t("Select a date") : "Select a date",
            body: (
                `<div class="o_form_label">${env._t ? env._t("Date") : "Date"}</div>
                 <input class="o_input" type="date" value="${defaultISO}" style="width:100%" />`
            ),
            confirmLabel: env._t ? env._t("Apply") : "Apply",
            cancelLabel: env._t ? env._t("Cancel") : "Cancel",
        };

        const doOpen = dialog && dialog.add ? dialog.add : null;
        if (!doOpen) {
            // Fallback: no dialog service available
            const chosen = window.prompt("Enter date (YYYY-MM-DD)", defaultISO);
            if (!chosen) return reject();
            const start = DateTime.fromISO(chosen).startOf("day");
            const end = DateTime.fromISO(chosen).endOf("day");
            return resolve([start.toISO(), end.toISO()]);
        }

        // Simple custom dialog wrapper (HTML string) because some setups
        // don't expose a dedicated DatePicker dialog component in public API.
        const Dialog = require("@web/core/dialog/dialog").Dialog || null;
        if (Dialog) {
            doOpen(Dialog, {
                title: content.title,
                body: content.body,
                buttons: [
                    { text: content.cancelLabel, close: true },
                    {
                        text: content.confirmLabel,
                        classes: "btn-primary",
                        close: true,
                        click: (ev) => {
                            const input = ev.currentTarget.closest(".modal").querySelector("input[type='date']");
                            const val = input && input.value ? input.value : defaultISO;
                            const start = DateTime.fromISO(val).startOf("day");
                            const end = DateTime.fromISO(val).endOf("day");
                            resolve([start.toISO(), end.toISO()]);
                        },
                    },
                ],
            });
        } else {
            // Very old fallback: prompt
            const chosen = window.prompt("Enter date (YYYY-MM-DD)", defaultISO);
            if (!chosen) return reject();
            const start = DateTime.fromISO(chosen).startOf("day");
            const end = DateTime.fromISO(chosen).endOf("day");
            return resolve([start.toISO(), end.toISO()]);
        }
    });
}

