from registration.forms import RegistrationForm

from api.models import UserProfile


__author__ = 'schien'
from registration.views import ActivationView as BaseActivationView
from registration.models import RegistrationProfile

from registration.backends.default.views import RegistrationView


class ActivationView(BaseActivationView):
    def activate(self, request, activation_key):
        """
        Given an an activation key, look up and activate the user
        account corresponding to that key (if possible).

        After successful activation, the signal
        ``registration.signals.user_activated`` will be sent, with the
        newly activated ``User`` as the keyword argument ``user`` and
        the class of this backend as the sender.

        """
        activated_user = RegistrationProfile.objects.activate_user(activation_key)
        # if activated_user:
        # signals.user_activated.send(sender=self.__class__,
        # user=activated_user,
        # request=request)
        return activated_user

    def get_success_url(self, request, user):
        return ('registration_activation_complete', (), {})


from django import forms
from django.utils.translation import ugettext_lazy as _


class RegistrationFormGreendoors(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.

    """
    newsletter = forms.BooleanField(widget=forms.CheckboxInput,
                                    initial=True,
                                    label=_(
                                        u'Please add my email address to the Bristol Green Doors monthly newsletter'),
                                    required=False
    )
    participate_research = forms.BooleanField(widget=forms.CheckboxInput,
                                              required=False,
                                              initial=True,

                                              label=_(
                                                  u'I am happy to be contacted by the University of Bristol for research purposes involving this app. Financial incentives are available with participation.'),
    )


class RegistrationViewGreendoors(RegistrationView):
    form_class = RegistrationFormGreendoors


    def register(self, request, **cleaned_data):

        user = super(RegistrationViewGreendoors, self).register(request, **cleaned_data)

        UserProfile(user=user, newsletter=cleaned_data['newsletter'],
                    research=cleaned_data['participate_research']).save()

        return user