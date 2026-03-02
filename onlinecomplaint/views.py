from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserRegister   # model correct name use pannunga
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from .models import Complaint
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,date 
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test





def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if UserRegister.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        # ✅ EMAIL CHECK (IMPORTANT)
        if UserRegister.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        UserRegister.objects.create(
            username=username,
            email=email,
            phone=phone,
            password=make_password(password)
        )

        User.objects.create_user(
             username=username,
             email=email,
             password=password
)         

        try:
            send_mail(
                'Welcome to Online Complaint System',
                f'Hi {username},\n\nYour account has been successfully created!',
                'ResolveX0510@gmail.com',
                [email],
                fail_silently=False
            )
        except Exception as e:
            messages.warning(request, f"Registered but email failed: {e}")

        messages.success(request, "Registration successful! Please login.")
        return redirect('userlogin')

    return render(request, 'userregister.html')


def userlogin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 🔹 Step 1: User exists-aa nu check
        if not UserRegister.objects.filter(username=username).exists():
            messages.error(request, "User not registered",extra_tags='login')
            return render(request, 'index.html')

        # 🔹 Step 2: Authenticate password
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Wrong password",extra_tags='login')
            return render(request, 'index.html')

        # 🔹 Step 3: Proper Django login
        login(request, user)
        return redirect('complaintportal')

    return redirect('index')

    

def forgotpassword(request):
    if request.method == "POST":
        identifier = request.POST.get('username')  # user can enter username or email

        try:
            # Try to get user by username or email
            user = UserRegister.objects.get(username=identifier)
        except UserRegister.DoesNotExist:
            try:
                user = UserRegister.objects.get(email=identifier)
            except UserRegister.DoesNotExist:
                messages.error(request, "User not found")
                return redirect('userlogin')

        # Generate OTP
        otp = random.randint(100000, 999999)
        request.session['otp'] = otp
        request.session['reset_user'] = user.username

        try:
            # Send OTP email
            send_mail(
                'Password Reset OTP',
                f'Your OTP is {otp}',
                'yourmail@gmail.com',  # Replace with your real email / DEFAULT_FROM_EMAIL
                [user.email],
                fail_silently=False,   # Show error if email fails
            )
            messages.success(request, f"OTP sent to {user.email} successfully")
            return redirect('verifyotp')

        except Exception as e:
            messages.error(request, f"Could not send email: {e}")
            return redirect('forgotpassword')

    return render(request, 'index.html')

def verifyotp(request):
    if request.method == "POST":
        if request.POST.get('otp') == str(request.session.get('otp')):
            return redirect('resetpassword')
        else:
            messages.error(request, "Invalid OTP")
            return redirect('verifyotp')
    return render(request, 'verifyotp.html')

def resetpassword(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('resetpassword')

        # Get the user who requested password reset
        username = request.session.get('reset_user')
        if not username:
            messages.error(request, "Session expired. Please try again.")
            return redirect('forgotpassword')

        user = UserRegister.objects.get(username=username)

        # Update password with hashing
        user.password = make_password(password)
        user.save()
        
        try:
            django_user = User.objects.get(username=username)
            django_user.set_password(password)   # proper hash
            django_user.save()
        except User.DoesNotExist:
            pass

        # Clear the session variables
        request.session.pop('reset_user', None)
        request.session.pop('otp', None)

        messages.success(request, "Password updated successfully! Please login.")
        return redirect('userlogin')

    return render(request, 'resetpassword.html')

@login_required
def edit_profile(request):

    profile, created = UserRegister.objects.get_or_create(
        email=request.user.email,
        defaults={
            'username': request.user.username,
            'phone': ''
        }
    )

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Update UserRegister
        profile.username = username
        profile.email = email
        profile.phone = phone
        profile.save()

        # Update Django User
        request.user.username = username
        request.user.email = email
        request.user.save()

        messages.success(request, "Profile updated successfully!", extra_tags='profile')

        # ✅ IMPORTANT: complaints fetch pannanum
        complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')

        return render(request, 'complaintportal.html', {
            'profile': profile,
            'complaints': complaints,   # ✅ ADD THIS
            'show_edit': True
        })

    # GET request
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'complaintportal.html', {
        'profile': profile,
        'complaints': complaints     # ✅ ADD THIS
    })



