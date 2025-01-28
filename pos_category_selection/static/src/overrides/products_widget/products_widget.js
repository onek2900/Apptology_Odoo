/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { patch } from "@web/core/utils/patch";
import { SelectCategory } from "../../components/select_category/select_category"
const { useState } = owl

ProductsWidget.components = { ...ProductsWidget.components, SelectCategory };
patch(ProductsWidget.prototype, {
    setup() {
        super.setup();
        this.state = useState({
            ...this.state,
            categorySelected: false,
            subcategorySelected: false,
            currentCategoryId: 0,
        });
    },

    onSelectCategory(selectedCategory) {
        this.state.currentCategoryId = selectedCategory;
        const hasSubcategories = this.pos.db.get_category_childs_ids(selectedCategory).length > 0;

        if (hasSubcategories) {
            this.state.categorySelected = true;
            this.state.subcategorySelected = false;
        } else {
            this.state.categorySelected = true;
            this.state.subcategorySelected = true;
            this.pos.setSelectedCategoryId(selectedCategory);
        }
    },


    onSelectSubcategory(selectedCategory) {
        this.state.subcategorySelected = true;
        this.pos.setSelectedCategoryId(selectedCategory);
    },

    onClickBack() {
        const hasSubcategories = this.pos.db.get_category_childs_ids(this.state.currentCategoryId).length > 0;

        if (!hasSubcategories) {
            this.state.categorySelected = false;
            this.state.subcategorySelected = false;
            this.state.currentCategoryId = 0;
            this.pos.setSelectedCategoryId(0);
        } else if (this.state.subcategorySelected) {
            this.state.subcategorySelected = false;
        } else {
            this.state.categorySelected = false;
            this.state.currentCategoryId = 0;
            this.pos.setSelectedCategoryId(0);
        }
    },

    getShowCategoryImages() {
        return false;
    },

    get categorySelected() {
        return this.state.categorySelected;
    },

    get subcategorySelected() {
        return this.state.subcategorySelected;
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
                return {
                    id: category.id,
                    name: !isRootCategory ? category.name : "",
                    imageUrl:
                        category?.has_image &&
                        `/web/image?model=pos.category&field=image_128&id=${category.id}&unique=${category.write_date}`,
                    hasChildren: this.pos.db.get_category_childs_ids(category.id).length > 0,
                };
            });
    },

    get subcategoriesForSelector() {
        return this.pos.db.get_category_childs_ids(this.state.currentCategoryId)
            .map((id) => this.pos.db.category_by_id[id])
            .map((category) => ({
                id: category.id,
                name: category.name,
                imageUrl:
                    category?.has_image &&
                    `/web/image?model=pos.category&field=image_128&id=${category.id}&unique=${category.write_date}`,
                hasChildren: this.pos.db.get_category_childs_ids(category.id).length > 0,
            }));
    },
});
