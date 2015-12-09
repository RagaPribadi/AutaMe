import datetime
import logging
import os
import webapp2
import cgi

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import mail


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

def get_user_nickname():
  result = None
  user = users.get_current_user()
  if user:
    result = user.nickname()
    return result

###############################################################################
class MainPageHandler(webapp2.RequestHandler):
  def get(self):
    user_email = get_user_email()
    if user_email:
      tasks = get_tasks()
      page_params = {
      'tasks': tasks,
      'user_email': user_email,
      'nickname': get_user_nickname()
        # 'login_url': users.create_login_url(),
        # 'logout_url': users.create_logout_url('/')
      }
      render_template(self, 'index1.html', page_params)
    else:
      page_params = {
      'login_url': users.create_login_url('/')
      }
      render_template(self, 'login.html', page_params)

class ProfilePageHandler(webapp2.RequestHandler):
  def get(self):
    user_email = get_user_email()
    page_params = {
      'nickname': get_user_nickname(),
      'user_email': user_email,
      'logout_url': users.create_logout_url('/')
      }
    render_template(self, 'profile_page.html', page_params)

class MapPageHandler(webapp2.RequestHandler):
  def get(self):
    render_template(self, 'map_page.html', {})

class ContactUsPageHandler(webapp2.RequestHandler):
  def get(self):
    render_template(self, 'main_contact.html')

class PostPageHandler(webapp2.RequestHandler):
  def get(self):
    render_template(self, 'post_task.html', {})


class PostTaskHandler(webapp2.RequestHandler):
  def post(self):
    task = Task_Model()
    task.title = cgi.escape(self.request.get('title'))
    task.author = get_user_email()
    task.content = self.request.get('desc')
    task.category =self.request.get('category')
    task.pending = 0
    task._put()
    self.response.out.write({'title':  task.title, 'author': task.author})
    self.redirect('/')

class Refresh(webapp2.RequestHandler):
  def get(self):
    self.post()
  def post(self):
    tasks = get_tasks()
    takss_json = join.dumb(tasks)
    render_template(self, takss_json, {})

    # self.response.write(cgi.escape(self.request.get('desc')))
    # self.response.write('</pre></body></html>')
###############################################################################
class AcceptHandler(webapp2.RequestHandler):
  def get(self):
    id = self.request.get('id')
    task = get_task(id)
    if task:
      page_params = {
        'task': task
        }
      task.key.delete()
    self.redirect('/')
###############################################################################
class ClaimHandler(webapp2.RequestHandler):
  def get(self):
    id = self.request.get('id')
    task = get_task(id)
    if task:
      page_params = {
        'task': task
        }
      task.pending = 2
      task._put()
      from_address = 'auta-me-1@appspot.gserviceaccount.com'
      claimer_email = get_user_email()
      claim_body = 'The user with the email ' + claimer_email + ' wants to help! Email the claimer to receive help!'
      post_author = task.author
      mail.send_mail(from_address, post_author, 'Auta Post Claimed', claim_body)
    self.redirect('/')
###############################################################################
class TaskDetailHandler(webapp2.RequestHandler):
  def get(self):
    id = self.request.get('id')
    task = get_task(id)
    current = get_user_email()
 #   email = get_user_email()
    if task:
      #task.comments = task.get_comments()
      #task.comment_count = len(task.comments)
      #task.count = task.count_votes()
      page_params = {
      # 'user_email': email,
      # 'login_url': users.create_login_url(),
      # 'logout_url': users.create_logout_url('/'),
      'task': task,
      'current': current
      }
      render_template(self, 'task_detail.html', page_params)
    else:
      self.redirect('/')

####################################################################################
#handle contact form
class FormHandler(webapp2.RequestHandler):
  def post(self):
    name = self.request.get('name')
    message = self.request.get('message')
    email = self.request.get('email')
    
    params = {
      'name': name,
      'message': message,
      'email': email
    }
    
    from_address = 'auta-me-1@appspot.gserviceaccount.com'
    subject = 'Contact from ' + name
    body = 'Message from ' + email + ':\n\n' + message
    mail.send_mail(from_address, 'autame1520@gmail.com', subject, body)
    mail.send_mail(from_address, email, 'Auta Me Customer Service', 'Thanks for contacting us. We will get back to you shortly')

    render_template(self, 'response_contact.html', params)

###############################################################################
# models
class Task_Model(ndb.Model):
  title = ndb.StringProperty()
  content = ndb.StringProperty()
  author = ndb.StringProperty()
  category = ndb.StringProperty()
  pending = ndb.IntegerProperty()

  time_created = ndb.DateTimeProperty(auto_now_add=True)


###############################################################################
# static methods
def get_tasks():
  result = list()
  q = Task_Model.query()
  q = q.order(-Task_Model.time_created)
  for task in q.fetch(100):
    result.append(task)
 
  return result

###############################################################################
def get_task(task_id):
  return ndb.Key(urlsafe=task_id).get()

mappings = [
  ('/', MainPageHandler),
  ('/post_task', PostTaskHandler),
  # ('/upload', UploadPageHandler),
  # ('/upload_complete', FileUploadHandler),
  # ('/dumb', DumbHandler),
  # ('/notdumb', NotDumbHandler),
  ('/task', TaskDetailHandler),
  ('/post', PostPageHandler),
  ('/map', MapPageHandler),
  ('/profile', ProfilePageHandler),
  ('/refresh', Refresh),
  ('/contact', ContactUsPageHandler),
  ('/send-contact', FormHandler),
  ('/claim', ClaimHandler),
  ('/accept', AcceptHandler)
]

app = webapp2.WSGIApplication(mappings, debug=True)