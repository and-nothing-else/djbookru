from django.contrib.auth.models import UserManager, User as BaseUser
from django.db import models
from django.db.models.signals import post_save
import datetime
import hashlib
from django.utils.translation import ugettext_lazy as _
from sorl.thumbnail.main import DjangoThumbnail

class User(BaseUser):
    photo = models.ImageField(_(u'photo'), upload_to='users/photo',null=True,blank=True)    
    biography = models.TextField(_(u'biography'), blank=True)
    homepage = models.URLField(_(u'homepage'), verify_exists=False, blank=True)
        
    #forum profile fields
    last_activity = models.DateTimeField(_(u'last activity'), null=True)
    last_session_activity = models.DateTimeField(_(u'last session activity'), null=True)
    userrank = models.CharField(_(u'user rank'), max_length=30, default="Junior Member")
    last_posttime = models.DateTimeField(_(u'last posttime'), null=True)
    signature = models.CharField(_(u'signature'), max_length = 1000, null = True, blank = True)
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _(u'User')
        verbose_name_plural = _(u'Users')
    
    @models.permalink
    def get_absolute_url(self):
        return ('accounts:profile', [self.pk])      
    
    def gravatar_photo(self):
        return 'http://www.gravatar.com/avatar/%s.jpg' % self.getMD5()
    
    def avatar(self):
        if self.photo:
            return DjangoThumbnail(self.photo, (80, 80))
        else:
            return self.gravatar_photo()
    
    #forum profile methods
    def get_total_posts(self):
        return self.user.ftopics_set.count() + self.user.reply_set.count()
    
    def is_online(self):
        from django.conf import settings
        last_online_duration = getattr(settings, 'LAST_ONLINE_DURATION', 900)
        now = datetime.datetime.now()
        if (now - self.last_activity).seconds < last_online_duration:
            return True
        return False   

    def getMD5(self):
        m = hashlib.md5()
        m.update(self.user.email)        
        return m.hexdigest()
    
    def get_since_last_visit(self):
        "Topics with new relies since last visit"
        from dinette.models import Ftopics
        return Ftopics.objects.get_new_since(self.last_session_activity)
    
    @property
    def nickname(self):
        #for easy change of user name display 
        return self.username
    
def create_custom_user(sender, instance, created, **kwargs):
    if created:
        values = {}
        for field in sender._meta.local_fields:
            values[field.attname] = getattr(instance, field.attname)
        user = User(**values)
        user.save()
        
post_save.connect(create_custom_user, BaseUser)