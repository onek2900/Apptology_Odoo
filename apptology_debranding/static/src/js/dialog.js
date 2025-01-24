/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { patch } from "@web/core/utils/patch";

const component = { Dialog };

patch(component.Dialog.prototype, {
    setup() {
        const debranding_new_name = odoo.debranding_new_name;

        if (this.constructor.title && this.constructor.title.replace) {
            var title = this.constructor.title.replace(/Odoo/gi, debranding_new_name);
            this.constructor.title = title;
        } else {
            this.constructor.title = debranding_new_name;
        }

        super.setup();
    },
});
