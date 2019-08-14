from rest_framework import serializers


class PostSerializers(serializers.Serializer):
    post_id = serializers.IntegerField(source="id")
    question = serializers.CharField()
    reply_num = serializers.IntegerField()
    like_num = serializers.IntegerField()
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')
    course_id = serializers.IntegerField(source="course.id")  # 正向获取外键的信息
    creator = serializers.SerializerMethodField()  # 自定义显示，正向获取外键的信息
    content_images = serializers.SerializerMethodField()  # 自定义显示，反向获取外键的信息
    content_files = serializers.SerializerMethodField()# 自定义显示，反向获取外键的信息
    def get_creator(self, row):
        res = dict()
        res["email"] = row.creator.email
        res["name"] = row.creator.name
        res["university"] = row.creator.university
        res["major"] = row.creator.major
        res["grade"] = row.creator.grade
        res["photo_url"] = row.creator.photo.url
        return res

    def get_content_images(self, row):
        res = []
        image_list = row.image_set.all()
        for item in image_list:
            res.append(item.url)
        return res

    def get_content_files(self, row):
        res = []
        file_list = row.file_set.all()
        for item in file_list:
            res.append(item.url)
        return res


class MessageSerializers(serializers.Serializer):
    post_id = serializers.IntegerField(source="post.id")
    message_id = serializers.IntegerField(source="id")
    content = serializers.CharField()
    send_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S')  # 格式时间输出
    sender = serializers.SerializerMethodField()  # 自定义显示，正向获取外键的信息
    content_images = serializers.SerializerMethodField()  # 自定义显示，反向获取外键的信息
    content_files = serializers.SerializerMethodField()  # 自定义显示，反向获取外键的信息

    def get_sender(self, row):
        res = dict()
        res["email"] = row.sender.email
        res["name"] = row.sender.name
        res["university"] = row.sender.university
        res["major"] = row.sender.major
        res["grade"] = row.sender.grade
        res["photo_url"] = row.sender.photo.url
        return res

    def get_content_images(self, row):
        res = []
        image_list = row.image_set.all()
        for item in image_list:
            res.append(item.url)
        return res

    def get_content_files(self, row):
        res = []
        file_list = row.file_set.all()
        for item in file_list:
            res.append(item.url)
        return res


class LessonSerializers(serializers.Serializer):
    lesson_id = serializers.IntegerField(source="id")
    year = serializers.IntegerField()
    semester = serializers.IntegerField()
    week_num = serializers.CharField()
    day_of_week = serializers.IntegerField()
    day_slot = serializers.CharField()
    teacher = serializers.CharField()
    classroom = serializers.CharField()
    description = serializers.CharField()
    course_id=serializers.CharField(source="course.id")
    course_name = serializers.CharField(source="course.course_name")



class UserSerializers(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    name = serializers.CharField()
    university = serializers.CharField()
    major = serializers.CharField()
    grade = serializers.CharField()
    photo_url = serializers.SerializerMethodField()  # 自定义显示

    def get_photo_url(self, row):
        if row.photo != None:
            return row.photo.url
        else:
            return "null"