@login_required
def submit_complaint(request):
    if request.method == "POST":
        title = request.POST.get('title')
        category = request.POST.get('category')
        place = request.POST.get('place')
        description = request.POST.get('description')
        issue_date = request.POST.get('issue_date')  # string
        attachment = request.FILES.get('attachment')

        if issue_date:
            issue_date = datetime.strptime(issue_date, "%Y-%m-%d").date()
        else:
            issue_date = None

        # Save complaint in DB
        complaint = Complaint.objects.create(
            user=request.user,
            title=title,
            category=category,
            place=place,
            description=description,
            attachment=attachment,
            issue_date=issue_date,
            status="Pending"
        )

        # Send email notification
        try:
            send_mail(
                subject=f"Complaint Submitted: {title}",
                message=f"Hi {request.user.username},\n\nYour complaint has been submitted successfully!\n\n"
                        f"Title: {title}\n"
                        f"Category: {category}\n"
                        f"Status: {complaint.status}\n"
                        f"Issue Date: {issue_date}\n\n"
                        f"Place: {place}\n\n"
                        "We will update you once the status changes.",
                from_email='ResolveX0510@gmail.com',  # your EMAIL_HOST_USER
                recipient_list=[request.user.email],
                fail_silently=False
            )
        except Exception as e:
            messages.warning(request, f"Complaint submitted but email could not be sent: {e}",extra_tags="complaint")
        else:
            messages.success(request, "Your complaint submitted successfully! Confirmation email sent.",extra_tags="complaint")
            return redirect('complaintportal')
    return redirect('complaintportal')

@login_required
def complaintportal(request):
    try:
        profile = UserRegister.objects.filter(email=request.user.email).first()
    except UserRegister.DoesNotExist:
        # Optional: create profile only if needed, but check email first
        if UserRegister.objects.filter(email=request.user.email).exists():
            profile = UserRegister.objects.get(email=request.user.email)
        else:
            profile = UserRegister.objects.create(
                username=request.user.username,
                email=request.user.email,
                phone=''
            )

    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'complaintportal.html', {
        'complaints': complaints,
        'profile': profile
    })


from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse

