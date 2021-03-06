from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags

from email.mime.image import MIMEImage

from jobs.models import JobListing
from companies.models import CompanyListing
from consultants.models import ConsultantListing
from groups.models import GroupListing
from events.models import EventListing
from django.db.models import Value, CharField, Q

from .models import NewsletterUser, Newsletter
from .forms import NewsletterUserSignUpForm, NewsletterCreationForm


# Create a Newsletter
def control_newsletter(request):
	jobs = JobListing.objects.all().order_by('-date_posted').annotate(type=Value('job', CharField()))
	companies = CompanyListing.objects.all().order_by('-date_posted').annotate(type=Value('company', CharField()))
	events = EventListing.objects.all().order_by('-date_posted').annotate(type=Value('event', CharField()))
	groups = GroupListing.objects.all().order_by('-date_posted').annotate(type=Value('group', CharField()))
	consultants = ConsultantListing.objects.all().order_by('-date_posted').annotate(type=Value('consultant', CharField()))

	results = list(jobs) + list(events) + list(companies) + list(groups) + list(consultants)
	results = sorted(results, key=lambda obj: obj.date_posted, reverse=True)

	form = NewsletterCreationForm(request.POST or None)
	if form.is_valid():
		instance = form.save()
		newsletter = Newsletter.objects.get(id=instance.id)
		if newsletter.status == "Send":
			subject, from_email, body = newsletter.subject, settings.EMAIL_HOST_USER, newsletter.body
			for newsletteruser in newsletter.email.all():
				mail = EmailMultiAlternatives(subject=subject,to=[newsletteruser.email], from_email=from_email)
				mail.attach_alternative(render_to_string('newsletters/newsletter_template.html', {'all_items_feed': results}), "text/html")
				mail.send()
			messages.success(request, 'The newsletter has been created and sent!', 'alert alert-success alert-dismissable')
			return redirect('control_newsletter_list')
		elif newsletter.status == "Draft":
			messages.success(request, 'The newsletter draft has been saved!', 'alert alert-success alert-dismissable')
			return redirect('control_newsletter_list')
	context = {
		"form": form,
	}
	template = 'control_panel/control_newsletter.html'
	return render(request, template, context)

# Edit a Newsletter
def control_newsletter_edit(request, pk):
	jobs = JobListing.objects.all().order_by('-date_posted').annotate(type=Value('job', CharField()))
	companies = CompanyListing.objects.all().order_by('-date_posted').annotate(type=Value('company', CharField()))
	events = EventListing.objects.all().order_by('-date_posted').annotate(type=Value('event', CharField()))
	groups = GroupListing.objects.all().order_by('-date_posted').annotate(type=Value('group', CharField()))
	consultants = ConsultantListing.objects.all().order_by('-date_posted').annotate(type=Value('consultant', CharField()))

	results = list(jobs) + list(events) + list(companies) + list(groups) + list(consultants)
	results = sorted(results, key=lambda obj: obj.date_posted, reverse=True)

	newsletter = get_object_or_404(Newsletter, pk=pk)

	if request.method == "POST":
		form = NewsletterCreationForm(request.POST, instance=newsletter)
		if form.is_valid():
			newsletter = form.save()
			if newsletter.status == 'Send':
				subject, from_email, body = newsletter.subject, settings.EMAIL_HOST_USER, newsletter.body
				for newsletteruser in newsletter.email.all():
					mail = EmailMultiAlternatives(subject=subject,to=[newsletteruser.email], from_email=from_email)
					mail.attach_alternative(render_to_string('newsletters/newsletter_template.html', {'all_items_feed': results}), "text/html")
					mail.send()
				messages.success(request, 'The newsletter has been sent!', 'alert alert-success alert-dismissable')
				return redirect('control_newsletter_list')
			elif newsletter.status == "Draft":
				messages.success(request, 'The newsletter draft has been saved!', 'alert alert-success alert-dismissable')
				return redirect('control_newsletter_list')
	else:
		form = NewsletterCreationForm(instance=newsletter)

	context = {
		"form": form,
	}

	template = 'control_panel/control_newsletter.html'
	return render(request, template, context)


