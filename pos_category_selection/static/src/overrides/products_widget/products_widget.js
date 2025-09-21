/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { patch } from "@web/core/utils/patch";
import { SelectCategory } from "../../components/select_category/select_category";
const { useState } = owl;

const computeNonEmptyCategoryIds = (pos) => {
    const categoriesWithProducts = new Set();
    const productMap = pos?.db?.product_by_category_id || {};
    const categoryParent = pos?.db?.category_parent_id || {};

    const markWithAncestors = (categoryId) => {
        if (categoryId === undefined || categoryId === null) {
            return;
        }
        if (categoriesWithProducts.has(categoryId)) {
            return;
        }
        categoriesWithProducts.add(categoryId);
        const parentId = categoryParent[categoryId];
        if (parentId !== undefined && parentId !== categoryId) {
            markWithAncestors(parentId);
        }
    };

    for (const [categoryId, productIds] of Object.entries(productMap)) {
        const numericId = Number(categoryId);
        if (Number.isNaN(numericId)) {
            continue;
        }
        if (productIds && productIds.length) {
            markWithAncestors(numericId);
        }
    }

    return categoriesWithProducts;
};

const getNonEmptyChildIds = (pos, categoryId, nonEmptyCategoryIds) =>
    pos.db.get_category_childs_ids(categoryId).filter((id) => nonEmptyCategoryIds.has(id));

ProductsWidget.components = { ...ProductsWidget.components, SelectCategory };
patch(ProductsWidget.prototype, {
    setup() {
        super.setup();
        this.pos.categorySelected = false;
        this.pos.subcategorySelected = false;
        this.pos.currentCategoryId = 0;
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

        const nonEmptyCategoryIds = computeNonEmptyCategoryIds(this.pos);
        const childIds = getNonEmptyChildIds(this.pos, selectedCategory, nonEmptyCategoryIds);
        const hasSubcategories = childIds.length > 0;

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
        this.pos.searchProductWord = "";
        const nonEmptyCategoryIds = computeNonEmptyCategoryIds(this.pos);
        const childIds = getNonEmptyChildIds(this.pos, this.pos.currentCategoryId, nonEmptyCategoryIds);
        const hasSubcategories = childIds.length > 0;
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
        const nonEmptyCategoryIds = computeNonEmptyCategoryIds(this.pos);
        const rootCategoryId = this.pos.db.root_category_id;
        const candidateIds = [
            ...new Set([
                ...this.pos.db.get_category_ancestors_ids(rootCategoryId),
                rootCategoryId,
                ...getNonEmptyChildIds(this.pos, rootCategoryId, nonEmptyCategoryIds),
            ]),
        ].filter((id) => id === rootCategoryId || nonEmptyCategoryIds.has(id));

        return candidateIds
            .map((id) => this.pos.db.category_by_id[id])
            .filter(Boolean)
            .map((category) => {
                const isRootCategory = category.id === rootCategoryId;
                const childIds = getNonEmptyChildIds(this.pos, category.id, nonEmptyCategoryIds);
                return {
                    id: category.id,
                    name: !isRootCategory ? category.name : "",
                    imageUrl:
                        category?.has_image &&
                        `/web/image?model=pos.category&field=image_128&id=${category.id}&unique=${category.write_date}`,
                    hasChildren: childIds.length > 0,
                };
            });
    },

    get subcategoriesForSelector() {
        const nonEmptyCategoryIds = computeNonEmptyCategoryIds(this.pos);
        return getNonEmptyChildIds(this.pos, this.pos.currentCategoryId, nonEmptyCategoryIds)
            .map((id) => this.pos.db.category_by_id[id])
            .filter(Boolean)
            .map((category) => {
                const childIds = getNonEmptyChildIds(this.pos, category.id, nonEmptyCategoryIds);
                return {
                    id: category.id,
                    name: category.name,
                    imageUrl:
                        category?.has_image &&
                        `/web/image?model=pos.category&field=image_128&id=${category.id}&unique=${category.write_date}`,
                    hasChildren: childIds.length > 0,
                };
            });
    },
});
