#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
version: python 3+
adminviews.py defines the AdminIndexView and all ModelViews
Dani van Enk, 11823526

references:
    https://flask-admin.readthedocs.io/en/v1.0.4/quickstart/
    https://flask-admin.readthedocs.io/en/latest/api/mod_model/
    https://flask-admin.readthedocs.io/en/latest/api/mod_contrib_sqla/
"""

# used imports
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask import redirect, url_for
from flask_login import current_user
from wtforms.validators import ValidationError


class AdminUserIndexView(AdminIndexView):
    """
    Here the AdminUserIndexView class is defined
        it's based on the AdminIndexView class

    expose:
        index ("/") - renders the homepage of the admin part of the site;

    methods:
        is_accessible           - returns if current_user is admin;
        inaccessible_callback   - redirects to site index if inaccessible
    """

    @expose("/")
    def index(self):
        """
        defines the index template for the admin part of the site

        expose:
            - "/"
        """

        return self.render("admin/index.html", user=current_user)

    def is_accessible(self):
        """
        check if current_user is admin, return true if so else false
        """

        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        """
        redirect to site home if user isn't admin
        """

        return redirect(url_for('index'))


class AdminView(ModelView):
    """
    Here the AdminView class is defined
        it's based on the ModelView class

    methods:
        is_accessible           - returns if current_user is admin;
        inaccessible_callback   - redirects to site index if inaccessible
    """

    # excludes from columns and forms
    column_exclude_list = ["password"]
    form_exclude_columns = ["Order"]

    def is_accessible(self):
        """
        check if current_user is admin, return true if so else false
        """

        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        """
        redirect to site home if user isn't admin
        """

        return redirect(url_for('index'))


class MenuView(ModelView):
    """
    Here the MenuView class is defined
        it's based on the ModelView class

    methods:
        is_accessible           - returns if current_user is admin;
        inaccessible_callback   - redirects to site index if inaccessible
    """

    # excludes from columns and forms
    column_exclude_list = ["Non-Pizza"]
    form_excluded_columns = ["Non-Pizza", "Extra", "Extras"]

    def is_accessible(self):
        """
        check if current_user is admin, return true if so else false
        """

        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        """
        redirect to site home if user isn't admin
        """

        return redirect(url_for('index'))


class ProductView(ModelView):
    """
    Here the ProductView class is defined
        it's based on the ModelView class

    methods:
        is_accessible           - returns if current_user is admin;
        inaccessible_callback   - redirects to site index if inaccessible
        on_model_change         - makes sure the model is entered correctly
    """

    def is_accessible(self):
        """
        check if current_user is admin, return true if so else false
        """

        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        """
        redirect to site home if user isn't admin
        """

        return redirect(url_for('index'))

    def on_model_change(self, form, model, is_created):
        """
        runs when a modelchange is called
            it makes sure toppings can only go with a pizza
            and extra cheese can only go with a nonpizza,
            also it makes sure a nonpizza and pizza can't
            be submitted in the same product

        references:
            https://stackoverflow.com/a/31859170
        """

        # one is true when a nonpizza is entered
        #   and the_other when a pizza is entered
        one = form.pizza.data is None and form.nonpizza.data is not None
        the_other = form.pizza.data is not None and form.nonpizza.data is None

        # only a pizza OR a nonpizza can be entered else ValidationError
        if one or the_other:

            # toppings can only go with a pizza
            if form.toppings.data and not the_other:
                raise ValidationError("A topping can only go with a pizza")

                return False

            # extra cheese can only go with a nonpizza
            elif form.extra_cheese.data and not one:
                raise ValidationError("A extra cheese can only go with a "
                                      "nonpizza")

                return False

            super().on_model_change(form, model, is_created)
        else:
            raise ValidationError("Choose either a pizza or nonpizza "
                                  "not both/none")
            return False


class OrderView(ModelView):
    """
    Here the OrderView class is defined
        it's based on the ModelView class

    methods:
        is_accessible           - returns if current_user is admin;
        inaccessible_callback   - redirects to site index if inaccessible
    """

    # excludes from columns
    column_exclude_list = ["User"]

    def is_accessible(self):
        """
        check if current_user is admin, return true if so else false
        """

        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        """
        redirect to site home if user isn't admin
        """

        return redirect(url_for('index'))
