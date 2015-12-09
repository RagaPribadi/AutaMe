import os
import webapp2

from google.appengine.ext.webapp import template
from google.appengine.api import users



def render_template(handler, templatename, templatevalues):
  path = os.path.join(os.path.dirname(__file__), 'templates/'+ templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)





class MyHandler(webapp2.RequestHandler):
    def get(self):         
        user = users.get_current_user()
        if user:
            page_params = {
            'logout_url': users.create_logout_url('/')
            }
            greeting = ('(<a href="%s">sign out</a>)' % users.create_logout_url('/'))
            self.response.out.write("<html><body>GO TO MAIN PAGE</body></html>")
            self.response.out.write("<html><body>%s</body></html>" % greeting)
        else:
            page_params = {
            'login_url': users.create_login_url('/')
            }
            render_template(self, 'login.html', page_params)


        # user = users.get_current_user()
        # if user:
        #     greeting = ('Welcome, %s! (<a href="%s">sign out</a>)' %
        #                 (user.nickname(), users.create_logout_url('/')))

        #     self.response.out.write("<html><body>%s</body></html>" % greeting)
        # else:
        #     render_template(self, 'login.html', {})
        #     greeting = ('<a href="%s">Sign in or register</a>.' %
        #                 users.create_login_url('/'))

        #     self.response.out.write("<html><body>%s</body></html>" % greeting)
        







app = webapp2.WSGIApplication([
	('/', MyHandler),
], debug=True)