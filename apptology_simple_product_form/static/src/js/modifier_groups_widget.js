/** @odoo-module */
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component, useEffect, useState } from "@odoo/owl";

class ModifierGroupsField extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ groups: [], allGroups: [], toppingsById: {}, loading: false, expanded: {} });
        // Ensure we don't return the promise from loadData (which Owl would treat as a cleanup)
        useEffect(() => { this.loadData(); }, () => [this.props.value]);
    }

    get toppingsField() {
        return (this.props.options && this.props.options.toppings_field) || "tmpl_sh_topping_ids";
    }

    async loadData() {
        const groupIds = (this.props.value || []).map((rec) => rec.id || rec);
        this.state.loading = true;
        let groups = [];
        let toppingsById = {};
        // Load all groups (limited) for selection chips
        const allGroups = await this.orm.searchRead(
            "sh.topping.group",
            [],
            ["name", "sequence", "toppinds_ids"],
            { limit: 200, order: "sequence,name" }
        );
        // Selected groups are a subset of allGroups
        groups = allGroups.filter((g) => groupIds.includes(g.id));
        const toppingIds = [...new Set(groups.flatMap((g) => g.toppinds_ids))];
        if (toppingIds.length) {
            const toppings = await this.orm.searchRead("product.product", [["id", "in", toppingIds]], ["name"]);
            toppingsById = Object.fromEntries(toppings.map((t) => [t.id, t]));
        }
        // order groups by sequence then name
        groups.sort((a, b) => (a.sequence ?? 0) - (b.sequence ?? 0) || a.name.localeCompare(b.name));
        // preserve expanded states; default collapsed
        const prevExpanded = this.state.expanded || {};
        const expanded = {};
        for (const g of groups) {
            expanded[g.id] = Object.prototype.hasOwnProperty.call(prevExpanded, g.id)
                ? prevExpanded[g.id]
                : false;
        }
        this.state.allGroups = allGroups;
        this.state.groups = groups;
        this.state.toppingsById = toppingsById;
        this.state.expanded = expanded;
        this.state.loading = false;
    }

    get selectedToppingIds() {
        const field = this.toppingsField;
        const val = this.props.record.data[field];
        return new Set((val || []).map((r) => r.id || r));
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
        this.render();
    }

    toggleGroup(id) {
        this.state.expanded[id] = !this.state.expanded[id];
        this.render(true);
    }

    async toggleGroupPick(groupId) {
        const currentIds = (this.props.value || []).map((rec) => rec.id || rec);
        const set = new Set(currentIds);
        if (set.has(groupId)) set.delete(groupId);
        else set.add(groupId);
        const newIds = Array.from(set);
        await this.props.record.update({ [this.props.name]: [[6, 0, newIds]] });
        await this.loadData();
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
