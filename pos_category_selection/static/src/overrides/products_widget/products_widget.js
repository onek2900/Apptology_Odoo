/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { patch } from "@web/core/utils/patch";
import { SelectCategory } from "../../components/select_category/select_category"
const { useState } = owl

ProductsWidget.components = { ...ProductsWidget.components, SelectCategory };
patch(ProductsWidget.prototype, {
    setup() {
        super.setup();
        this.pos.categorySelected=false
        this.pos.subcategorySelected=false
        this.pos.currentCategoryId=0
        this.state = useState({
            ...this.state,
            categorySelected: this.pos.categorySelected,
            subcategorySelected: this.pos.subcategorySelected,
            currentCategoryId: this.pos.currentCategoryId,
        });
    },

    onSelectCategory(selectedCategory) {
        this.pos.currentCategoryId = selectedCategory;
            if (selectedCategory === 0) {
            this.pos.categorySelected = true;
            this.pos.subcategorySelected = true;
            this.pos.setSelectedCategoryId(0);
            return;
        }
        const hasSubcategories = this.pos.db.get_category_childs_ids(selectedCategory).length > 0;

        if (hasSubcategories) {
            this.pos.categorySelected = true;
            this.pos.subcategorySelected = false;
        } else {
            this.pos.categorySelected = true;
            this.pos.subcategorySelected = true;
            this.pos.setSelectedCategoryId(selectedCategory);
        }
    },

    onSelectSubcategory(selectedCategory) {
        this.pos.subcategorySelected = true;
        this.pos.setSelectedCategoryId(selectedCategory);
    },
    onClickBack() {
        this.pos.searchProductWord=""
        const hasSubcategories = this.pos.db.get_category_childs_ids(this.pos.currentCategoryId).length > 0;
        if (!hasSubcategories || this.pos.currentCategoryId === 0) {
            this.pos.categorySelected = false;
            this.pos.subcategorySelected = false;
            this.pos.currentCategoryId = 0;
            this.pos.setSelectedCategoryId(0);
        } else if (this.pos.subcategorySelected) {
            this.pos.subcategorySelected = false;
        } else {
            this.pos.categorySelected = false;
            this.pos.currentCategoryId = 0;
            this.pos.setSelectedCategoryId(0);
        }
    },

    getShowCategoryImages() {
        return false;
    },

    get categorySelected() {
        return this.pos.categorySelected;
    },

    get subcategorySelected() {
        return this.pos.subcategorySelected;
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
        return this.pos.db.get_category_childs_ids(this.pos.currentCategoryId)
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
