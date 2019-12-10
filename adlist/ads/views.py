
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.humanize.templatetags.humanize import naturaltime

from ads.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from ads.models import Ad, Comment, Fav
from ads.forms import CreateForm,CommentForm


from django.db.models import Q

class AdListView(OwnerListView):
    model = Ad
    template_name = "ads/ads_list.html"

    def get(self, request) :
        ad_list = Ad.objects.all()
        favorites = list()
        strval =  request.GET.get("search", False)
        if request.user.is_authenticated:
            # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
            rows = request.user.favorite_ads.values('id')
            # favorites = [2, 4, ...] using list comprehension
            favorites = [ row['id'] for row in rows ]

        if strval:
            # Simple title-only search
            # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

            # Multi-field search
            query = Q(title__contains=strval)
            query.add(Q(text__contains=strval), Q.OR)
            ad_list = Ad.objects.filter(query).select_related().order_by('-updated_at')[:10]
        else :
            # try both versions with > 4 posts and watch the queries that happen
            ad_list = Ad.objects.all().order_by('-updated_at')[:10]
            # objects = Post.objects.select_related().all().order_by('-updated_at')[:10]

        # Augment the post_list
        for obj in ad_list:
            ad_list.natural_updated = naturaltime(obj.updated_at)


        ctx = {'ad_list' : ad_list, 'favorites': favorites}
        retval = render(request, self.template_name, ctx)

        # dump_queries()
        return retval

class AdDetailView(OwnerDetailView):
    model = Ad
    template_name = "ads/ads_detail.html"

    ##From forums/views.py
    ##don't know which is form model, which is form application

    def get(self, request, pk) :
        ad = Ad.objects.get(id=pk)
        comments = Comment.objects.filter(ad=ad).order_by('-updated_at')
        comment_form = CommentForm()
        #CommentForm() is a class in forms.py
        #class CommentForm(forms.Form):
        #   comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)
        context = { 'ad' : ad, 'comments': comments, 'comment_form': comment_form }
        return render(request, self.template_name, context) #pass data to template_name(ads_detail.html) to render

class AdCreateView(OwnerCreateView):
    model = Ad
    fields = ['title', 'text', 'price']
    template_name = "ads/ads_form.html"

    # from pics/views.py
    # template = 'pics/form.html' //original code in pics/views.py
    success_url = reverse_lazy('ads:ads') #'pics:all' --> 'ads:ads'
    def get(self, request, pk=None) :
        form = CreateForm()
        ctx = { 'form': form }
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None) :
        form = CreateForm(request.POST, request.FILES or None)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        # Add owner to the model before saving
        ad = form.save(commit=False)
        ad.owner = self.request.user
        ad.save()
        return redirect(self.success_url)

class AdUpdateView(OwnerUpdateView):
    model = Ad
    fields = ['title', 'text', 'price']
    template_name = "ads/ads_form.html"

    # from  pics/views.py
    def get(self, request, pk) :
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(instance=ad)
        ctx = { 'form': form }
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None) :
        ad = get_object_or_404(Ad, id=pk, owner=self.request.user)
        form = CreateForm(request.POST, request.FILES or None, instance=ad)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        ad = form.save(commit=False)
        ad.save()

        return redirect(self.success_url)

class AdDeleteView(OwnerDeleteView):
    model = Ad
    template_name = "ads/ads_delete.html"

class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        f = get_object_or_404(Ad, id=pk)
        comment = Comment(text=request.POST['comment'], owner=request.user, ad=f)
        comment.save()
        return redirect(reverse('ads:ad_detail', args=[pk]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name = "ads/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        ad = self.object.ad
        return reverse('ads:ad_detail', args=[ad.id])

def stream_file(request, pk) :
    ad = get_object_or_404(Ad, id=pk)
    response = HttpResponse()
    response['Content-Type'] = ad.content_type
    response['Content-Length'] = len(ad.picture)
    response.write(ad.picture)
    return response

# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

@method_decorator(csrf_exempt, name='dispatch')
class AddFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Add PK",pk)
        a = get_object_or_404(Ad, id=pk)
        fav = Fav(user=request.user, ad=a)
        try:
            fav.save()  # In case of duplicate key
        except IntegrityError as e:
            pass
        return HttpResponse()

@method_decorator(csrf_exempt, name='dispatch')
class DeleteFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        print("Delete PK",pk)
        a = get_object_or_404(Ad, id=pk)
        try:
            fav = Fav.objects.get(user=request.user, ad=a).delete()
        except Fav.DoesNotExist as e:
            pass

        return HttpResponse()
