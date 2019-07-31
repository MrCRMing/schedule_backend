import hashlib

from django.shortcuts import render
from rest_framework.views import APIView
from . import models, serializers
from rest_framework.response import Response
from rest_framework import status
from schedule import settings
from rest_framework.response import Response
from django.core.mail import send_mail


import time
import datetime


# Create your views here.

def md5(user_num):
    ctime = str(time.time())
    m = hashlib.md5(bytes(user_num, encoding="utf-8"))
    m.update(bytes(ctime, encoding="utf-8"))
    return m.hexdigest()


class AuthView(APIView):
    """"
    用于用户认证登录
    """

    # authentication_classes = []
    # 先不考虑全局认证
    def post(self, request, *args, **kwargs):

        ret = {"code": 1000, "msg": None}

        try:
            email = request._request.POST.get("email", None)
            user_password = request._request.POST.get("user_pwd", None)
            obj = models.Users.objects.filter(email=email, password=user_password).first()
            if not obj:
                ret["code"] = 1001
                ret["msg"] = "用户名或密码错误"
                return Response(ret, status.HTTP_200_OK)
            else:

                # 为用户登录创建token
                # token = md5(user_num)
                # 存在就更新，不存在就创建
                # models.UserToken.objects.update_or_create(user=obj, defaults={"token": token})
                # ret["token"] = token
                ser=serializers.UserSerializers(instance=obj,many=False)

                ret["msg"] = "成功登录"
                result=dict(ret,**ser.data)
                return Response(result, status.HTTP_200_OK)
        except Exception as e:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterView(APIView):
    """"
    用于用户注册
    """

    # authentication_classes = []
    def get(self, request, *args, **kwargs):  # 发送邮箱验证码
        ret = dict()
        email = request._request.GET.get("email", None)
        try:
            user=models.Users.objects.filter(pk=email).first()
            if not user:
                # 为用户登录创建验证码
                checkcode = md5(email)[:5]
                # 将验证码保存在session中
                request._request.session["checkcode"] = checkcode
                request._request.session.set_expiry(300)
                # 发送邮件
                title = "乐学课程表注册"
                msg = "您好！感谢您注册乐学课程表，这是您本次注册使用的验证码 " + checkcode + " ,该验证码将在5分钟后过期，如过期请重新点击发送，获得新的验证码"
                email_from = settings.DEFAULT_FROM_EMAIL
                reciever = [
                    email,
                ]
                # 发送邮件
                send_mail(title, msg, email_from, reciever)
                ret["code"] = 1000
                ret["msg"] = "成功发送验证码"

                return Response(ret, status.HTTP_200_OK)
            else:
                ret["code"]=1001
                ret["msg"]="该邮箱已注册过"
                return Response(ret,status.HTTP_200_OK)
        except:
            ret["code"]=1002
            ret["msg"]="该邮箱为无效邮箱"
            return Response(ret,status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):  # 注册

        ret = {"code": 1000, "msg": None}
        try:
            email = request._request.POST.get("email", None)
            user_password = request._request.POST.get("user_pwd", None)
            checkcode = request._request.POST.get("checkcode", None)

            if checkcode != request._request.session["checkcode"]:
                ret["code"] = 1002
                ret["msg"] = "验证码错误"
                return Response(ret, status.HTTP_200_OK)
            else:
                db_search = models.Users.objects.filter(email=email).first()
                if db_search == None:
                    temp = models.Users()
                    temp.email = email
                    temp.password = user_password
                    temp.save()
                    ret["code"] = 1000
                    ret["msg"] = "成功注册"
                    ret["email"]=temp.email
                    ret["user_pwd"]=temp.password

                    return Response(ret, status.HTTP_200_OK)
                else:
                    ret["code"] = 1001
                    ret["msg"] = "用户已存在"
                    return Response(ret, status.HTTP_200_OK)
        except:
            ret["code"]=1003
            ret["msg"]="验证码已失效"
            return Response(ret,status.HTTP_200_OK)


