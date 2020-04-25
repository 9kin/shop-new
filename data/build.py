from flask_admin import BaseView, expose


class Build(BaseView):
    @expose('/')
    def index(self):
        return self.render('/admin/build.html')