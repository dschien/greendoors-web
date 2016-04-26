from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from web import views
from web.views import HouseDetailView, ContactView, NotesListView, NoteCreate, NoteUpdate, NoteDelete

urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name="greendoors/index.html"), name="home"),
                       url(r'^about$', TemplateView.as_view(template_name="greendoors/about.html"), name="about"),
                       url(r'^contact$', TemplateView.as_view(template_name="greendoors/contact.html"), name="contactpage"),
                       url(r'^app$', TemplateView.as_view(template_name="greendoors/app.html"), name="app_info"),

                       url(r'^mail/(?P<key>[0-9a-z\-]+)/$', ContactView.as_view(), name='contact'),
                       url(r'house/(?P<pk>\d+)',
                           HouseDetailView.as_view(template_name="greendoors/house.html",
                                                   context_object_name="house"),
                           name='web_house_detail'),
                       # url(r'^house/(?P<pk>\d+)/$', detail, name='detail'),
                       url(r'^thanks/', TemplateView.as_view(template_name="greendoors/thanks.html"), name="thanks"),
                       url(r'^privacy/', TemplateView.as_view(template_name="greendoors/privacy.html"),
                           name="privacy"),
                       # url(r'^debug/', views.debug)
                       url(r'^notes$', login_required(NotesListView.as_view(template_name="greendoors/notes.html")), name='notes'),


                       url(r'note/add/$', login_required(NoteCreate.as_view()), name='note_add'),
                       url(r'note/(?P<pk>\d+)/$', login_required(NoteUpdate.as_view()), name='note'),
                       url(r'note/(?P<pk>\d+)/delete/$', login_required(NoteDelete.as_view()), name='note_delete'),
                       # url(r'^note/(?P<pk>\d+)$', views.edit_note, {'template_name': "greendoors/note.html"},
                       #     name='note'),
                       # url(r'^note/(?P<pk>\d+)$', views.edit_note, {'template_name': "greendoors/note.html"},
                       #     name='note-detail'),
                       url(r'^pdf$', login_required(views.pdf_report), name='pdf'),
                       url(r'^report$', login_required(views.report), name='report'),




)