# Newsletter Sign Up
def newsletter_signup(request):
	s_form = NewsletterUserSignUpForm(request.POST or None)
	if s_form.is_valid():
		instance = s_form.save(commit=False)
		if NewsletterUser.objects.filter(email=instance.email).exists():
			messages.warning(request, 'Your email is already signed up to the newsletter', 'alert alert-warning alert-dismissable')
		else:
			instance.save()
			messages.success(request, 'You have been subscribed to the newsletter', 'alert alert-success alert-dismissable')
			subject = "Tech Palmy Newsletter"
			from_email = settings.EMAIL_HOST_USER
			to_email = [instance.email]
			message = EmailMultiAlternatives(subject=subject, from_email=from_email, to=to_email)
			html_template = get_template("newsletters/signup_email.html").render()
			message.attach_alternative(html_template, "text/html")
			message.send()
			return redirect('sites-home')

	context = {
		's_form': s_form,
	}
	template = 'newsletters/signup.html'
	return render(request, template, context)

# Newsletter Unsubscribe
def newsletter_unsubscribe(request):
	u_form = NewsletterUserSignUpForm(request.POST or None)
	if u_form.is_valid():
		instance = u_form.save(commit=False)
		if NewsletterUser.objects.filter(email=instance.email).exists():
			NewsletterUser.objects.filter(email=instance.email).delete()
			messages.success(request, 'You have successfully unsubscribed!', 'alert alert-success alert-dismissable')
			subject = "Tech Palmy Newsletter"
			from_email = settings.EMAIL_HOST_USER
			to_email = [instance.email]
			message = EmailMultiAlternatives(subject=subject, from_email=from_email, to=to_email)
			html_template = get_template("newsletters/unsubscribe_email.html").render()
			message.attach_alternative(html_template, "text/html")
			message.send()
			return redirect('sites-home')
		else:
			messages.warning(request, 'Your email is not curently subsrcibed!', 'alert alert-warning alert-dismissable')
	context = {
		'u_form': u_form,
	}
	template = 'newsletters/unsubscribe.html'
	return render(request, template, context)

# Display ALL Newsletters
def control_newsletter_list(request):
	newsletters = Newsletter.objects.all().order_by('-created')
	paginator = Paginator(newsletters, 5)
	page = (request.GET.get('page'))
	try:
		items = paginator.page(page)
	except PageNotAnInteger:
		items = paginator.page(1)
	except EmptyPage:
		items = paginator.page(paginator.num_pages)

	index = items.number - 1
	max_index = len(paginator.page_range)
	start_index = index - 5 if index >= max_index -5 else 0
	end_index = index + 5 if index <= max_index -5 else max_index
	page_range = paginator.page_range[start_index:end_index]


	context = {
		"items": items,
		"page_range": page_range
	}
	template = "control_panel/control_newsletter_list.html"
	return render(request,template, context)

# Single Newsletter Detail
def control_newsletter_detail(request, pk):
	newsletter = get_object_or_404(Newsletter, pk=pk)

	context = {
	"newsletter": newsletter,
	}
	template = "control_panel/control_newsletter_detail.html"
	return render(request, template, context)

# Delete a Newsletter
def control_newsletter_delete(request, pk):
	newsletter = get_object_or_404(Newsletter, pk=pk)

	if request.method == "POST":
		form = NewsletterCreationForm(request.POST, instance=newsletter)
		if form.is_valid():
			newsletter.delete()
			messages.success(request, 'The newsletter has been deleted!', 'alert alert-success alert-dismissable')
			return redirect('control_newsletter_list')

	else:
		form = NewsletterCreationForm(instance=newsletter)

	context = {
		"form": form,
	}
	template = 'control_panel/control_newsletter_delete.html'
	return render(request, template, context)
