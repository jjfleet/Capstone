from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from sites.models import Companies
from sites.models import Post


class HomePageView(ListView):
	def get(self, request, **kwargs):
		data = Post.objects.all()
		args = {'data': data}
		return render(request, 'sites/index.html', args)

class ConsultantsPageView(TemplateView):
    template_name = "sites/consultants.html"

class CompaniesPageView(TemplateView):
    template_name = "sites/companies.html"

class EventsPageView(TemplateView):
    template_name = "sites/events.html"

class JobsPageView(TemplateView):
    template_name = "sites/jobs.html"

class GroupsPageView(TemplateView):
    template_name = "sites/groups.html"

class EducationPageView(TemplateView):
    template_name = "sites/education.html"

class AboutPageView(TemplateView):
    template_name = "sites/about.html"
