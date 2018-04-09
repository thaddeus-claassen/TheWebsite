from django.contrib.auth.decorators import login_required;
from django.db.models.functions import Lower;
from rest_framework.renderers import JSONRenderer;
from django.utils.decorators import method_decorator;
from django.views.generic import TemplateView;
from notification.models import Notification;
from jobuser.serializers import PledgeSerializer, WorkSerializer;
from annoying.functions import get_object_or_None;
from update.serializers import UpdateSerializer;
from django.shortcuts import render, get_object_or_404, redirect;
from django.db.models import Q, F;
from jobuser.models import JobUser;
from update.models import Update, Image;
from .serializers import JobSerializer;
from filter.forms import PledgeFilterForm, WorkerFilterForm;
from django.http import HttpResponse, Http404;
from django.core import serializers;
from .models import Job, Tag, User;
from .forms import NewJobForm;
import json, re, math;

def home(request):
    tag = None;
    context = None;
    if ('tag' in request.GET):
        tag = request.GET['tag'];
        context = {
            'tag' : tag,
        };
    else:
        location = None;
        if ('location' in request.GET):
            location = request.GET['location'];
            context = {
                'location' : location,
            };
    return render(request, 'job/home.html', context);
    
def get_jobs(request):
    if (request.is_ajax()):
        jobs = findJobs(request.GET['search'], request.GET['sort'], request.GET['latitude'], request.GET['longitude'], request.GET['radius']);
        if (jobs == "Invalid Search"):
            return HttpResponse(jobs, content_type="application/json");
        else:
            numSearches =  int(request.GET['numSearches']);
            jobs = jobs[50 * (numSearches - 1):50 * numSearches];
            serializer = JobSerializer(jobs, many=True, context={'user' : request.user});
            json = JSONRenderer().render(serializer.data);
            return HttpResponse(json, content_type="application/json");
    else:
        return Http404();
        
def get_total_jobs(request):
    if (request.is_ajax()):
        total = {};
        jobs = findJobs(request.GET['search'], request.GET['sort'], request.GET['latitude'], request.GET['longitude'], request.GET['radius']);
        if (jobs == "Invalid Search"):
            total = "";
        else:
            total['total'] = len(jobs);
        return HttpResponse(json.dumps(total), content_type="application/json");
    else:
        return Http404();
        
def findJobs(search, sort, latitude_in_degrees_as_string, longitude_in_degrees_as_string, radius_in_miles_as_string):
    if (search == ""):
        jobs = Job.objects.all();
    else:
        if (re.match(r'^[A-Za-z0-9\s_]+$', search)):
            jobs = Job.objects.all();
            for word in search.split(" "):
                jobs = jobs.filter(Q(title__icontains=word) | Q(tag__tag__icontains=word));
        else:
            if (re.match(r'^[A-Za-z0-9\s_&\|\(\)~]+$', search)):
                jobs = get_jobs_from_custom_search(search);
            else:
                return "Invalid Search";
    jobs = jobs.distinct();
    sort_array = sort.split("-");
    if (latitude_in_degrees_as_string != "" and longitude_in_degrees_as_string != "" and radius_in_miles_as_string != ""):
        jobs = findJobsByRadius(jobs, float(latitude_in_degrees_as_string), float(longitude_in_degrees_as_string), float(radius_in_miles_as_string));
    if (sort_array[0] == 'created'):
        jobs = jobs.order_by('date');
    elif (sort_array[0] == 'pledging'):
        jobs = jobs.order_by('pledging');
    elif (sort_array[0] == 'working'):
        jobs = jobs.order_by('working');
    else:
        jobs = jobs.extra(select={'case_insensitive_title': 'lower(title)'}).order_by('case_insensitive_title');
    if (sort_array[1] == 'descending'):
        jobs = jobs[::-1];
    return jobs;
    
