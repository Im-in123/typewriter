from django.shortcuts import render

# Create your views here.

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.views.generic import ListView, DetailView, View,CreateView, DeleteView, UpdateView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from .models import Collection, Images, Results, Notification, ProofImages, CustomNotification, ImgConvert
from typr_users.models import Temp, Profile
from typr_users.forms import AdminAmountForm, AdminPaidForm, AdminImageTyped, AdminCollectionDone, AdminAmountDepositForm, UserUpdateEmailForm, UserUpdatePhone
from django.contrib.auth.models import User

import os
import base64


from io import StringIO
 
from django.urls import reverse 
# Create your views here.

from django.http.response import HttpResponseRedirect

from django.http import JsonResponse
# def handler404(request, *args, **kwargs):
#     #return HttpResponseRedirect('/')
#     return render(request, "typr_main/home.html")
from PIL import Image



def home(request, *args, **kwargs):
    context = {
           "message": "Welcome to iHype"
        }
    if request.user.is_authenticated:

        return redirect("typr_main:dashboard")
    else:
        return render(request, "typr_main/home.html", context)

def dashboard(request, *args, **kwargs):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("typr_main:super_pending")

        try:
            cc = get_object_or_404(Temp, username = request.user)
            print(cc)
            cv = cc.number
            cvv = cc.gender
        except Exception as e:
            print('*********** passsssss  ccc ***********', e)
        
        try:
            dd  = User.objects.get(username= request.user).profile
            dd.phonenumber = cv
            dd.gender = cvv
            dd.save()
            cc.delete()
            
        except Exception as d:
            print('*********** passsssss ddd ***********', d)

        

        noti = Notification.objects.all().filter(user = request.user, viewed= False)


        try:
            cnotifica = CustomNotification.objects.all().filter(user = request.user, viewed= False)
            print(cnotifica, len(cnotifica), ",,,,,,,,,,,,,,,,,,,,,,,,,,,,")
        except Exception as e:
                cnotifica = None
                print(e, '''''''''''''''''''''''''')

        
        summary = Collection.objects.all().filter(client= request.user, uploading= False).order_by("id")
        payment_count = 0
        order_count = 0
        in_progress_count = 0
        pending_count = 0
        completed_count = 0
        if cnotifica != None:
            for a in cnotifica:
                if a.target == "pending":
                    pending_count += 1
                elif a.target == "order":
                    order_count += 1
                elif a.target == "in_progress":
                    in_progress_count += 1
                elif a.target == "completed":
                    completed_count += 1
                elif a.target == "payment":
                    payment_count += 1
                else:
                    pass
        context = {
            'noti':noti,
            'pending_count':pending_count,
            'in_progress_count': in_progress_count,
            'completed_count':completed_count,
            'payment_count':payment_count,
            'summary':summary
        }
        return render(request, "typr_main/dashboard/dashboard.html", context)
    else:
        return redirect("typr_users:login")

def notification(request, id, *args, **kwargs):
    if request.user.is_authenticated:
        noti = Notification.objects.get(id = id)
        noti.viewed = True
        noti.save()
        return redirect("typr_main:dashboard")

def deletecoll(request, id, *args, **kwargs):
    if request.user.is_authenticated:
        coll = Collection.objects.get(id = id)
        coll.delete()
        return redirect("typr_main:pending")

