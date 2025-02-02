/* @odoo-module */

//===========================================
//Quick Menu (main on off switch)
//===========================================

import { Component, useState, xml } from "@odoo/owl";
import { useModel } from "@web/model/model";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { jsonrpc } from "@web/core/network/rpc_service";
import { renderToFragment } from "@web/core/utils/render";
import { onWillStart } from "@odoo/owl";
import { useBus } from "@web/core/utils/hooks";


export class QuickMenuSh extends Component {
    static template = "quick.menu";

        setup() {
        	super.setup()
            this.orm = useService("orm");
            this.actionService = useService("action");
            this.action = this.props.action;
            this.model = this.props.model;
            this._search_def = $.Deferred();
            this.onWillStart()
            this.sh_enable_quick_menu_mode = session.sh_enable_quick_menu_mode
            self.quick_menus_html = []
            useBus(this.env.bus, 'SHROUTE_CHANGE', (ev) => this._checkBookmarkUrl(ev));

		}
		getURLParams(url) {
            const params = new URLSearchParams(url.split('?')[1].split('#')[1]);
            return {
                id: params.get('id'),
                menu_id: params.get('menu_id'),
                action: params.get('action'),
                view_type: params.get('view_type')
            };
        }

        compareURLs(url1, url2) {
            const params1 = this.getURLParams(url1);
            const params2 = this.getURLParams(url2);

            return params1.id === params2.id &&
                   params1.menu_id === params2.menu_id &&
                   params1.action === params2.action &&
                   params1.view_type === params2.view_type;
        }

        _checkBookmarkUrl(ev){
            
            const self = this
            const curr_url = ev?.detail?.url || window.location.href
            const curr_bookmark = self.quick_menus_html.filter((rec) => self.compareURLs(curr_url,rec.sh_url) )
            if (curr_bookmark.length > 0) {
                $('.o_main_navbar').find('.o_menu_systray').find('.sh_bookmark').addClass('active');
            } else {
                $('.o_main_navbar').find('.o_menu_systray').find('.sh_bookmark').removeClass('active');
            }
        }
		async render_quick_menulist_actions(quick_menus_html){

		    var self = this
		    var quick_menu_list_html = await renderToFragment(
                                            'quick.menulist.actions', {
                                             quick_menulist_actions: quick_menus_html,
                                             remove_quick_menu: function (ev){
                                                        self.remove_quick_menu(ev)},
                                             _onSearchResultsNavigate : function (ev){
                                                        self._onSearchResultsNavigate(ev)},
                                            });
                                            $(".sh_wqm_quick_menu_submenu_list_cls").html(quick_menu_list_html)
		    }

		async render_quick_menulist(quick_menus_html){

		    var self = this
		    var quick_menu_list_html = await renderToFragment(
                                            'quick.menulist', {
                                             quick_menulist_actions: quick_menus_html,
                                             remove_quick_menu: function (ev){
                                                        self.remove_quick_menu(ev)
                                                    },

                                            });
                                            $(".sh_wqm_quick_menu_submenu_list_cls").html(quick_menu_list_html)
		    }

		async render_quick_menulist_no_menu(){
		    
		    var final_quick_menu_list_html = renderToFragment(
                        'quick.menulist', {
                         no_menu: 1
                        });
                        $(".sh_wqm_quick_menu_submenu_list_cls").html(final_quick_menu_list_html)
		    }

		async onWillStart() {
            var self = this;
            
            await self.loadBookMarks()
            if (self.quick_menus_html.length > 0) {
                    if(self.quick_menus_html.length > 13){
                          this.render_quick_menulist_actions(self.quick_menus_html)
                    }else{
                        this.render_quick_menulist(self.quick_menus_html)
                    }
                }

            else {
                    this.render_quick_menulist_no_menu()
                }

		}
        async loadBookMarks(){
            
            this.quick_menus_html = await jsonrpc("/web/dataset/call_kw/sh.wqm.quick.menu/get_quick_menu_data", {
                    model: 'sh.wqm.quick.menu',
                    method: 'get_quick_menu_data',
                    args: ['', ['name', 'sh_url']],
                    kwargs: {
                      },
                });
            return this.quick_menus_html
        }

        open_quick_menu(e) {
            this.onWillStart()            
            
            $('.o_user_bookmark_menu').addClass('bookmark_active')
            if ($('.sh_wqm_quick_menu_submenu_list_cls').css('display') == 'none')
            {
                $('.sh_wqm_quick_menu_submenu_list_cls').css('display','revert')
            }else{
                $('.sh_wqm_quick_menu_submenu_list_cls').css('display','none')
                $('.o_user_bookmark_menu').removeClass('bookmark_active')
            }

            // close other popup
			$('.sh_user_language_list_cls').css("display","none")
			$('.todo_layout').removeClass("sh_theme_model");
			$('.sh_calc_util').removeClass("active")
			$(".sh_calc_results").html("");

        }