class UserView(APIView):
    """
    用于对用户信息的相关操作
    """

    def post(self, request, *args, **kwargs):  # 填写学校等相关信息
        ret = {"code": 1000, "msg": None}
        try:
            email = request._request.POST.get("email", None)
            user_name = request._request.POST.get("name", None)
            university = request._request.POST.get("university", None)
            major = request._request.POST.get("major", None)
            grade = request._request.POST.get("grade", None)
            img = request.FILES['photo']
            date = datetime.date.today().strftime("%Y%m/%d/")
            # 先创建头像
            photo = models.Photo(image=img)
            imageName = str(photo.image.name)
            locations = str(imageName).find(".")
            extension = imageName[locations:]
            name = imageName[:locations]
            namestring = name + str(time.time())
            md5 = hashlib.md5(namestring.encode('utf-8')).hexdigest()
            photo.image.name = md5[:10] + extension
            photo.url = "http://" + settings.HOST + ":" + settings.PORT + "/media/photo/" + date + photo.image.name
            photo.save()
            # 创建用户
            user = models.Users.objects.get(pk=email)
            user.name =user_name
            user.university = university
            user.major = major
            user.grade = grade
            user.photo = photo
            user.save()

            ret["code"] = 1000
            ret["msg"] = "设置信息成功"
            ser=serializers.UserSerializers(instance=user,many=False)
            result=dict(ret,**ser.data)
            return Response(result, status.HTTP_200_OK)
        except:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostView(APIView):
    """
    对帖子的相关操作
    """

    def post(self, request, *args, **kwargs):  # 创建帖子或删除帖子

        # try:
            method = request._request.POST.get("method", None)
            if method == "create":  # 创建帖子
                course_id = request._request.POST.get("course_id", None)
                email = request._request.POST.get("email", None)
                question = request._request.POST.get("question", None)
                image_num = request._request.POST.get("image_num", 0)

                date = datetime.date.today().strftime("%Y/%m/%d/")
                # 创建帖子
                post = models.Post()
                post.question = question
                post.reply_num = 0
                post.like_num = 0
                post.create_time = datetime.datetime.now()

                creator = models.Users.objects.get(pk=email)
                course = models.Course.objects.get(pk=course_id)
                post.creator = creator
                post.course = course
                post.save()

                # 判断是否上传图片
                if (int(image_num) != 0):
                    for i in range(1,int(image_num)+1):
                        # 创建图片，并与该帖子进行绑定
                        key="image_"+str(i)
                        img = request.FILES[key]
                        image = models.Image(image=img)
                        imageName = str(image.image.name)
                        locations = str(imageName).find(".")
                        extension = imageName[locations:]
                        name = imageName[:locations]
                        namestring = name + str(time.time())
                        md5 = hashlib.md5(namestring.encode('utf-8')).hexdigest()
                        image.image.name = md5[:10] + extension
                        image.post = post
                        image.url = "http://" + settings.HOST + ":" + settings.PORT + "/media/image/" + date + image.image.name

                        image.save()

                # 序列化
                ser = serializers.PostSerializers(instance=post, many=False)
                res = {
                    "code": 1000,
                    "msg": "成功创建帖子"
                }
                result=dict(res,**ser.data)
                return Response(result, status.HTTP_200_OK)

            elif method=="delete":  # 删除帖子
                post_id = request._request.POST.get("post_id", None)
                post = models.Post.objects.filter(pk=post_id).first()
                if post!=None:
                    post.delete()
                    res = {
                        "code": 1000,
                        "msg": "成功删除该帖子"
                    }
                    return Response(res, status.HTTP_200_OK)
                else:
                    res = {
                        "code": 1001,
                        "msg": "该帖子不存在"
                    }
                    return Response(res, status.HTTP_200_OK)
            else:#给该帖子点赞
                post_id=request._request.POST.get("post_id",None)
                post=models.Post.objects.get(pk=post_id)
                post.like_num=post.like_num+1
                post.save()

                res={
                    "code":1000,
                    "msg":"点赞成功",
                    "like_num":post.like_num
                }

                return Response(res,status.HTTP_200_OK)
        #
        # except:
        #     return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):  # 得到所有帖子信息
        try:
            course_id = request._request.GET.get("course_id", None)

            course = models.Course.objects.get(pk=course_id)
            # 获得该课程下所有帖子
            post_list = course.post_set.all().order_by("-id")

            if len(post_list):
                # 序列化
                ser = ser = serializers.PostSerializers(instance=post_list, many=True)
                # 为了统一返回的数据类型 在这里将列表转化为字典

                res_dict = {
                    "code": 1000,
                    "msg": "搜索到相关帖子",
                    "record_num": len(post_list)
                }
                # 遍历ser.data,将里面各字典取出
                i = 0
                for item in ser.data:
                    i += 1
                    key = "post_" + str(i)
                    res_dict[key] = item

                return Response(res_dict, status.HTTP_200_OK)
            else:
                # 未查询到符合条件的记录
                res = dict()
                res["code"] = 1001
                res["msg"] = "该论坛下尚未有帖子"
                return Response(res, status.HTTP_200_OK)
        except:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)