def deletecoll2(request, id, *args, **kwargs):
    if request.user.is_authenticated:
        coll = Collection.objects.get(id = id)
        coll.delete()
        return redirect("typr_main:completed")
        
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
#from braces.views import CsrfExemptMixin
@method_decorator(csrf_exempt, name='dispatch')
class order(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
        	
            try:
            	todel = Collection.objects.all().filter(client = self.request.user, uploading = True)
            	for a in todel:
                    a.delete()
            except:
            	pass
        	
            try:
                cnotifica = CustomNotification.objects.all().filter(user = self.request.user, viewed= False)
             
            except Exception as e:
                cnotifica = None
            payment_count = 0
            order_count = 0
            in_progress_count = 0
            pending_count = 0
            completed_count = 0
            if cnotifica != None:
                for a in cnotifica:
                    if a.target == "pending":
                        pending_count += 1
                    if a.target == "order":
                        a.viewed = True
                        a.save()
                    elif a.target == "in_progress":
                        in_progress_count += 1
                    elif a.target == "completed":
                        completed_count += 1
                    elif a.target == "payment":
                        payment_count += 1
                    else:
                        pass
            context = {
            'pending_count':pending_count,
            'in_progress_count': in_progress_count,
            'completed_count':completed_count,
            'payment_count':payment_count
                }
          

            return render(self.request, "typr_main/dashboard/order.html", context)
        return redirect("typr_users:login")

    def post(self,*args, **kwargs):
        
        if self.request.method =="POST":
            try:
                collname = self.request.POST['collection']
                images = self.request.FILES.getlist('images')
                try:
                    upload_done = self.request.POST['upload_done']
                    print("upload_done", upload_done)
                except Exception as e:
                	pass
                	
                print("collname",collname)
                print("images", images)
                try:
                	delete_prev = self.request.POST['delete_prev']
                	print("delete_prev", delete_prev)
                	if delete_prev == "True":
                	    delp = Collection.objects.all().filter(client = self.request.user, uploading = True)
                	    for i in delp:
                	    	i.delete()
                	    print("deleted all prev")
                except Exception as e:
                	pass
                	
               
                try:
                	qs = Collection.objects.get(collname = collname, client= self.request.user, uploading=False)
                except Exception as e:
                	qs = None
                	
                	
                if qs != None:
                	print("name clash")
                	return JsonResponse({'error': True, 'errors': {'name':'this','error':'Error , A folder with this name already exist, use a different name!'}})
                
                
                try:
                	qs1 = Collection.objects.all().filter( client = self.request.user, job_status='Pending',  uploading = False)
                except:
                	qs1 = None
                	
                	
                	
                if len(qs1) > 0 :
                	
                	return JsonResponse({'error': True, 'errors': {'name':'this','error':'You already uploaded a folder, make payment for it at payment page or delete it from pending orders to create another one!!!'}})
                    
                else:
                	pass
                if upload_done == "True":
                	try:
                	    qs2= Collection.objects.get(collname= collname, client= self.request.user, job_status = "Pending", uploading= True)
                	except:
                		qs2 = None
                		
                	if qs2:
                	    qs2.uploading = False
                	    qs2.save()
                	    print("complete")
                	    return JsonResponse({'error': False, 'message': 'Uploaded set complete.'})
                
                if upload_done == "False":
                    try: 
                        qs2 = Collection.objects.get(collname= collname, client= self.request.user, job_status = "Pending", uploading = True)
                    except:
                    	qs2 = None
                    	
                    	
                    if qs2 != None:
                    
                        for i in images:
                        	
                       
                        
                            b =os.path.splitext(i.name)
                        
                            print("imageeeeeeeeeeeee")
                            name= i.name
                            ext= b[1]

                        
                        #i= base64.b64encode(i.read())

                        # image = ImageFile(io.BytesIO(i), name='foo.jpg')
                            read_data = i.read()
                        # a = Images(user= self.request.user, imageby1 =read_data, imageby2 =read_data, imageby4 = base64.b64encode(read_data).decode('utf-8'), imageby3= base64.b64encode(read_data) , name= name, collection_name = album)
                            a = Images(user= self.request.user, imageby= base64.b64encode(read_data).decode('utf-8'), name= name, collection_name = qs2)
                            a.save()
                    else:
                        qss = get_object_or_404(User, username = self.request.user).profile
                        qsn = qss.phonenumber
                        album = Collection.objects.create(collname= collname, client = self.request.user, phonenumber=qsn)
                        for i in images:
                       
                        #print(i.content_type)
                            b =os.path.splitext(i.name)
                        #print(b)
                            print("imageeeeeeeeeeeee")
                            name= i.name
                            ext= b[1]

                        
                        #i= base64.b64encode(i.read())

                        # image = ImageFile(io.BytesIO(i), name='foo.jpg')
                            read_data = i.read()
                        # a = Images(user= self.request.user, imageby1 =read_data, imageby2 =read_data, imageby4 = base64.b64encode(read_data).decode('utf-8'), imageby3= base64.b64encode(read_data) , name= name, collection_name = album)
                            a = Images(user= self.request.user, imageby= base64.b64encode(read_data).decode('utf-8'), name= name, collection_name = album)
                            a.save()
                    print("returning success")
                    return JsonResponse({'error': False, 'message': 'Uploaded Successfully.'})
            except Exception as e:
            	print(e)
            	return JsonResponse({'error':True, 'errors':str(e)})
   
                 
                        
                       
def redirect_view(request, *args, **kwargs):
    if request.user.is_authenticated:
        messages.success(request, "Your order was successful, read instructions below on how make payment!")
        return redirect('typr_main:payment')
    return redirect("typr_users:login")
        

        # if self.request.user.is_authenticated:
        #     if self.request.method =="POST":
        #         collname = self.request.POST['collection']
        #         images = self.request.FILES.getlist('images')
        #         try:
        #             cqs   = Collection.objects.all().filter(client = self.request.user, job_status='Pending',  colldone="False")
        #         except:
        #             cqs ="None"
        #         if len(cqs) > 0 :
        #             try:
        #                 cnotifica = CustomNotification.objects.all().filter(user = self.request.user, viewed= False)
        #                 print(cnotifica, "heeeereeeee", len(cnotifica))
        #             except Exception as e:
        #                 cnotifica = None
        #             payment_count = 0
        #             order_count = 0
        #             in_progress_count = 0
        #             pending_count = 0
        #             completed_count = 0
        #             if cnotifica != None:
        #                 for a in cnotifica:
        #                     if a.target == "pending":
        #                         pending_count += 1
        #                     elif a.target == "order":
        #                         order_count += 1
        #                     elif a.target == "in_progress":
        #                         in_progress_count += 1
        #                     elif a.target == "completed":
        #                         completed_count += 1
        #                     elif a.target == "payment":
        #                         a.viewed = True
        #                         a.save()
        #                     else:
        #                         pass
                
        #             context = {
        #                 'pending_count':pending_count,
        #                 'in_progress_count': in_progress_count,
        #                 'completed_count':completed_count,
        #                 'payment_count':payment_count
        #                 }  

        #             messages.warning(self.request, "You already have an unpaid order folder, make payment or delete it from pending orders to make another one!!!")
        #             return render(self.request, 'typr_main/dashboard/order.html', context)
                
        #         try:
        #             q1 = Collection.objects.get(collname = collname, client =self.request.user)
        #             q1 = True
                    
        #         except:
        #             q1 = False
                
        #         if q1 == False:
        #             qs = get_object_or_404(User, username = self.request.user).profile
        #             qsn = qs.phonenumber
        #             album = Collection.objects.create(collname= collname, client = self.request.user, phonenumber=qsn)
        #             from io import StringIO
        #             for i in images:
                       
        #                 print(i.content_type)
        #                 b =os.path.splitext(i.name)
        #                 print(b)
        #                 print("imageeeeeeeeeeeee")
        #                 name= i.name
        #                 ext= b[1]

                       
        #                 #i= base64.b64encode(i.read())

        #                 # image = ImageFile(io.BytesIO(i), name='foo.jpg')
        #                 read_data = i.read()
        #                 # a = Images(user= self.request.user, imageby1 =read_data, imageby2 =read_data, imageby4 = base64.b64encode(read_data).decode('utf-8'), imageby3= base64.b64encode(read_data) , name= name, collection_name = album)
        #                 a = Images(user= self.request.user, imageby= base64.b64encode(read_data).decode('utf-8'), name= name, collection_name = album)
        #                 a.save()

                    
        #             messages.success(self.request, "Your order was successful, read instructions below on how make payment!")
        #             return redirect('typr_main:payment')
        #         if q1 == True:
        #             messages.warning(self.request, "Error , A folder with this name already exist, use a different name!")
        #             return render(self.request, 'typr_main/dashboard/order.html')

        # else:
        #     return redirect("typr_users:login")


class pending(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            try:
                cnotifica = CustomNotification.objects.all().filter(user = self.request.user, viewed= False)
            except Exception as e:
                cnotifica = None
    
            qs  = Collection.objects.all().filter(client = self.request.user, job_status='Pending',  colldone="False", uploading = False)
        
            order_count = 0
            in_progress_count = 0
            pending_count = 0
            completed_count = 0
            payment_count=0
            if cnotifica != None:
                for a in cnotifica:
                    if a.target == "pending":
                        a.viewed = True
                        a.save()
                    if a.target == "order":
                        a.viewed = True
                        a.save()
                    elif a.target == "in_progress":
                        in_progress_count += 1
                    elif a.target == "completed":
                        completed_count += 1
                    elif a.target == "payment":
                        payment_count += 1
                    else:
                        pass
            context = {
            'collection':qs,
            'pending_count':pending_count,
            'in_progress_count': in_progress_count,
            'completed_count':completed_count,
            'payment_count':payment_count
                }
   

            return render(self.request, "typr_main/dashboard/pending.html", context)
        return redirect("typr_users:login")

  
class in_progress(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            try:
                cnotifica = CustomNotification.objects.all().filter(user = self.request.user, viewed= False)
                print(cnotifica, "heeeereeeee", len(cnotifica))
            except Exception as e:
                cnotifica = None
                print(e, 'eeeeeeeeeeeeeeeer')
            qs  = Collection.objects.all().filter(client = self.request.user, job_status= "In progress")
            
            payment_count = 0
            order_count = 0
            in_progress_count = 0
            pending_count = 0
            completed_count = 0
            if cnotifica != None:
                for a in cnotifica:
                    if a.target == "pending":
                        pending_count += 1
                    elif a.target == "order":
                        order_count += 1
                    elif a.target == "in_progress":
                        a.viewed = True
                        a.save()
                    elif a.target == "completed":
                        completed_count += 1
                    elif a.target == "payment":
                        payment_count += 1
                    else:
                        pass
            context = {
                'collection':qs,
                'pending_count':pending_count,
                'in_progress_count': in_progress_count,
                'completed_count':completed_count,
                'payment_count':payment_count
            }
        
            return render(self.request, "typr_main/dashboard/in_progress.html", context)
        return redirect("typr_users:login")

  
class completed(View): 
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            qs  = Collection.objects.all().filter(client = self.request.user, colldone="True")

            try:
                cnotifica = CustomNotification.objects.all().filter(user = self.request.user, viewed= False)
                print(cnotifica, "heeeereeeee", len(cnotifica))
            except Exception as e:
                cnotifica = None
            payment_count = 0
            order_count = 0
            in_progress_count = 0
            pending_count = 0
            completed_count = 0
            if cnotifica != None:
                for a in cnotifica:
                    if a.target == "pending":
                        pending_count += 1
                    elif a.target == "order":
                        order_count += 1
                    elif a.target == "in_progress":
                        in_progress_count += 1
                    elif a.target == "completed":
                        a.viewed = True
                        a.save()
                    elif a.target == "payment":
                        payment_count += 1
                    else:
                        pass
        
            context = {
                'collection':qs,
                'pending_count':pending_count,
                'in_progress_count': in_progress_count,
                'completed_count':completed_count,
                'payment_count':payment_count
                }   

            return render(self.request, "typr_main/dashboard/completed.html", context)

        return redirect("typr_users:login")


class payment(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            try:
                qs  = Collection.objects.all().filter(client = self.request.user, job_status="Pending", paid_option=False )
            except:
                    qs= None
            if qs == None:
                return render(self.request, "typr_main/dashboard/payment.html")
            
            b = 0.00
            for a in qs:
                b += a.deposited_amount

            bb = 0.00
            for a in qs:
                bb += a.estimated_amount

            try:
                cnotifica = CustomNotification.objects.all().filter(user = self.request.user, viewed= False)
                print(cnotifica, "heeeereeeee", len(cnotifica))
            except Exception as e:
                cnotifica = None
            payment_count = 0
            order_count = 0
            in_progress_count = 0
            pending_count = 0
            completed_count = 0
            if cnotifica != None:
                for a in cnotifica:
                    if a.target == "pending":
                        pending_count += 1
                    elif a.target == "order":
                        order_count += 1
                    elif a.target == "in_progress":
                        in_progress_count += 1
                    elif a.target == "completed":
                        completed_count += 1 
                    elif a.target == "payment":
                        payment_count += 1 
                    else:
                        pass
        
            context = {
                'collection':qs,
                'dep':b,
                'total':bb,
                'pending_count':pending_count,
                'in_progress_count': in_progress_count,
                'completed_count':completed_count,
                'payment_count':payment_count
                }   

            return render(self.request, "typr_main/dashboard/payment.html", context)
        return redirect("typr_users:login")

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
             if self.request.method =="POST":
                images = self.request.FILES.getlist('images')
                ids = self.request.POST['color']
                try:
                    qs = Collection.objects.all().filter(client = self.request.user, job_status= "Pending")[0]
                    print(qs, 'qqqsssssssssssssssssss')
                except:
                    qs= None
                qsthis = Collection.objects.all().filter(client = self.request.user, job_status= "Pending")
                if qs != None:
                    for i in images:
                        b =os.path.splitext(i.name)
                        ext= b[1]
                        name= i.name
                        read_data = i.read()

                        a = ProofImages(user= self.request.user, imageby = base64.b64encode(read_data).decode('utf-8'), collection_name = qs, name=         name)
                        #base64.b64decode(a.imageby.encode("utf-8"))
                        a.save()

                    messages.success(self.request, "Proof uploaded successfully, Your typing will immediately begin after administrator confirms it.")
                    try:
                        cnotifica = CustomNotification.objects.all().filter(user = self.request.user, viewed= False)
                    except Exception as e:
                        cnotifica = None

                    b = qs.deposited_amount
                    # for a in qsthis:
                    #     b += a.deposited_amount

                    bb = qs.estimated_amount
                    # for a in qsthis:
                    #     bb += a.estimated_amount

                    payment_count = 0
                    order_count = 0
                    in_progress_count = 0
                    pending_count = 0
                    completed_count = 0
                    if cnotifica != None:
                        for a in cnotifica:
                            if a.target == "pending":
                                pending_count += 1
                            if a.target == "order":
                               order_count += 1
                            elif a.target == "in_progress":
                                in_progress_count += 1
                            elif a.target == "completed":
                                completed_count += 1
                            elif a.target == "payment":
                                payment_count += 1
                            else:
                                pass
                    context = {
                    'dep':b,
                    'total':bb,
                    'collection':qsthis,
                    'pending_count':pending_count,
                    'in_progress_count': in_progress_count,
                    'completed_count':completed_count,
                    'payment_count':payment_count
                        }
                    
                    return render(self.request, "typr_main/dashboard/payment.html", context)

                messages.error(self.request, "Error, proof not uploaded, try agian!") 
                return render(self.request, "typr_main/dashboard/payment.html")


from django.core.files.base import  File
from django.core.files.temp import NamedTemporaryFile
# def decodeDesignImage(data):
#     try:
#         data = base64.b64decode(data.encode('UTF-8'))
#         buf = io.BytesIO(data)
#         img = Image.open(buf)
#         return img
#     except:
#         return None
class typrDetailView(DetailView):
  
    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            id_ =self.kwargs['id']
            collection = get_object_or_404(Collection, id=id_)
            images = Images.objects.all().filter(user = self.request.user, collection_name = collection).order_by("id")
            c_files = Results.objects.all().filter(user = self.request.user, collection_name = collection, finished= True ).order_by("id")
            if collection.colldone == True and collection.job_status == "Finished":
                file_check = True 
            else:
                file_check = False
            
            try:
                cnotifica = CustomNotification.objects.all().filter(user = self.request.user, viewed= False)
            except Exception as e:
                cnotifica = None

            dellthis=  ImgConvert.objects.all().filter(user = self.request.user, collection_name = collection).order_by("id")
            for a in dellthis:
                a.delete()

            fast =  Images.objects.all().filter(user = self.request.user, collection_name = collection).order_by("id")
      
                
            #fast_images= [{"id":x.id, "imageby": decodeDesignImage(x.imageby), "name": x.name, "typed": x.typed} for x in fast]
         
            for a in fast:
   

                try:
                   tmp = ImgConvert.objects.get(user= self.request.user,collection_name= collection, name=a.name, typed= a.typed)
                except Exception as e:
                    print(e)
                 
                    fileTemp = NamedTemporaryFile()
                    fileTemp.write(base64.b64decode(a.imageby.encode("utf-8")))
                    filename = a.name
                    file1 = File(fileTemp, name=filename)
                    tmp = ImgConvert.objects.create(user= self.request.user,collection_name= collection,imageby =file1, name=a.name, typed = a.typed)
               

            try:
                second_fast =ImgConvert.objects.all().filter(user = self.request.user, collection_name = collection).order_by("id")
                second_fast_len = len(second_fast)
            except:
                pass
            payment_count = 0
            order_count = 0
            in_progress_count = 0
            pending_count = 0
            completed_count = 0
            if cnotifica != None:
                for a in cnotifica:
                    if a.target == "pending":
                        pending_count += 1
                    elif a.target == "order":
                        order_count += 1
                    elif a.target == "in_progress":
                        in_progress_count += 1
                    elif a.target == "completed":
                        completed_count += 1
                    elif a.target == "payment":
                        payment_count += 1
                    else:
                        pass

            context = {
                    'collection':collection,
                    'c_files':c_files,
                    'file_check': file_check,
                    'pending_count':pending_count,
                    'in_progress_count': in_progress_count,
                    'completed_count':completed_count,
                    'payment_count':payment_count,
                    'second_fast':second_fast,
                    'len':second_fast_len
                
                
                }
           
            return render(self.request, "typr_main/dashboard/typr_detail.html", context)
        return redirect("typr_users:login")
    

class super_pending(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                qs = Collection.objects.all().filter(job_status="Pending", paid_option=False)
                context  = {
                'collection':qs,
                   }   
                return render(self.request, "typr_main/dashboard/super_pending.html", context)
        return redirect("typr_users:login")

class super_paid(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                qs = Collection.objects.all().filter(job_status= "In progress", paid_option= True)
                context  = {
                'collection':qs,
                   }   
                return render(self.request, "typr_main/dashboard/super_paid.html", context)
        return redirect("typr_users:login")

class super_completed(View):

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                qs = Collection.objects.all().filter(colldone= True)
                context  = {
                'collection':qs,
                }   
                return render(self.request, "typr_main/dashboard/super_completed.html", context)
        return redirect("typr_users:login")

class superDetailView(DetailView):

    
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                id_ =self.kwargs['id']
                collection = get_object_or_404(Collection, id=id_)
                images = Images.objects.all().filter(collection_name = collection).order_by("id")

                dellthis=  ImgConvert.objects.all().filter(user=collection.client, collection_name = collection).order_by("id")
                for a in dellthis:
                    a.delete()
                fast =  Images.objects.all().filter(user=collection.client, collection_name = collection).order_by("id")

                for a in fast:
                    try:
                        tmp = ImgConvert.objects.get(collection_name= collection, user= collection.client, name= a.name, typed= a.typed, code= a.id)
                    except Exception as e:
                        print(e)
                    
                        fileTemp = NamedTemporaryFile()
                        fileTemp.write(base64.b64decode(a.imageby.encode("utf-8")))
                        filename = a.name
                        file1 = File(fileTemp, name=filename)
                        tmp = ImgConvert.objects.create(user= collection.client, collection_name= collection, imageby =file1, name=a.name, typed=a.typed, code= a.id)
               
                try:
                    second_fast =ImgConvert.objects.all().filter(user = collection.client, collection_name = collection).order_by("id")
                except:
                    pass
              
                form = AdminAmountForm()
                form2 = AdminPaidForm()
                form3 = AdminImageTyped()
                form4 = AdminCollectionDone()
                form5 = AdminAmountDepositForm()
                context = {
                        'collection':collection,
                        'form':form,
                        'form2':form2,
                        'form3':form3,
                        'form4':form4,
                        'form5':form5,
                        'second_fast':second_fast
                    
                    
                    }
                return render(self.request, "typr_main/dashboard/super_detail.html", context)
        return redirect("typr_users:login")

    def post(self,*args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                if self.request.method =="POST":
                    print(self.request.POST)

                  
                    if 'estimated_amount' in self.request.POST:
                        form = AdminAmountForm(self.request.POST)
                        if form.is_valid():
                            esamount = self.request.POST['estimated_amount']
                            id_ = self.request.POST['code']
                            qs = Collection.objects.get(id = id_)
                            qs.estimated_amount = float(esamount)
                            qs.save()
                            messages.success(self.request, "Estimated amount set successfully")
                            return redirect("typr_main:super_detail", id_)
                        messages.warning(self.request, "Error, estimated amount not set!")
                        return redirect("typr_main:super_pending")

                    if 'paid_option' in self.request.POST:
                        form = AdminPaidForm(self.request.POST)
                        if form.is_valid():
                            po = self.request.POST['paid_option']
                            id_ = self.request.POST['code']
                            qs = Collection.objects.get(id = id_)
                            qs.paid_option = po
                           
                            if po == "True":
                                qs.job_status = "In progress"
                                try:
                                    notifica = CustomNotification.objects.get(user= qs.client,  target= "in_progress", name = qs.collname)
                                    notifica.viewed = "False"
                                    notifica.save()
                                except:
                                    notifica = CustomNotification.objects.create(user= qs.client, viewed = False, target= "in_progress", name = qs.collname)

                            if po == "False":
                                qs.job_status = "Pending"
                                try:
                                    notifica = CustomNotification.objects.get(user= qs.client, target= "in_progress", name= qs.collname)
                                    notifica.viewed = "True"
                                    notifica.save()
                                except:
                                    pass
                            
                            qs.save()
                            messages.success(self.request, "paid option set successfuly")
                            return redirect("typr_main:super_detail", id_)
                        messages.warning(self.request, "Error, paid option not set!")
                        return redirect("typr_main:super_pending")

                    if 'typed' in self.request.POST:
                        form = AdminImageTyped(self.request.POST)
                        if form.is_valid():
                            po = self.request.POST['typed']
                            id_ = self.request.POST['code']
                            iddd_ = self.request.POST['codedd']
                            qs = Images.objects.get(id = id_)
                            qs.typed = po
                            qs.save()
                            messages.success(self.request, "Typed option Set successfully")
                            return redirect("typr_main:super_detail", iddd_)
                        messages.warning(self.request, "Error, typed option not set!")
                        return redirect("typr_main:super_pending")

                    if 'done' in self.request.POST:
                        form = AdminCollectionDone(self.request.POST)
                        if form.is_valid():
                            po = self.request.POST['done']
                            id_ = self.request.POST['code']
                            qs = Collection.objects.get(id = id_)
                            if po == "True":
                                qs.colldone = "True"
                                qs.job_status = "Finished"
                                qs.save()
                                try:
                                    notifica = CustomNotification.objects.get(user= qs.client,  target= "completed", name = qs.collname)
                                    notifica.viewed = "False"
                                    notifica.save()
                                except:
                                    notifica = CustomNotification.objects.create(user= qs.client, viewed = False, target= "completed", name = qs.collname)
                            if po == "False":
                                qs.colldone = "False"
                                qs.job_status = "In progress"
                                qs.save()
                                try:
                                    notifica = CustomNotification.objects.get(user= qs.client, target= "completed", name= qs.collname)
                                    notifica.viewed = "False"
                                    notifica.save()
                                except:
                                    pass
                            
                               
                            

                            messages.success(self.request, "Set collection status successfully")
                            return redirect("typr_main:super_detail", id_)
                        messages.warning(self.request, "Error, collection status not set!")
                        return redirect("typr_main:super_pending")
                            

                    if 'deposit' in self.request.POST:
                        form = AdminAmountDepositForm(self.request.POST)
                        if form.is_valid():
                            esamount = self.request.POST['deposit']
                            id_ = self.request.POST['code']
                            qs = Collection.objects.get(id = id_)
                            qs.deposited_amount = float(esamount)
                            qs.save()
                            messages.success(self.request, "Amount deposited successfully")
                            return redirect("typr_main:super_detail", id_)
                        messages.warning(self.request, "Error, amount deposit failed!")
                        return redirect("typr_main:super_pending")

                    

                    if "thiscode" in self.request.POST:
                        code = self.request.POST['thiscode']
                        files = self.request.FILES.getlist('docs')
                        col = get_object_or_404(Collection, id= code)
                        if col:
                            for i in files:
                                b =os.path.splitext(i.name)
                                exto= b[1]
                                ext= exto[1:]
                                name= i.name
                                read_data = i.read()

                                a = Results( user = col.client, collection_name= col, c_file = base64.b64encode(read_data).decode('utf-8'), finished=       True , name=name, ext= ext)
                                a.save()
                            
                            messages.success(self.request, "Files saved successfully")
                            return redirect("typr_main:super_detail", code)
                        messages.warning(self.request, "Error, File save failed!")
                        return redirect("typr_main:super_pending")

        return redirect("typr_users:login")

     


class super_delete(DeleteView):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                id_ =self.kwargs['id']
                collection = get_object_or_404(Collection, id=id_)
                collection.delete()
                messages.success(self.request, "Collection deleted!")
                return redirect("typr_main:super_pending")
        return redirect("typr_users:login")
    
class super_delete_file(DeleteView):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.is_superuser:
                id_ =self.kwargs['id']
                
                qs = Results.objects.all().filter(id =id_)[0]
                qsname= qs.collection_name.collname
                thisto = Collection.objects.all().filter(collname= qsname)[0]
                this_id = thisto.id
                qs.delete()
                messages.success(self.request, "File deleted!")
                return redirect("typr_main:super_detail", this_id)
        return redirect("typr_users:login")
    

def u_profile(request, *args, **kwargs):
    if request.user.is_authenticated:
        try:
            cnotifica = CustomNotification.objects.all().filter(user = request.user, viewed= False)
            print(cnotifica, len(cnotifica), ",,,,,,,,,,,,,,,,,,,,,,,,,,,,")
        except Exception as e:
                cnotifica = None
                print(e, '''''''''''''''''''''''''')

        payment_count = 0
        order_count = 0
        in_progress_count = 0
        pending_count = 0
        completed_count = 0
        if cnotifica != None:
            for a in cnotifica:
                if a.target == "pending":
                    pending_count += 1
                elif a.target == "order":
                    order_count += 1
                elif a.target == "in_progress":
                    in_progress_count += 1
                elif a.target == "completed":
                    completed_count += 1
                elif a.target == "payment":
                    payment_count += 1
                else:
                    pass
        context = {
            'pending_count':pending_count,
            'in_progress_count': in_progress_count,
            'completed_count':completed_count,
            'payment_count':payment_count
        }
        return render(request, "typr_users/profile.html", context)
    return redirect("typr_users:login")


class u_settings(View):
    def get(self, *args, **kwargs):
    
        if self.request.user.is_authenticated:
            form1 = UserUpdateEmailForm(instance= self.request.user)
            form2 = UserUpdatePhone()


            try:
                cnotifica = CustomNotification.objects.all().filter(user = self.request.user, viewed= False)
                print(cnotifica, len(cnotifica), ",,,,,,,,,,,,,,,,,,,,,,,,,,,,")
            except Exception as e:
                cnotifica = None
                print(e, '''''''''''''''''''''''''')

            payment_count = 0
            order_count = 0
            in_progress_count = 0
            pending_count = 0
            completed_count = 0
            if cnotifica != None:
                for a in cnotifica:
                    if a.target == "pending":
                        pending_count += 1
                    elif a.target == "order":
                        order_count += 1
                    elif a.target == "in_progress":
                        in_progress_count += 1
                    elif a.target == "completed":
                        completed_count += 1
                    elif a.target == "payment":
                        payment_count += 1
                    else:
                        pass
            context = {
                'form1':form1,
                'form2': form2,
                'pending_count':pending_count,
                'in_progress_count': in_progress_count,
                'completed_count':completed_count,
                'payment_count':payment_count
            }
        
            return render(self.request, "typr_users/settings.html", context)
        return redirect("typr_users:login")

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.method =="POST":
                print(self.request.POST)
             
                if  'email' in self.request.POST:
                    form = UserUpdateEmailForm(self.request.POST, instance=self.request.user)
                    if form.is_valid():
                        #email= self.request.POST['email']
                       # c= User.objects.get(username=self.request.user)
                        #c.email = email
                        #c.save()
                        form.save()
                        messages.success(self.request, "Email updated successfully!")
                        return redirect("typr_main:u_settings")
                    messages.warning(self.request, "Error, email not updated!")
                    return redirect("typr_main:u_settings")

                if 'phone' in self.request.POST:
                    form = UserUpdatePhone(self.request.POST)
                    if form.is_valid():
                        phone = self.request.POST['phone']
                        if len(phone) < 10 or phone[0] != '0':
                            messages.warning(self.request, "Invalid phone number!")
                            return redirect("typr_main:u_settings")

                        c= Profile.objects.get(user=self.request.user)
                        c.phonenumber = int(phone)
                        c.save()
                        qs = Collection.objects.all().filter(client= self.request.user)
                        for g in qs:
                            g.phonenumber = phone
                            g.save()
                        messages.success(self.request, "Phone number updated successfully!")
                        return redirect("typr_main:u_settings")

                    print(form.errors)
                    messages.warning(self.request, "Error, phone number not updated!")
                    return redirect("typr_main:u_settings")

                if 'gender' in self.request.POST:
    
                    gender = self.request.POST['gender']
                    gender = gender.lower()
                    if gender == "male" or gender == "female":
                        c= Profile.objects.get(user=self.request.user)
                        c.gender = gender
                        c.save()
                        messages.success(self.request, "Gender updated successfully!")
                        return redirect("typr_main:u_settings")
                    messages.warning(self.request, "Invalid gender!")
                    return redirect("typr_main:u_settings")

                   

                messages.warning(self.request, "Error, try again later!")
                return redirect("typr_main:u_settings")
                

        return redirect("typr_users:login")