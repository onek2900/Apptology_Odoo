/** @odoo-module */
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component, useEffect, useState } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { selectCreate } from "@web/views/fields/relational_utils";

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
    }

    get toppingsField() {
        // The toppings field can be passed via options; otherwise use canonical field
        return (this.props.options && this.props.options.toppings_field) || "sh_topping_ids";
    }

    get groupsField() {
        // If not passed via options, assume the bound field is the groups field
        return (this.props.options && this.props.options.groups_field) || this.props.name || "sh_topping_group_ids";
    }

    // Normalize many2many values into an array of ids regardless of shape
    asIds(val) {
        if (!val) return [];
        if (Array.isArray(val)) return val.map((r) => (typeof r === "object" ? r.id : r)).filter((x) => !!x);
        if (val.resIds) return val.resIds;
        if (val.records) return val.records.map((r) => r.id);
        if (typeof val === "object" && "id" in val) return [val.id];
        return [];
    }

    _groupKey() {
        const groupsVal = (this.props.record && this.props.record.data && this.props.record.data[this.groupsField]) || [];
        const ids = this.asIds(groupsVal).slice().sort((a, b) => a - b);
        return ids.join(",");
    }

    async loadData(force = false) {
        const groupsVal = (this.props.record && this.props.record.data && this.props.record.data[this.groupsField]) || [];
        const groupIds = this.asIds(groupsVal);
        this.state.loading = true;
        let groups = [];
        let toppingsById = {};
        const cacheKey = groupIds.slice().sort((a, b) => a - b).join(",");
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
        this.state.loading = false;

        // Auto-populate toppings from selected groups if missing
        const groupKey = cacheKey;
        if (!this.props.readonly && groupKey !== this._lastGroupKey) {
            await this._ensureAutoPopulate(groups);
            this._lastGroupKey = groupKey;
        }
    }

    get selectedToppingIds() {
        const field = this.toppingsField;
        const val = this.props.record.data[field];
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

    async openAddToppingDialog(groupId) {
        if (this.props.readonly) return;
        const grp = (this.state.groups || []).find((g) => g.id === groupId);
        const existing = new Set(grp ? grp.toppinds_ids : []);
        const domain = [["available_in_pos", "=", true]];
        const result = await selectCreate(this, {
            resModel: "product.product",
            resIds: Array.from(existing),
            domain,
            context: this.props.record.context,
            title: _t("Add Toppings"),
            allowCreate: true,
            multiSelect: true,
        });
        if (result && result.resIds) {
            const newIds = Array.from(new Set([...(result.resIds || [])]));
            await this.orm.write("sh.topping.group", [groupId], { toppinds_ids: [[6, 0, newIds]] });
            await this.loadData(true);
        }
    }

    countSelectedInGroup(grp) {
        const selected = this.selectedToppingIds;
        let c = 0;
        for (const tid of grp.toppinds_ids || []) if (selected.has(tid)) c++;
        return c;
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

    async openAddGroupDialog() {
        if (this.props.readonly) return;
        const current = new Set(this.asIds(this.props.record.data[this.groupsField] || []));
        const result = await selectCreate(this, {
            resModel: "sh.topping.group",
            resIds: Array.from(current),
            domain: [],
            context: this.props.record.context,
            title: _t("Select Topping Groups"),
            allowCreate: true,
            multiSelect: true,
        });
        if (result && result.resIds) {
            const newIds = Array.from(new Set([...(result.resIds || [])]));
            await this.props.record.update({ [this.groupsField]: [[6, 0, newIds]] });
            await this.loadData(true);
        }
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
