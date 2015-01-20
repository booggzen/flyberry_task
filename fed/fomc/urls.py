from django.conf.urls import patterns, url
from fomc import views

urlpatterns = patterns('',
    url(r'^$', views.version, name='version'),
    url(r'^calendar', views.calendar),
    #TODO: this url could be generic to support any query based upon table name    
    url(r'^pace_of_firming', views.pace_of_firming),

)