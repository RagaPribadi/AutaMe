import datetime
import logging
import os
import webapp2

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

###############################################################################
# We'll just use this convenience function to retrieve and render a template.
def render_template(handler, templatename, templatevalues={}):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)


###############################################################################
# We'll use this convenience function to retrieve the current user's email.
def get_user_email():
  result = None
  user = users.get_current_user()
  if user:
    result = user.email()
  return result

###############################################################################
class MainPageHandler(webapp2.RequestHandler):
  def get(self):
    # tasks = get_tasks()
    # email = get_user_email()


    # page_params = {
    #   'tasks': tasks,
    #   'user_email': email,
    #   'login_url': users.create_login_url(),
    #   'logout_url': users.create_logout_url('/')
    # }


    render_template(self, 'index.html', {})


class PostTaskHandler(webapp2.RequestHandler):
  def post(self):
    email = get_user_email()
    if email: 
      task = PostedTask()
      title = self.request.get('title')
      task.title = title
      task.author = email
      task.desc = self.request.get('desc')
      task.put()
      self.redirect('/')
    else:
      self.redirect('/')


class PostedTask(ndb.Model):
	title = ndb.StringProperty()
	desc = ndb.StringProperty()
	author = ndb.StringProperty()
	time_created = ndb.DateTimeProperty( auto_now_add = True )



###############################################################################
def get_tasks():
  result = list()
  q = PostedImage.query()
  q = q.order(-Tasks.time_created)
  for task in q.fetch(100):
    task.count = task.count_votes()
    task.comment_count = task.count_comments()
    result.append(task)
  return result


mappings = [
  ('/', MainPageHandler),
  ('/upload', UploadPageHandler),
  ('/upload_complete', FileUploadHandler),
  ('/dumb', DumbHandler),
  ('/notdumb', NotDumbHandler),
  ('/image', ImageDetailHandler),
  ('/post_task', PostTaskHandler)
]

app = webapp2.WSGIApplication(mappings, debug=True)