        async _searchData() {
            var query = $(".sh_bookmark_search").val();
            var self = this;
            var menus = await jsonrpc("/web/dataset/call_kw/sh.wqm.quick.menu/get_search_result", {
                    model: 'sh.wqm.quick.menu',
                    method: 'get_search_result',
                    args: [[query]],
                    kwargs:{ },
                });
                if (menus.length > 0) {
                      var self = this
                      var quick_menu_list_html = await renderToFragment(
                                        'quick.menulist', {
                                         quick_menulist_actions:menus,
                                         remove_quick_menu: function (ev){
                                                    self.remove_quick_menu(ev)
                                                },
                                        });
                                        $(".sh_search_result").html(quick_menu_list_html)
                } else {
                      self.render_quick_menulist_no_menu()
                }
        }

        _onSearchResultsNavigate(event) {
            this._search_def.reject();
            this._search_def = $.Deferred();
            setTimeout(this._search_def.resolve.bind(this._search_def), 50);
            this._search_def.done(this._searchData.bind(this));
        }

        async remove_quick_menu(e) {
            var self = this;
            var id = parseInt(e.target.dataset.id);
            if (id !== NaN) {
                var quick_menus_html = await jsonrpc("/web/dataset/call_kw/sh.wqm.quick.menu/remove_quick_menu_data", {
                    model: 'sh.wqm.quick.menu',
                    method: 'remove_quick_menu_data',
                    args: ['', id],
                    kwargs:{},
                }).then(function (res) {
                    if (res.id) {
                        if (window.location.href == res.sh_url) {
                            $('.sh_bookmark').removeClass('active')
                        }
                        if (res.final_quick_menu_list.length > 0) {
                            if(res.final_quick_menu_list.length > 13){
                                self.render_quick_menulist_actions(res.final_quick_menu_list)
                            }else{
                                self.render_quick_menulist(res.final_quick_menu_list)
                            }
                        } else {
                            self.render_quick_menulist_no_menu()
                        }
                    }
                });
            }
            return false;
        }

        getUrlVars() {
            var vars = [], hash;
            var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
            for (var i = 0; i < hashes.length; i++) {
                hash = hashes[i].split('=');
                vars.push(hash[0]);
                vars[hash[0]] = hash[1];
            }
            return vars;
        }

        getUrl() {
            return window.location.href;
        }

        async getMenuRecord() {

            var action_id = this.actionService.currentController.action.id

            var model = this.actionService.currentController.action.res_model
            if(!model){
                model = this.actionService.currentController.action.context.params.id
            }

            if (this.actionService.currentController.view.type == 'form') {
                var res_id = this.actionService.currentController.props.resId
            }
            var sh_url = this.getUrl()

            var self = this;

            var search_result = await jsonrpc("/web/dataset/call_kw/sh.wqm.quick.menu/set_quick_url", {
                    model: 'sh.wqm.quick.menu',
                    method: 'set_quick_url',
                    args: ['', sh_url, model, res_id, action_id],
                    kwargs: {
                      },
                });
            await this.loadBookMarks()
            return search_result
        }

        on_click(ev) {
            
            var self = this;
            this.getMenuRecord().then(function (rec) {

                $('.sh_bookmark').addClass('active')
                if (rec.is_set_quick_menu) {
                    if (rec.final_quick_menu_list.length > 0) {

                        if(rec.final_quick_menu_list.length > 13){
                            self.render_quick_menulist_actions(rec.final_quick_menu_list)
                        }else{
                            self.render_quick_menulist(rec.final_quick_menu_list)
                        }
                    } else {
                        self.render_quick_menulist_no_menu()
                    }


                } else {
                    $('.sh_bookmark').removeClass('active')
                    if (rec.final_quick_menu_list.length > 0) {
                        if(rec.final_quick_menu_list.length > 13){
                            self.render_quick_menulist_actions(rec.final_quick_menu_list)
                        }else{
                            self.render_quick_menulist(rec.final_quick_menu_list)

                        }

                    } else {
                        self.render_quick_menulist_no_menu()
                    }
                }
            });
        }
}

registry.category("systray").add("sh_entmate_theme.QuickMenuSh", { Component: QuickMenuSh }, { sequence: 25 });