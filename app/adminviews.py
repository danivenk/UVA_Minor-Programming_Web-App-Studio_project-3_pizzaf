from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask import redirect, url_for, session
from flask_login import current_user


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
    column_exclude_list = ["password", ]

    def is_accessible(self):
        return current_user.admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect if user isn't admin
        return redirect(url_for('index'))
