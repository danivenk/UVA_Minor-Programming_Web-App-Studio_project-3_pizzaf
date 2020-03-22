from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask import redirect, url_for, session
from flask_login import current_user
from wtforms.validators import ValidationError


class AdminUserIndexView(AdminIndexView):
    @expose("/admin")
    def index(self):
        urls_list = session.get("urls")

        return self.render("index.html", urls=urls_list)


class MenuView(ModelView):
    column_exclude_list = ["Non-Pizza"]
    form_excluded_columns = ["Non-Pizza", "Extra", "Extras"]

    def is_accessible(self):
        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect if user isn't admin
        return redirect(url_for('index'))


class AdminView(ModelView):
    column_exclude_list = ["password"]
    form_exclude_columns = ["Order"]

    def is_accessible(self):
        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect if user isn't admin
        return redirect(url_for('index'))


class OrderView(ModelView):
    column_exclude_list = ["User"]

    def is_accessible(self):
        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect if user isn't admin
        return redirect(url_for('index'))


class ProductView(ModelView):

    def is_accessible(self):
        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect if user isn't admin
        return redirect(url_for('index'))

    def on_model_change(self, form, model, is_created):
        """https://stackoverflow.com/a/31859170"""

        one = form.pizza.data is None and form.nonpizza.data is not None
        the_other = form.pizza.data is not None and form.nonpizza.data is None

        if one or the_other:
            if form.toppings.data and not the_other:
                raise ValidationError("A topping can only go with a pizza")

                return False
            elif form.extra_cheese.data and not one:
                raise ValidationError("A extra cheese can only go with a "
                                      "nonpizza")

                return False

            super().on_model_change(form, model, is_created)
        else:
            raise ValidationError("Choose either a pizza or nonpizza "
                                  "not both/none")
            return False
