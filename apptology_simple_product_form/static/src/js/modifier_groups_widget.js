/** @odoo-module */
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { useService } from "@web/core/utils/hooks";
import { Component, useEffect, useState } from "@odoo/owl";
import { selectCreate } from "@web/views/fields/relational_utils";

class ModifierGroupsField extends Component {
    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({ groups: [], toppingsById: {}, loading: false, expanded: {} });
        // Ensure we don't return the promise from loadData (which Owl would treat as a cleanup)
        useEffect(() => { this.loadData(); }, () => [this.props.value, this.props.record && this.props.record.data && this.props.record.data[this.groupsField]]);
    }

    get toppingsField() {
        return (this.props.options && this.props.options.toppings_field) || this.props.name || "tmpl_sh_topping_ids";
    }

    get groupsField() {
        // groups are provided via options or default field on template
        return (this.props.options && this.props.options.groups_field) || "tmpl_sh_topping_group_ids";
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

    async loadData() {
        // Prefer the bound field's live value (when this widget is on the groups field)
        const groupsVal = this.props.value || this.props.record.data[this.groupsField] || [];
        const groupIds = this.asIds(groupsVal);
        this.state.loading = true;
        let groups = [];
        let toppingsById = {};
        if (groupIds.length) {
            groups = await this.orm.searchRead(
                "sh.topping.group",
                [["id", "in", groupIds]],
                ["name", "sequence", "toppinds_ids"]
            );
        }
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
        this.state.groups = groups;
        this.state.toppingsById = toppingsById;
        this.state.expanded = expanded;
        this.state.loading = false;
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
        this.render();
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
            title: this.env._t("Add Toppings"),
            allowCreate: true,
            multiSelect: true,
        });
        if (result && result.resIds) {
            const newIds = Array.from(new Set([...(result.resIds || [])]));
            await this.orm.write("sh.topping.group", [groupId], { toppinds_ids: [[6, 0, newIds]] });
            await this.loadData();
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