def get_jobs_from_custom_search(tags):
        return eval(re.sub(r'([a-zA-Z0-9_]+)', "Job.objects.filter(tag__tag__iexact='" + r'\1' + "')", tags));
    
def findJobsByRadius(jobs, latitude_in_degrees, longitude_in_degrees, radius_in_miles):
    radius_in_degrees = radius_in_miles / 69;
    latitude_in_radians = latitude_in_degrees * math.pi / 180;
    longitude_in_radians = longitude_in_degrees * math.pi / 180;
    radius_in_radians = radius_in_degrees * math.pi / 180;
    jobs = jobs.filter(latitude__range=(latitude_in_degrees - radius_in_degrees, latitude_in_degrees + radius_in_degrees));
    for job in jobs:
        lat = job.latitude * math.pi / 180;
        lon = job.longitude * math.pi / 180;
        RADIUS_OF_EARTH_IN_MILES = 3959;
        distance = RADIUS_OF_EARTH_IN_MILES * math.acos(math.sin(latitude_in_radians) * math.sin(lat) + math.cos(latitude_in_radians) * math.cos(lat) * math.cos(math.fabs(longitude_in_radians - lon))); #This is called the Spherical Law of Cosines and it is used to calculate distances on a sphere. (Note: Earth is not a sphere, thus this will have a margin of error, but it is small. Quicker computation speed compensates)
        if (distance > radius_in_miles):
            jobs = jobs.exclude(id=job.id);
    return jobs;
        
class DetailView(TemplateView):
    template_name = 'job/detail.html';
    
    def get(self, request, *args, **kwargs):
        job = get_object_or_404(Job, random_string=kwargs['job_random_string']);
        if (request.user.is_authenticated):
            if (Notification.objects.filter(user=request.user, job=job).exists()):
                Notification.objects.get(user=request.user, job=job).delete();
        return render(request, self.template_name, self.get_context_data(request, job=job));
        
    def post(self, request, *args, **kwargs):
        job = get_object_or_404(Job, random_string=job_random_string);
        if ('work' in request.POST):
            jobuser = get_object_or_None(JobUser, user=request.user, job=job);
            if (jobuser):
                jobuser = JobUser.create(jobuser=jobuser, work_status='Working');
                jobuse.save();
            else:
                jobuser.work_status = 'Working';
            return redirect('job:detail', job_random_string=job.random_string);
        elif ('finish' in request.POST):
            jobuser = get_object_or_404(JobUser, user=request.user, job=job);
            jobuser.work_status = 'Finished';
            return redirect('job:detail', job_random_string=job.random_string);
        else:
            return render(request, self.template_name, self.get_context_data(job=job));
    
    def get_context_data(self, request, **kwargs):
        job = kwargs['job'];
        pledging = JobUser.objects.filter(Q(job=job) & (Q(pledging__gt=0) | Q(paid__gt=0)));
        pledging_total = 0;
        for p in pledging:
            pledging_total = pledging_total + p.pledging;
        paid_total = 0;
        for p in pledging:
            paid_total = paid_total + p.paid;
        working = JobUser.objects.filter(job=job).exclude(work_status='');
        received_total = 0;
        for w in working:
            received_total = received_total + w.received;
        context = {
            'job': job,
            'updates' : Update.objects.filter(jobuser__job=job).order_by('date')[:50],
            'pledging' : pledging[:50],
            'pledging_total' : pledging.count(),
            'pledging_amount_total' : pledging_total,
            'paid_amount_total' : paid_total,
            'working' : working[:50],
            'working_total' : working.count(),
            'received_amount_total' : received_total,
        }
        if (request.user.is_authenticated):
            serializer = JobSerializer(Job.objects.filter(pk=job.pk), many=True, context={'user' : request.user});
            jobuser = JobUser.objects.filter(Q(user=request.user) & Q(job=job) & ~Q(work_status='')).first();
            payment_verification = False;
            if (jobuser):
                for pay in jobuser.misc_pay_receiver.all():
                    if (not pay.verified):
                        payment_verification = True;
                        break;
            context['jobuser'] = jobuser;
            context['payment_verification'] = payment_verification; 
        return context;
        
