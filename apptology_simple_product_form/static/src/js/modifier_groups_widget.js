/** @odoo-module */
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component, useEffect, useState } from "@odoo/owl";

class ModifierGroupsField extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ groups: [], toppingsById: {}, loading: false, expanded: {} });
        this._lastGroupKey = null; // track last applied group set to avoid loops
        this._cache = new Map(); // cache by groupKey -> { groups, toppingsById }
        this._debounce = null;
        // React only when groups change; avoid RPC on every toppings toggle
        useEffect(
            () => {
                if (this._debounce) clearTimeout(this._debounce);
                this._debounce = setTimeout(() => this.loadData(), 120);
                return () => this._debounce && clearTimeout(this._debounce);
            },
            () => [this._groupKey()]
        );
        console.log('modifier_groups: setup props', this.props);
    }

    get toppingsField() {
        // The toppings field can be passed via options; otherwise use canonical field
        return (this.props.options && this.props.options.toppings_field) || "sh_topping_ids";
    }

    get groupsField() {
        if (this.props.options && this.props.options.groups_field) {
            return this.props.options.groups_field;
        }
        if (this.props.record && this.props.record.fields && this.props.record.fields.sh_topping_group_ids) {
            return 'sh_topping_group_ids';
        }
        if (this.props.name && this.props.name !== 'sh_topping_ids') {
            return this.props.name;
        }
        return 'sh_topping_group_ids';
    }

    // Normalize many2many values into an array of ids regardless of shape
    asIds(val) {
        console.log('modifier_groups: asIds input', val);
        if (!val) {
            console.log('modifier_groups: asIds output', []);
            return [];
        }
        if (typeof val === "object" && !Array.isArray(val)) {
            if (Array.isArray(val.commands)) {
                const cmdResult = this.asIds(val.commands);
                console.log('modifier_groups: asIds output from commands', cmdResult);
                return cmdResult;
            }
            if (Array.isArray(val.resIds)) {
                const res = val.resIds.slice();
                console.log('modifier_groups: asIds output from resIds', res);
                return res;
            }
            if (Array.isArray(val.records)) {
                const res = val.records.map((r) => r.id);
                console.log('modifier_groups: asIds output from records', res);
                return res;
            }
            if ("id" in val && typeof val.id === "number") {
                console.log('modifier_groups: asIds output single id', [val.id]);
                return [val.id];
            }
        }
        if (Array.isArray(val)) {
            const ids = [];
            const ensureUniquePush = (value) => {
                if (typeof value === "number" && Number.isFinite(value) && !ids.includes(value)) {
                    ids.push(value);
                }
            };
            for (const entry of val) {
                if (entry == null) {
                    continue;
                }
                if (typeof entry === "number") {
                    ensureUniquePush(entry);
                    continue;
                }
                if (Array.isArray(entry) && entry.length) {
                    const [command, arg1, arg2] = entry;
                    switch (command) {
                        case 6:
                            ids.length = 0;
                            if (Array.isArray(arg2)) {
                                for (const id of arg2) ensureUniquePush(id);
                            }
                            break;
                        case 4:
                        case 1:
                        case 0:
                            if (typeof arg1 === "number") {
                                ensureUniquePush(arg1);
                            } else if (arg2 && typeof arg2.id === "number") {
                                ensureUniquePush(arg2.id);
                            }
                            break;
                        case 3:
                            if (typeof arg1 === "number") {
                                const idx = ids.indexOf(arg1);
                                if (idx !== -1) ids.splice(idx, 1);
                            }
                            break;
                        case 5:
                            ids.length = 0;
                            break;
                        default:
                            break;
                    }
                    continue;
                }
                if (typeof entry === "object" && typeof entry.id === "number") {
                    ensureUniquePush(entry.id);
                }
            }
            console.log('modifier_groups: asIds output from command list', ids);
            return ids;
        }
        console.log('modifier_groups: asIds output fallback', []);
        return [];
    }

    _groupKey() {
        const groupsVal = (this.props.record && this.props.record.data && this.props.record.data[this.groupsField]) || [];
        const ids = this.asIds(groupsVal).slice().sort((a, b) => a - b);
        return ids.join(",");
    }

    async loadData(force = false) {
        if (!this.props.record || !this.props.record.data) {
            console.log('modifier_groups: loadData skipped - no record yet', {
                force,
                hasRecord: !!this.props.record,
            });
            this.state.loading = false;
            return;
        }
        const groupsVal = this.props.record.data[this.groupsField] || [];
        const groupIds = this.asIds(groupsVal);
        const cacheKey = groupIds.slice().sort((a, b) => a - b).join(',');
        if (!force && cacheKey === this._lastGroupKey) {
            console.log('modifier_groups: loadData cached skip', { cacheKey, groupsField: this.groupsField });
            this.state.loading = false;
            return;
        }
        if (!groupIds.length) {
            console.log('modifier_groups: loadData skip (no groups)', {
                force,
                cacheKey,
                recordId: this.props.record.resId,
                groupsField: this.groupsField,
            });
            this.state.groups = [];
            this.state.toppingsById = {};
            this.state.expanded = {};
            this.state.loading = false;
            this._lastGroupKey = cacheKey;
            return;
        }
        this.state.loading = true;
        console.log('modifier_groups: loadData start', {
            force,
            cacheKey,
            groupIds,
            recordId: this.props.record.resId,
            groupsField: this.groupsField,
            rawGroupsVal: groupsVal,
        });
        try {
            let groups = [];
            let toppingsById = {};
            const cached = this._cache.get(cacheKey);
            if (cached && !force) {
                ({ groups, toppingsById } = cached);
            } else {
                if (groupIds.length) {
                    groups = await this.orm.searchRead(
                        "sh.topping.group",
                        [["id", "in", groupIds]],
                        ["name", "sequence", "toppinds_ids", "min", "max", "multi_max"]
                    );
                    const toppingIds = [...new Set(groups.flatMap((g) => g.toppinds_ids))];
                    if (toppingIds.length) {
                        const toppings = await this.orm.searchRead("product.product", [["id", "in", toppingIds]], ["name"]);
                        toppingsById = Object.fromEntries(toppings.map((t) => [t.id, t]));
                    }
                    // order groups by sequence then name
                    groups.sort((a, b) => (a.sequence ?? 0) - (b.sequence ?? 0) || a.name.localeCompare(b.name));
                }
                this._cache.set(cacheKey, { groups, toppingsById });
            }
            // preserve expanded states; default collapsed
            const prevExpanded = this.state.expanded || {};
            const expanded = {};
            for (const g of groups) {
                expanded[g.id] = Object.prototype.hasOwnProperty.call(prevExpanded, g.id)
                    ? prevExpanded[g.id]
                    : false;
            }
            this.state.groups = groups;
            this.state.toppingsById = toppingsById;
            this.state.expanded = expanded;
            // Auto-populate toppings from selected groups if missing
            if (!this.props.readonly && cacheKey !== this._lastGroupKey) {
                await this._ensureAutoPopulate(groups);
                this._lastGroupKey = cacheKey;
            }
        } catch (e) {
            console.error('modifier_groups: loadData error', e);
            this.notification.add(String(e.message || e), { type: "danger" });
        } finally {
            console.log('modifier_groups: loadData end', { cacheKey, groupIds, loading: this.state.loading });
            this.state.loading = false;
        }
    }

    get selectedToppingIds() {
        const field = this.toppingsField;
        const val = (this.props.record && this.props.record.data && this.props.record.data[field]) || [];
        return new Set(this.asIds(val));
    }

    isSelected(id) {
        return this.selectedToppingIds.has(id);
    }

    async toggleTopping(toppingId) {
        const selected = this.selectedToppingIds;
        if (selected.has(toppingId)) selected.delete(toppingId);
        else selected.add(toppingId);
        const ids = Array.from(selected);
        try {
            await this.props.record.update({ [this.toppingsField]: [[6, 0, ids]] });
        } catch (e) {
            this.notification.add(String(e.message || e), { type: "danger" });
        }
    }

    toggleGroup(id) {
        this.state.expanded[id] = !this.state.expanded[id];
        this.render(true);
    }

    // Template-safe handlers to preserve component context
    onToppingClick(toppingId) {
        if (this.props.readonly) {
            return;
        }
        return this.toggleTopping(toppingId);
    }

    async onRemoveGroup(groupId) {
        if (this.props.readonly) return;
        const groupsField = this.groupsField;
        const current = new Set(this.asIds(this.props.record.data[groupsField] || []));
        if (current.has(groupId)) {
            current.delete(groupId);
            // Also remove this group's toppings from selection
            const grp = (this.state.groups || []).find((g) => g.id === groupId);
            const selectedToppings = this.selectedToppingIds;
            if (grp) {
                for (const tid of grp.toppinds_ids) {
                    selectedToppings.delete(tid);
                }
            }
            await this.props.record.update({
                [groupsField]: [[6, 0, Array.from(current)]],
                [this.toppingsField]: [[6, 0, Array.from(selectedToppings)]],
            });
            await this.loadData();
        }
    }

    countSelectedInGroup(grp) {
        const selected = this.selectedToppingIds;
        let c = 0;
        for (const tid of grp.toppinds_ids || []) if (selected.has(tid)) c++;
        return c;
    }

    _normalizedLimit(value) {
        if (typeof value === 'number' && Number.isFinite(value)) {
            return value;
        }
        if (typeof value === 'string' && value.trim() !== '') {
            const parsed = parseInt(value, 10);
            return Number.isNaN(parsed) ? 0 : parsed;
        }
        return 0;
    }

    groupSelectionMeta(grp) {
        const selected = this.countSelectedInGroup(grp);
        const total = (grp.toppinds_ids || []).length;
        const min = this._normalizedLimit(grp.min);
        const max = this._normalizedLimit(grp.multi_max || grp.max);
        const requirementParts = [];
        if (min) requirementParts.push(`Min ${min}`);
        if (max) requirementParts.push(`Max ${max}`);
        let statusClass = 'text-muted';
        if (min && selected < min) {
            statusClass = 'text-warning';
        } else if (max && selected > max) {
            statusClass = 'text-danger';
        } else if (min || max) {
            statusClass = 'text-success';
        }
        return {
            selected,
            total,
            min,
            max,
            requirementText: requirementParts.join(', '),
            statusClass,
        };
    }

    async selectAllInGroup(groupId) {
        if (this.props.readonly) return;
        const grp = (this.state.groups || []).find((g) => g.id === groupId);
        if (!grp) return;
        const selected = this.selectedToppingIds;
        for (const tid of grp.toppinds_ids || []) selected.add(tid);
        await this.props.record.update({ [this.toppingsField]: [[6, 0, Array.from(selected)]] });
    }

    async clearGroup(groupId) {
        if (this.props.readonly) return;
        const grp = (this.state.groups || []).find((g) => g.id === groupId);
        if (!grp) return;
        const selected = this.selectedToppingIds;
        for (const tid of grp.toppinds_ids || []) selected.delete(tid);
        await this.props.record.update({ [this.toppingsField]: [[6, 0, Array.from(selected)]] });
    }

    async clearAllGroups() {
        if (this.props.readonly) return;
        await this.props.record.update({
            [this.groupsField]: [[6, 0, []]],
            [this.toppingsField]: [[6, 0, []]],
        });
        await this.loadData(true);
    }

    async _ensureAutoPopulate(groups) {
        try {
            // Union currently selected toppings with all toppings from groups
            const selected = this.selectedToppingIds;
            const beforeCount = selected.size;
            for (const g of groups || []) {
                for (const tid of g.toppinds_ids || []) {
                    selected.add(tid);
                }
            }
            if (selected.size > beforeCount) {
                await this.props.record.update({ [this.toppingsField]: [[6, 0, Array.from(selected)]] });
            }
        } catch (e) {
            this.notification.add(String(e.message || e), { type: "danger" });
        }
    }
}

ModifierGroupsField.template = "apptology_simple_product_form.ModifierGroupsField";
ModifierGroupsField.props = {
    ...standardFieldProps,
};

registry.category("fields").add("modifier_groups", {
    component: ModifierGroupsField,
    supportedTypes: ["many2many"],
});

