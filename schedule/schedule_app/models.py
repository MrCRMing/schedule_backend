from django.db import models
import datetime, os


def get_image_path(instance, filename):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    year, month, day = date.split("-")

    return os.path.join("image", year, month, day, filename)


def get_photo_path(instance, filename):
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    year, month, day= date.split("-")

    return os.path.join("photo", year, month, day, filename)


# Create your models here.
class Users(models.Model):
    class Meta:
        db_table = "users"

    email = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=20, null=True)
    password = models.CharField(max_length=20)
    university = models.CharField(max_length=20, null=True)
    major = models.CharField(max_length=20, null=True)
    grade = models.CharField(max_length=20, null=True)

    # 指定外键
    photo = models.OneToOneField("Photo", on_delete=models.CASCADE, default=None, null=True)

    def __str__(self):
        return "%s-%s-%s-%s-%s-%s" % (self.email, self.name, self.password, self.university, self.major, self.grade)


class Course(models.Model):
    class Meta:
        db_table = "course"

    course_name = models.CharField(max_length=30)
    university = models.CharField(max_length=20)
    major = models.CharField(max_length=20)


class Lesson(models.Model):
    class Meta:
        db_table = "lesson"

    week_num = models.CharField(max_length=20)
    weekday = models.CharField(max_length=20)
    class_num = models.CharField(max_length=20)
    teacher = models.CharField(max_length=20)
    classroom = models.CharField(max_length=20)

    # 指定外键
    course = models.ForeignKey("Course", on_delete=None)
    user = models.ForeignKey("Users", on_delete=models.CASCADE)


class Post(models.Model):
    class Meta:
        db_table = "post"

    question = models.CharField(max_length=300)
    reply_num = models.IntegerField()
    like_num = models.IntegerField()
    create_time = models.DateTimeField()

    # 指定外键
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    creator = models.ForeignKey("Users", on_delete=models.CASCADE)


class Message(models.Model):
    class Meta:
        db_table = "message"

    content = models.CharField(max_length=200)
    send_time = models.DateTimeField()

    # 指定外键
    sender = models.ForeignKey("Users", on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)


class Image(models.Model):
    url = models.TextField(null=True)
    image = models.ImageField(upload_to=get_image_path)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)

    # 建立外键
    post = models.ForeignKey("Post", on_delete=models.CASCADE)

    class Meta:
        db_table = "image"


class Photo(models.Model):
    url = models.TextField(null=True)
    image = models.ImageField(upload_to=get_photo_path)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = "photo"


class checkcode(models.Model):
    class Meta:
        db_table = "checkcode"

    email = models.CharField(max_length=30,primary_key=True)
    code = models.CharField(max_length=10)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    update_time = models.DateTimeField(auto_now=True, null=True)