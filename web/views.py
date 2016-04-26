# Create your views here.
import json
import logging
import re
from smtplib import SMTPRecipientsRefused
import cStringIO as StringIO
from cgi import escape

from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView, DeleteView, UpdateView, CreateView
from jinja2 import Environment, PackageLoader
from tinymce.widgets import TinyMCE
# import ho.pisa as pisa
from django.http import HttpResponse

from api import models
from api.models import House, Message, Note
from greendoors.services.mail_service import SMTPConnection
from greendoors.services.report_service import ReportService


logger = logging.getLogger(__name__)

env = Environment(loader=PackageLoader('data', 'email_templates'))


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        exclude = ['timestamp', 'user', 'created', 'house']


class NoteCreate(CreateView):
    template_name = 'greendoors/note.html'
    model = Note
    form_class = NoteForm


class NoteUpdate(UpdateView):
    template_name = 'greendoors/note.html'
    model = Note
    form_class = NoteForm


class NoteDelete(DeleteView):
    template_name = 'greendoors/note.html'
    model = Note
    success_url = reverse_lazy('author-list')
    form_class = NoteForm



class NoteView(FormView):
    """
    Provide internal messaging system.

    Each message has a key, that is used in a URL to identify.

    When responding a new message is created with a new URL key.

    This class is called twice:
    1. with GET when the form is loaded
    2. with POST when the response is posted

    """
    template_name = 'greendoors/note.html'
    form_class = NoteForm
    success_url = reverse_lazy('web:notes')



def edit_note(request, pk, template_name):
    if pk:
        note = get_object_or_404(models.Note, pk=pk)

    if request.method == 'POST':
        note_form = NoteForm(request.POST, instance=note)
        if note_form.is_valid():
            note = note_form.save()
            return HttpResponseRedirect(reverse('web:notes'))
    else:
        note_form = NoteForm(request.GET, instance=note, initial={'text': note.text})
        return render_to_response(template_name, {'form': note_form}, context_instance=RequestContext(request))


class NotesListView(ListView):
    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        self.request = request
        return super(NotesListView, self).get(request, *args, **kwargs)


class HouseDetailView(DetailView):
    queryset = House.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(HouseDetailView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['image'] = self.object.image.all()[0]
        return context


        # def get_object(self):
        #     # Call the superclass
        #     object = super(HouseDetailView, self).get_object()
        #
        #     # Return the object
        #     return object
        #
        #     # return HttpResponse('<img src="data:image/png;base64,' + house.image.img_data + '" />')


def detail(request, pk):
    house = get_object_or_404(House, pk=pk)

    data = {'house': house, 'image': house.image.all()[0]}
    return render(request, 'greendoors/house.html', data)


def debug(request):
    return render(request, 'greendoors/debug.html', {'host': request.get_host()})


def insert_response_url_header(key=None, text=None):
    # Add the response key to the top of the text
    # url = "https://localhost:8000/web/mail/{0}".format(message.key)
    url = reverse_lazy('web:contact', kwargs={'key': key})
    domain = Site.objects.get(pk=1).domain
    str_path = str(url)
    header_template = env.get_template('message_header.html')
    header = header_template.render(domain=domain, path=str_path)

    message_template = env.get_template('sent_message_layout.html')
    text_with_header = message_template.render(header=header, body=text)
    return text_with_header


class ContactForm(forms.ModelForm):
    text = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30}))

    class Meta:
        model = Message
        exclude = ('created_by', 'sender', 'receiver', 'timestamp', 'sent', 'thread')


    def send_email(self, bcc=False):
        # send email using the self.cleaned_data dictionary

        # get this message
        old_message = self.instance

        # get this thread
        thread = old_message.thread
        house_id = ""
        try:
            house_id = thread.messages[0].receiver.home_owner_profile.house.all()[0].pk
        except:
            pass
            # Create a new message instance
        message = Message(text="",
                          sender=old_message.receiver,
                          receiver=old_message.sender,
                          thread=thread
        )
        message.save()

        text_with_header = insert_response_url_header(key=message.key, text=self.cleaned_data['text'])
        message.text = text_with_header

        message.save()

        # send
        bcc_email = None
        if bcc:
            bcc_email = old_message.receiver.email

        try:
            con = SMTPConnection()
            success = con.send_email(recipient_address=message.receiver.email,
                                     subject="Greendoors Communications [House {0}]".format(house_id),
                                     body=message.text, bcc=bcc_email)
        except SMTPRecipientsRefused:
            logger.error("Email sending refused for message {0}".format(message.pk))
        if success:
            message.sent = True
            message.save()


def email_quote(text):
    """A non-optimal implementation of a regex filter"""
    # text = '\n' + text
    return re.sub(r'\n', '\n> ', text)
    # return re.sub('\n','\n > ', text)


env.filters['email_quote'] = email_quote


class ContactView(FormView):
    """
    Provide internal messaging system.

    Each message has a key, that is used in a URL to identify.

    When responding a new message is created with a new URL key.

    This class is called twice:
    1. with GET when the form is loaded
    2. with POST when the response is posted

    """
    template_name = 'greendoors/mail.html'
    form_class = ContactForm
    success_url = reverse_lazy('web:thanks')

    def get_context_data(self, **kwargs):
        data = super(ContactView, self).get_context_data(**kwargs)
        data.update({'key': self.kwargs['key']})
        return data

    def get_initial(self):
        """
        In order to find the original message model, we inject the key here.
        The instance resolver in the ContactForm (above) will use this to find the correct message.

        We don't need to do that on POST.
        """
        data = super(ContactView, self).get_initial()
        # if self.request.method == 'GET':
        message_filter = Message.objects.filter(key__exact=self.kwargs['key'])
        self.message = message_filter[0]
        message_template = env.get_template('display_message_layout.html')
        data.update({'text': message_template.render(original_msg=self.message.text)})
        return data

    def get_form_kwargs(self):
        # also calls self.get_initial() ...
        kwargs = super(ContactView, self).get_form_kwargs()
        # if self.request.method == 'GET':
        # resolve the message instance
        kwargs['instance'] = self.message

        return kwargs

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        if 'bcc' in form.data:
            bbc = True
        else:
            bbc = False
        form.send_email(bcc=bbc)
        return super(ContactView, self).form_valid(form)




def report(request):
    report = ReportService().get_html_report(user=request.user)
    return HttpResponse(content=report)


def render_to_pdf(html):

    raise NotImplementedError("Pisa is disabled")
    result = StringIO.StringIO()

    # pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
    # if not pdf.err:
    #     return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


def pdf_report(request):
    #Retrieve data or whatever you need
    report = ReportService().get_html_report(user=request.user)
    return render_to_pdf(report)