@login_required
def complaint_status(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    # 🔒 If admin → allow view
    if request.user.is_staff:
        return render(request, 'complaint_status.html', {'complaint': complaint})

    # 🔒 If normal user → check ownership
    if complaint.user != request.user:
        messages.error(request, "You are not allowed to view this complaint.")
        return redirect('complaintportal')

    return render(request, 'complaint_status.html', {'complaint': complaint})


@login_required
def edit_complaint(request, id):
    complaint = Complaint.objects.get(id=id, user=request.user)

    # 🔒 Status check
    if complaint.status != "Pending":
        messages.error(request, "You cannot edit this complaint.")
        return redirect('complaintportal')

    if request.method == "POST":
        complaint.title = request.POST.get('title')
        complaint.category = request.POST.get('category')
        complaint.place = request.POST.get('place')
        complaint.description = request.POST.get('description')
       
        issue_date = request.POST.get('issue_date')


        if issue_date:
           complaint.issue_date = datetime.strptime(issue_date, "%Y-%m-%d").date()
        

           # ❌ REMOVE attachment
        if request.POST.get('remove_attachment'):
           if complaint.attachment:
              complaint.attachment.delete(save=False)
              complaint.attachment = None

        if request.FILES.get('attachment'):
            complaint.attachment = request.FILES['attachment']
        
        complaint.save()

        messages.success(request, "Complaint updated successfully!", extra_tags="complaint")
        return redirect('complaintportal')
        

       

    complaints = Complaint.objects.filter(user=request.user)

    return render(request, 'complaintportal.html', {
        'edit_complaint': complaint,   # 🔥 important
        'complaints': complaints,
        'today': date.today(),
    })


@login_required
def delete_complaint(request, id):
    try:
        complaint = Complaint.objects.get(id=id, user=request.user)
    except Complaint.DoesNotExist:
        messages.error(request, "Complaint not found.")
        return redirect('complaintportal')

    # Only allow delete if status is Pending
    if complaint.status != "Pending":
        messages.error(request, "You cannot delete this complaint.")
        return redirect('complaintportal')

    complaint.delete()
    messages.success(request, "Complaint deleted successfully!", extra_tags="complaint")
    return redirect('complaintportal')


def userlogout(request):
    logout(request)
    return redirect('userlogin')



def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_user'):
            messages.error(request, "Admin login required")
            return redirect('adminlogin')
        return view_func(request, *args, **kwargs)
    return wrapper

def adminlogin(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        password = request.POST.get('password').strip()

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid admin credentials")
            return redirect('adminlogin')

        if not user.is_staff:
            messages.error(request, "You are not an admin")
            return redirect('adminlogin')

        login(request, user)
        return redirect('admindashboard')
       

    return render(request, "adminlogin.html")


def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admindashboard(request):
    # 🔒 Make sure only admin session users can access
    

    # Fetch all users and complaints
    users = UserRegister.objects.all()
    complaints = Complaint.objects.all()
    
    # Pending complaints count
    pending_count = Complaint.objects.filter(status='Pending').count()

    resolved_count = Complaint.objects.filter(status='Resolved').count()

    # Admin info from session
    admin_user = request.session.get('admin_user')  

    return render(request, "admindashboard.html", {
        'users': users,
        'complaints': complaints,
        'pending_count': pending_count,
        'resolved_count': resolved_count,
        'admin_user': request.user.username,
        'admin':request.user
    })

from django.contrib import messages
from django.shortcuts import redirect

@login_required
@user_passes_test(is_admin)
def admin_edit_profile(request):

    django_user = request.user
    profile = UserRegister.objects.filter(email=django_user.email).first()

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if UserRegister.objects.exclude(id=profile.id).filter(username=username).exists():
            messages.error(request, "Username already exists")
        else:
            profile.username = username
            profile.email = email
            profile.phone = phone
            profile.save()

            django_user.username = username
            django_user.email = email
            django_user.save()

            messages.success(request, "Profile updated successfully", extra_tags='profile')

        return redirect('admindashboard')

    return redirect('admindashboard')


       

# Admin Logout
def adminlogout(request):
    request.session.pop('admin_user', None)
    messages.success(request, "Admin logged out successfully")
    return redirect('adminlogin')



def admin_edit_complaint(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    old_status = complaint.status

    if request.method == "POST":
        complaint.title = request.POST.get('title')
        complaint.category = request.POST.get('category')
        complaint.place = request.POST.get('place')
        complaint.description = request.POST.get('description')
        complaint.status = request.POST.get('status')
        complaint.save()

         # ✅ Mail check & send
        if old_status != complaint.status and complaint.status.lower() == "resolved":
            try:
                status_url = request.build_absolute_uri(
                    reverse('complaint_status', args=[complaint.id])
                )
                send_mail(
                    subject="Your Complaint Has Been Resolved ✅",
                    message=f"""
Hello {complaint.user.username},

Your complaint "{complaint.title}" has been RESOLVED.

👉 Check your complaint status here:
{status_url}

Thank you for using our service.
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[complaint.user.email],
                    fail_silently=False,
                )
                messages.success(request, "Complaint updated & email sent successfully!",extra_tags='complaint1')
            except Exception as e:
                messages.warning(request, f"Complaint updated but email NOT sent: {e}",extra_tags='complaint1')

        else:
          messages.success(request, "Complaint updated successfully!",extra_tags='complaint1')
        
        return redirect('admin_edit_complaint',id=complaint.id)

    return render(request, 'admin_edit_complaint.html', {'complaint': complaint})
       
       

# Admin delete complaint
@login_required
@user_passes_test(is_admin)
def admin_delete_complaint(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    if request.method == "POST":
        complaint.delete()
        messages.success(request, "Complaint deleted successfully!",extra_tags='complaint2')
        return render(request, "admin_delete_complaint.html")

    return render(request, "admin_delete_complaint.html", {"complaint": complaint})    

def admin_edit_user(request, id):
    user = get_object_or_404(UserRegister, id=id)

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        # Update user details
        user.username = username
        user.email = email
        user.phone = phone
        user.save()
        messages.success(request, "User details updated successfully!",extra_tags='user')
        

    return render(request, "admin_edit_user.html", {"user": user})


# Delete User
@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, id):

    user = get_object_or_404(UserRegister, id=id)
    
    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully!",extra_tags='user1')
        return render(request, "admin_delete_user.html")

    return render(request, "admin_delete_user.html", {"user": user})