from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.utils.text import slugify
from shortuuid.django_fields import ShortUUIDField
import shortuuid

class User(AbstractUser):
    username = models.CharField(unique=True, max_length=100)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        email_username, mobile = self.email.split("@")
        if self.full_name == "" or self.full_name == None:
            self.full_name = email_username
        if self.username == "" or self.username == None:
            self.username = email_username  
    
        super(User, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.FileField(upload_to="image", default="default/default-user.jpg", null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    bio = models.CharField(max_length=100, null=True, blank=True)
    about = models.CharField(max_length=100, null=True, blank=True)
    author = models.BooleanField(default=False)
    country = models.CharField(max_length=100, null=True, blank=True)
    facebook = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "profile"

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.full_name:
            self.full_name = self.user.full_name
        super(Profile, self).save(*args, **kwargs)

def create_user_profile(sender,instance,created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender,instance,**kwargs):
    instance.profile.save()

post_save.connect(create_user_profile,sender=User)
post_save.connect(save_user_profile,sender=User)

class Category(models.Model):
    title = models.CharField(max_length=200)
    image = models.FileField(upload_to="image", blank=True, null=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    
    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title
    
    def save(self,*args, **kwargs):
        if self.slug =="" or self.slug==None:
            self.slug = slugify(self.title)
        super(Category,self).save()

    def post_count(self):
        return Post.objects.filter(category=self).count()

class Post(models.Model):
    STATUS = (
        ('Active', 'Active'),
        ('Draft', 'Draft'),
        ('Disabled', 'Disabled')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,related_name='posts')
    title = models.CharField(max_length=200, blank=True, null=True)
    tags = models.CharField(max_length=100, blank=True, null=True)
    Description = models.TextField(blank=True, null=True)
    image = models.FileField(upload_to="image", null=True, blank=True)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, blank=True, related_name="likes_user")
    status = models.CharField(choices=STATUS, max_length=100, default="Active")
    slug = models.SlugField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + '-' + shortuuid.uuid()[:2]
        super(Post, self).save(*args, **kwargs)

    def comment(self):
        return Comment.objects.filter(post=self)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100,null=True, blank=True)
    email = models.CharField(max_length=100,null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post.title} - {self.name}"

    class Meta:
        verbose_name_plural = "Comments"
    


    
class Bookmark(models.Model):
    post = models.ForeignKey(Post,blank=True,on_delete=models.CASCADE)
    user = models.ForeignKey(User,blank=True,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "bookmark"

    def __str__(self):
        return self.post.title
    
class Notification(models.Model):
    NOT_TYPE = (
        ('Like','Like'),
        ('Comment','Comment'),
        ('Bookmark','Bookmark'),
    )
    post = models.ForeignKey(Post,blank=True,on_delete=models.CASCADE)
    user = models.ForeignKey(User,blank=True,on_delete=models.CASCADE)
    type = models.CharField(choices=NOT_TYPE,max_length=200)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "notification"

    def __str__(self):
        if self.post:
            return f"{self.post.title} - {self.type}"
        else:
            return "Notification"
      