class MessageView(APIView):
    """
    对于帖子下回复消息的相关操作
    """

    def get(self, request, *args, **kwargs):  # 得到某帖子下的所有回复信息
        try:
            post_id = request._request.GET.get("post_id", None)
            post = models.Post.objects.get(pk=post_id)
            message_list = post.message_set.all()
            if len(message_list):
                # 序列化
                ser = serializers.MessageSerializers(instance=message_list, many=True)
                # 为了统一返回的数据类型 在这里将列表转化为字典

                res_dict = {
                    "code": 1000,
                    "msg": "搜索到相关回复",
                    "message_num": len(message_list)
                }
                # 遍历ser.data,将里面各字典取出
                i = 0
                for item in ser.data:
                    i += 1
                    key = "message_" + str(i)
                    res_dict[key] = item

                return Response(res_dict, status.HTTP_200_OK)
            else:
                # 未查询到符合条件的记录
                res = dict()
                res["code"] = 1001
                res["msg"] = "该帖子下尚未有回复"
                return Response(res, status.HTTP_200_OK)
        except:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):  # 对某个帖子新加回复
        try:
            post_id = request._request.POST.get("post_id", None)
            content = request._request.POST.get("content", None)
            email = request._request.POST.get("email", None)

            user = models.Users.objects.get(pk=email)
            post = models.Post.objects.get(pk=post_id)
            post.reply_num=post.reply_num+1
            post.save()
            message = models.Message()
            message.content = content
            message.send_time = datetime.datetime.now()
            message.sender = user
            message.post = post
            message.save()

            # 序列化
            ser = serializers.MessageSerializers(instance=message, many=False)

            # 在返回字典里增添新信息
            ret = {
                "code": 1000,
                "msg": "添加回复成功",
            }
            result = dict(ret, **ser.data)

            return Response(result, status.HTTP_200_OK)


        except:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

class LessonView(APIView):
    """
    对课程的相关操作
    """
    def get(self, request, *args, **kwargs):  # 得到该用户的所有课程信息
         try:
            email=request._request.GET.get("email",None)

            user=models.Users.objects.get(pk=email)
            lesson_list=user.lesson_set.all()
            if len(lesson_list):
                #序列化
                ser=serializers.LessonSerializers(instance=lesson_list,many=True)
                # 为了统一返回的数据类型 在这里将列表转化为字典

                res_dict = {
                    "code": 1000,
                    "msg": "成功得到该用户的课程信息",
                    "lessons_num": len(lesson_list)
                }
                # 遍历ser.data,将里面各字典取出
                i = 0
                for item in ser.data:
                    i += 1
                    key = "lesson_" + str(i)
                    res_dict[key] = item

                return Response(res_dict, status.HTTP_200_OK)
            else:
                res = dict()
                res["code"] = 1001
                res["msg"] = "该用户尚未上传过课程"
                return Response(res, status.HTTP_200_OK)

         except:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self,request,*args,**kwargs): #添加新的课程信息
        try:
            email = request._request.POST.get("email", None)
            lesson_num=request._request.POST.get("lesson_num",None)
            user = models.Users.objects.get(pk=email)
            universiy=user.university
            major=user.major

            for i in range(1,int(lesson_num)+1):
                key_course_name="course_name_"+str(i)
                key_week_num="week_num_"+str(i)
                key_weekday="weekday_"+str(i)
                key_class_num="class_num_"+str(i)
                key_teacher="teacher_"+str(i)
                key_classroom="classroom_"+str(i)
                #从POST中取出数据
                course_name=request._request.POST.get(key_course_name,None)
                week_num=request._request.POST.get(key_week_num,None)
                weekday=request._request.POST.get(key_weekday,None)
                class_num=request._request.POST.get(key_class_num,None)
                teacher=request._request.POST.get(key_teacher,None)
                classroom=request._request.POST.get(key_classroom,None)
                #创建lesson对象
                lesson=models.Lesson()
                lesson.week_num=week_num
                lesson.weekday=weekday
                lesson.class_num=class_num
                lesson.teacher=teacher
                lesson.classroom=classroom
                #为该课程指定用户
                lesson.user=user
                #为该课程指定course,如果数据库中已有该course则直接建立联系，若没有则新建course
                course_obj=models.Course.objects.filter(course_name=course_name,university=universiy,major=major).first()
                if not course_obj:
                    course=models.Course()
                    course.course_name=course_name
                    course.university=universiy
                    course.major=major
                    course.save()
                    lesson.course=course
                    lesson.save()
                else:
                    lesson.course=course_obj
                    lesson.save()

            #返回操作信息，暂不考虑将新添的lesson信息返回
            res={
                "code":1000,
                "msg":"上传成功"
            }
            return Response(res,status.HTTP_200_OK)

        except:
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)

