/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { patch } from "@web/core/utils/patch";
import { SelectCategory } from "../../components/select_category/select_category"
const { useState } = owl

ProductsWidget.components = { ...ProductsWidget.components,  SelectCategory};
patch(ProductsWidget.prototype, {
    setup() {
        super.setup();
        this.state = useState({...this.state, categorySelected: false});
    },
    onSelectCategory(selectedCategory) {
        this.pos.setSelectedCategoryId(selectedCategory)
        this.state.categorySelected = true;
    },
    onClickBack () {
        this.state.categorySelected = false;
    },
    getShowCategoryImages () {
        return false
    },
    get categorySelected() {
        return this.state.categorySelected;
    },
    get categoriesForSelector() {
        return [
            ...this.pos.db.get_category_ancestors_ids(0),
            0,
            ...this.pos.db.get_category_childs_ids(0),
        ]
            .map((id) => this.pos.db.category_by_id[id])
            .map((category) => {
                const isRootCategory = category.id === this.pos.db.root_category_id;
                const showSeparator =
                    !isRootCategory &&
                    [
                        ...this.pos.db.get_category_ancestors_ids(this.pos.selectedCategoryId),
                        this.pos.selectedCategoryId,
                    ].includes(category.id);
                return {
                    id: category.id,
                    name: !isRootCategory ? category.name : "",
                    imageUrl:
                        category?.has_image &&
                        `/web/image?model=pos.category&field=image_128&id=${category.id}&unique=${category.write_date}`,
                };
            });
    }
})