def add_to_detail_table(request, job_random_string):
    if (request.is_ajax()):
        job = get_object_or_404(Job, random_string=job_random_string);
        numSearches = int(request.GET['num_searches']);
        table = request.GET['table'];
        column = request.GET['column'];
        order = request.GET['order'];
        if (table == 'updates'):
            if (column == 'username' or column == 'date'):
                data = Update.objects.filter(jobuser__job=job);
            else:
                return Http404();
        elif (table == 'pledging'):
            if (column == 'username' or column == 'pledging' or column == 'paid'):
                data = JobUser.objects.filter(Q(job=job) & (Q(pledging__gt=0) | Q(paid__gt=0)));
            else:
                return Http404();
        elif (table == 'working'):
            if (column == 'username' or column == 'work_status' or column == 'received'):
                data = JobUser.objects.filter(job=job).exclude(work_status='');
            else:
                return Http404();
        if (column == 'username'):
            if (table == 'updates'):
                if (order == 'ascending'):
                    data = data.order_by(Lower('jobuser__user__username'))[50 * numSearches : 50 * (numSearches + 1)][::-1];
                else:
                    data = data.order_by(Lower('jobuser__user__username'))[50 * numSearches : 50 * (numSearches + 1)];
            else:
                if (order == 'ascending'):
                    data = data.order_by(Lower('user__username'))[50 * numSearches : 50 * (numSearches + 1)][::-1];
                else:
                    data = data.order_by(Lower('user__username'))[50 * numSearches : 50 * (numSearches + 1)];
        else:
            if (order == 'ascending'):
                data = data.order_by(column)[50 * numSearches : 50 * (numSearches + 1)][::-1];
            else:
                data = data.order_by(column)[50 * numSearches : 50 * (numSearches + 1)];
        if (table == 'updates'):
            serializer = UpdateSerializer(data, many=True);
        elif (table == 'pledging'):
            serializer = PledgeSerializer(data, many=True);
        elif (table == 'working'):
            serializer = WorkSerializer(data, many=True);
        json = JSONRenderer().render(serializer.data);
        return HttpResponse(json, 'application/json');
    else:
        return Http404();

class PledgeHistoryView(TemplateView):
    template_name = 'job/pledge-history.html';
    
    def get(self, request, *args, **kwargs):
        pass;

class CreateView(TemplateView):
    template_name = 'job/create.html';
    form = NewJobForm;

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data(form=self.form));
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form(request.POST);
        if (form.is_valid()):
            title = form.cleaned_data['title'];
            latitude = form.cleaned_data['latitude'];
            longitude = form.cleaned_data['longitude'];
            location = form.cleaned_data['location'];
            tags = form.cleaned_data['tags'];
            comment = form.cleaned_data['comment'];
            job = Job.create(title=title, latitude=latitude, longitude=longitude, location=location);
            job.save();
            if (tags != ''):
                tagsArray = tags.split(" ");
                for tagString in tagsArray:
                    tag = get_object_or_None(Tag, tag=tagString);
                    if (tag is None):
                        tag = Tag.create(tag=tagString);
                        tag.save();
                    job.tag_set.add(tag);
            jobuser = JobUser.create(user=request.user, job=job);
            jobuser.save();
            update = Update.create(jobuser=jobuser, comment=comment);
            update.save();
            for image in request.FILES.getlist('image_set'):
                image = Image.create(update=update, image=image);
                image.save();
            return redirect('job:detail', job_random_string=job.random_string);
        return render(request, self.template_name, self.get_context_data(form=form));
        
    def get_context_data(self, **kwargs):
        context = {
            'form' : kwargs['form'],
        }
        return context