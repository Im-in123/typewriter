from django.urls import path


from .views import ( home,
                     dashboard,
                     order,
                     completed,
                     pending,
                     typrDetailView,
                     payment,
                     super_pending,
                     super_completed,
                     superDetailView,
                     super_paid,
                     in_progress,
                     super_delete,
                     u_profile,
                     u_settings,
                     notification,
                     deletecoll,
                     deletecoll2,
                     super_delete_file,
                     redirect_view
              
                     ) 
app_name = 'typr_main'

urlpatterns = [

    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('notification/<int:id>', notification, name='notification'),
    path('deletecoll/<int:id>', deletecoll, name='deletecoll'),
    path('deletecoll2/<int:id>', deletecoll2, name='deletecoll2'),
    path('order/', order.as_view(), name='order'),
    path('redirect/', redirect_view, name='redirect'),
    path('completed/', completed.as_view(), name='completed'),
    path('payment/', payment.as_view(), name='payment'),
    path('in_progress/', in_progress.as_view(), name='in_progress'),
    path('pending/', pending.as_view(), name='pending'),
    path('detail/<int:id>', typrDetailView.as_view() , name='typr_detail'),
    path('super_pending/', super_pending.as_view(), name='super_pending'),
    path('super_paid/', super_paid.as_view() , name='super_paid'),
    path('super_completed/', super_completed.as_view(), name='super_completed'),
    path('super_detail/<int:id>', superDetailView.as_view() , name='super_detail'),
    path('super_delete/<int:id>', super_delete.as_view(), name='super_delete'),
    path('super_delete_file/<int:id>', super_delete_file.as_view(), name='super_delete_file'),
    path('u_profile/', u_profile, name='profile'),
    path('u_settings/', u_settings.as_view(), name='u_settings'),
   
           ]


