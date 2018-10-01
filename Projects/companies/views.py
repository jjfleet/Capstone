from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import CompanyListing
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from companies.forms import CompanyCreateView, CompanyUpdateForm
from django.urls import reverse

@login_required
def companyCreate(request):
	if request.method == 'POST':
		form = CompanyCreateView(request.POST)
		if form.is_valid():
			form.instance.author = request.user
			comp = form.save()
			messages.success(request, "Your company has been created!")
			return redirect(reverse('company-detail', kwargs={'pk': comp.pk}))
	else:
		form = CompanyCreateView()
	return render(request, 'companies/companylisting_form.html', {'form': form})

class CompanyPageView(ListView):
	model = CompanyListing
	template_name = 'companies/company.html'
	context_object_name = 'data'
	ordering = ['-date_posted']

class UserCompanyPageView(ListView):
	model = CompanyListing
	template_name = 'companies/user_company.html'
	context_object_name = 'data'
	paginate_by = 3

	def get_queryset(self):
		user = get_object_or_404(User, username=self.kwargs.get('username'))
		return CompanyListing.objects.filter(author=user).order_by('-date_posted')


<<<<<<< HEAD
def CompanyUpdateView(request, pk):
=======
def CompanyUpdateView(request, **kwargs):
>>>>>>> 57009736c9b148fd3b1dd012ba3c33c0d844a86e
	if request.method  == 'POST':
		c_form = CompanyUpdateForm(request.POST)
		if c_form.is_valid():
			c_form.instance.author = request.user
			camp = c_form.save()
			messages.success(request, "Your Company has been updated!")
			return redirect(reverse('company-detail', kwargs={'pk': camp.pk}))
	else:
<<<<<<< HEAD
		c_form = CompanyUpdateForm(instance = CompanyListing.objects.get(pk=pk))
=======
		c_form = CompanyUpdateForm(instance=CompanyListing.objects.get())
>>>>>>> 57009736c9b148fd3b1dd012ba3c33c0d844a86e
	return render(request, 'companies/companyupdate_form.html', {'c_form': c_form})


class CompanyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
	model = CompanyListing
	success_url = '/'
	def test_func(self):
		company = self.get_object()
		return self.request.user == company.author


class CompanyDetailView(DetailView):
	model = CompanyListing
