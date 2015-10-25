#!/usr/bin/env python

import webapp2
import logging
from webapp2_extras import routes

from utils import render_to_text

class PageHandler(webapp2.RequestHandler):

  element_name = None

  def get(self):
    self.response.write(render_to_text('page.html', {
      'element_name': self.element_name
    }))

  @classmethod
  def HandlerFor(cls, element):
    class stub(PageHandler):
      element_name = element
    return stub


app = webapp2.WSGIApplication([
  ('/',               PageHandler.HandlerFor('photo-cover')),
  ('/staying-there/', PageHandler.HandlerFor('staying-there'))
], debug=False)
