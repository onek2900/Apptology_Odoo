/** @odoo-module **/

import { debrandTranslation } from "./translation";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { WebClient } from "@web/webclient/webclient";

const { onMounted } = owl;
const components = { WebClient };

patch(components.WebClient.prototype, {
    setup() {
        super.setup();
        odoo.debranding_new_name = "";
        odoo.debranding_new_website = "";
        odoo.debranding_new_title = "";
        this.title.setParts({ zopenerp: odoo.debranding_new_title });
        this.orm = useService("orm");
        onMounted(() => {
            this.updateDebrandingValues();
        });
    },
    async updateDebrandingValues() {
        const result = await this.orm.call(
            "ir.config_parameter",
            "get_debranding_parameters"
        );
        odoo.debranding_new_name = result["apptology_debranding.new_name"];
        odoo.debranding_new_website = result["apptology_debranding.new_website"];
        odoo.debranding_new_title = result["apptology_debranding.new_title"];
        this.title.setParts({ zopenerp: odoo.debranding_new_title });
        debrandTranslation();
    },
});
